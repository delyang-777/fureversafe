"""
FureverSafe AI Server - Standalone FastAPI inference server
Loads the GGUF quantized model (primary) or LoRA adapter (fallback).
Run with: python ai_server.py
"""

import os
import sys
import warnings
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import logging
from config import Config

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FureverSafe AI Server", version="2.0")

_llm = None
_backend = None
_lora_model = None
_lora_tokenizer = None
_loaded_model_path = None

SYSTEM_PROMPT = Config.AI_SYSTEM_PROMPT + (
    " Keep answers practical and easy to scan. Use short paragraphs or simple bullet points when that helps."
)


class ChatRequest(BaseModel):
    message: str
    max_tokens: int = Config.AI_MAX_NEW_TOKENS
    temperature: float = Config.AI_TEMPERATURE


def _resolve_model_candidates(base_dir: str) -> list[str]:
    """Build a deduplicated list of preferred GGUF model paths."""
    configured_path = Config.GGUF_MODEL_PATH
    if not os.path.isabs(configured_path):
        configured_path = os.path.join(base_dir, configured_path)

    candidates = [
        configured_path,
        os.path.join(base_dir, "datasets", "ai_model", "fureversafe-q4_k_m-v2.gguf"),
        os.path.join(base_dir, "datasets", "ai_model", "fureversafe_q4_k_m.gguf"),
        os.path.join(base_dir, "datasets", "ai_model", "fureversafe-q8.gguf"),
        os.path.join(base_dir, "datasets", "ai_model", "fureversafe_f16.gguf"),
    ]

    deduped = []
    seen = set()
    for path in candidates:
        normalized = os.path.normcase(os.path.abspath(path))
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(path)
    return deduped


def load_model():
    """Load GGUF model (primary) or LoRA (fallback)."""
    global _llm, _backend, _lora_model, _lora_tokenizer, _loaded_model_path

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Priority 1: configured GGUF model, then known local fallbacks
    gguf_paths = _resolve_model_candidates(base_dir)

    for gguf_path in gguf_paths:
        if os.path.isfile(gguf_path):
            try:
                from llama_cpp import Llama
                logger.info("Loading GGUF model: %s", os.path.basename(gguf_path))
                _llm = Llama(
                    model_path=gguf_path,
                    n_gpu_layers=Config.GGUF_N_GPU_LAYERS,
                    n_ctx=Config.GGUF_N_CTX,
                    verbose=False,
                )
                _backend = "gguf"
                _loaded_model_path = gguf_path
                logger.info("AI backend: GGUF loaded successfully (%s)", os.path.basename(gguf_path))
                return True
            except Exception as e:
                logger.warning("GGUF load failed (%s): %s", os.path.basename(gguf_path), e)
                continue

    # Fallback to LoRA
    lora_path = Config.LORA_MODEL_PATH
    if not os.path.isabs(lora_path):
        lora_path = os.path.join(base_dir, lora_path)
    if os.path.isdir(lora_path):
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            from peft import PeftModel

            base_model_name = Config.LORA_BASE_MODEL
            logger.info("Loading LoRA fallback: %s + %s", base_model_name, lora_path)
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name, torch_dtype=torch.float32, device_map="cpu"
            )
            _lora_tokenizer = AutoTokenizer.from_pretrained(base_model_name)
            _lora_model = PeftModel.from_pretrained(base_model, lora_path)
            _lora_model.eval()
            _backend = "lora"
            _loaded_model_path = lora_path
            logger.info("AI backend: LoRA loaded successfully")
            return True
        except Exception as e:
            logger.error("LoRA load failed: %s", e)

    logger.error("No AI model could be loaded")
    return False


def generate_response(user_message: str, max_tokens: int = 200, temperature: float = 0.2) -> str:
    prompt = f"System: {SYSTEM_PROMPT}\nUser: {user_message}\nAssistant:"

    if _backend == "gguf":
        output = _llm(
            prompt, max_tokens=max_tokens, temperature=temperature,
            top_p=0.9, repeat_penalty=1.15, stop=["User:", "\nUser"],
        )
        reply = output["choices"][0]["text"].strip()
    else:
        import torch
        inputs = _lora_tokenizer(prompt, return_tensors="pt").to(_lora_model.device)
        with torch.no_grad():
            outputs = _lora_model.generate(
                **inputs, max_new_tokens=max_tokens, temperature=temperature,
                top_p=0.9, repetition_penalty=1.15, do_sample=True,
                pad_token_id=_lora_tokenizer.eos_token_id,
            )
        full = _lora_tokenizer.decode(outputs[0], skip_special_tokens=True)
        reply = full.split("Assistant:")[-1].strip()

    return reply or "I'm sorry, I didn't quite understand that. Could you rephrase your question about pet care or adoption?"


def generate_response_stream(user_message: str, max_tokens: int = 200, temperature: float = 0.2):
    prompt = f"System: {SYSTEM_PROMPT}\nUser: {user_message}\nAssistant:"

    if _backend == "gguf":
        for chunk in _llm(
            prompt, max_tokens=max_tokens, temperature=temperature,
            top_p=0.9, repeat_penalty=1.15, stop=["User:", "\nUser"],
            stream=True,
        ):
            token = chunk["choices"][0]["text"]
            if token:
                yield token
    else:
        import torch
        from transformers import TextIteratorStreamer
        import threading

        inputs = _lora_tokenizer(prompt, return_tensors="pt").to(_lora_model.device)
        streamer = TextIteratorStreamer(_lora_tokenizer, skip_prompt=True, skip_special_tokens=True)
        gen_kwargs = dict(
            **inputs, max_new_tokens=max_tokens, temperature=temperature,
            top_p=0.9, repetition_penalty=1.15, do_sample=True,
            pad_token_id=_lora_tokenizer.eos_token_id, streamer=streamer,
        )

        def run():
            with torch.no_grad():
                _lora_model.generate(**gen_kwargs)

        thread = threading.Thread(target=run)
        thread.start()
        for token_text in streamer:
            if token_text:
                yield token_text
        thread.join()


@app.on_event("startup")
async def startup_event():
    success = load_model()
    if not success:
        logger.warning("AI model failed to load, server will run in degraded mode")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_loaded": _backend is not None,
        "backend": _backend,
        "model_path": _loaded_model_path,
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if _backend is None:
        raise HTTPException(status_code=503, detail="AI model is not loaded.")
    try:
        response = generate_response(request.message, request.max_tokens, request.temperature)
        return {"response": response}
    except Exception as e:
        logger.error("Chat error: %s", e)
        raise HTTPException(status_code=500, detail="Failed to generate response")


@app.post("/api/chat-stream")
async def chat_stream(request: ChatRequest):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if _backend is None:
        raise HTTPException(status_code=503, detail="AI model is not loaded.")

    async def event_generator():
        try:
            yield f"data: {json.dumps({'thinking': True})}\n\n"
            for token in generate_response_stream(request.message, request.max_tokens, request.temperature):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            logger.error("Stream error: %s", e)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("AI_SERVER_PORT", 5000))
    logger.info("Starting FureverSafe AI Server on port %d...", port)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
