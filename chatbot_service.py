"""
FureverSafe Chatbot Service
Loads the GGUF quantized model (primary) or LoRA adapter (fallback)
and serves inference directly inside the Flask process.
"""

import os
import logging
import threading

logger = logging.getLogger(__name__)

_llm = None
_config = None
_backend = None  # "gguf" or "lora"

# LoRA-specific globals (only used when GGUF is unavailable)
_lora_model = None
_lora_tokenizer = None


def _load_gguf(model_path, n_gpu_layers, n_ctx):
    """Load GGUF model via llama-cpp-python."""
    from llama_cpp import Llama

    logger.info("Loading GGUF model: %s", os.path.basename(model_path))
    llm = Llama(
        model_path=model_path,
        n_gpu_layers=n_gpu_layers,
        n_ctx=n_ctx,
        verbose=False,
    )
    logger.info("GGUF model loaded successfully")
    return llm


def _load_lora(base_model_name, lora_path):
    """Fallback: load LoRA adapter on TinyLlama via transformers + peft."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel

    logger.info("Loading base model: %s", base_model_name)
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name, torch_dtype=torch.float32, device_map="cpu"
    )
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)

    logger.info("Attaching LoRA adapter from: %s", lora_path)
    model = PeftModel.from_pretrained(base_model, lora_path)
    model.eval()
    logger.info("LoRA model loaded successfully")
    return model, tokenizer


def init_ai_model(app):
    """Initialize the AI model. Tries GGUF first, falls back to LoRA."""
    global _llm, _config, _backend, _lora_model, _lora_tokenizer
    _config = app.config

    gguf_path = _config.get("GGUF_MODEL_PATH", "")
    if not os.path.isabs(gguf_path):
        gguf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), gguf_path)

    # Try GGUF first
    if os.path.isfile(gguf_path):
        try:
            _llm = _load_gguf(
                gguf_path,
                n_gpu_layers=_config.get("GGUF_N_GPU_LAYERS", -1),
                n_ctx=_config.get("GGUF_N_CTX", 512),
            )
            _backend = "gguf"
            logger.info("AI backend: GGUF (%s)", os.path.basename(gguf_path))
            return
        except Exception as e:
            logger.warning("GGUF load failed, trying LoRA fallback: %s", e)

    # Fallback to LoRA
    lora_path = _config.get("LORA_MODEL_PATH", "")
    if not os.path.isabs(lora_path):
        lora_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), lora_path)

    if os.path.isdir(lora_path):
        try:
            base_model = _config.get("LORA_BASE_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
            _lora_model, _lora_tokenizer = _load_lora(base_model, lora_path)
            _backend = "lora"
            logger.info("AI backend: LoRA")
            return
        except Exception as e:
            logger.error("LoRA load failed: %s", e)

    logger.error("No AI model could be loaded. Chatbot will be unavailable.")


def process_chatbot_message(message: str) -> str:
    """Generate a complete response for the given message."""
    if not message or not message.strip():
        return "Please ask me something!"

    if _backend is None:
        return "The AI model is not loaded. Please contact the administrator."

    message = message.strip()
    system_prompt = _config.get("AI_SYSTEM_PROMPT", "You are the FureverSafe AI assistant.")
    max_tokens = _config.get("AI_MAX_NEW_TOKENS", 200)
    temperature = _config.get("AI_TEMPERATURE", 0.2)

    if _backend == "gguf":
        return _generate_gguf(system_prompt, message, max_tokens, temperature)
    return _generate_lora(system_prompt, message, max_tokens, temperature)


def process_chatbot_message_stream(message: str):
    """Yield tokens as they are generated."""
    if not message or not message.strip():
        yield "Please ask me something!"
        return

    if _backend is None:
        yield "The AI model is not loaded. Please contact the administrator."
        return

    message = message.strip()
    system_prompt = _config.get("AI_SYSTEM_PROMPT", "You are the FureverSafe AI assistant.")
    max_tokens = _config.get("AI_MAX_NEW_TOKENS", 200)
    temperature = _config.get("AI_TEMPERATURE", 0.2)

    if _backend == "gguf":
        yield from _stream_gguf(system_prompt, message, max_tokens, temperature)
    else:
        yield from _stream_lora(system_prompt, message, max_tokens, temperature)


# ── GGUF inference ──────────────────────────────────────────────────────────

def _generate_gguf(system_prompt, user_message, max_tokens, temperature):
    prompt = f"System: {system_prompt}\nUser: {user_message}\nAssistant:"
    output = _llm(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=0.9,
        repeat_penalty=1.15,
        stop=["User:", "\nUser"],
    )
    reply = output["choices"][0]["text"].strip()
    return reply or "I'm sorry, I didn't quite understand that. Could you rephrase your question about pet care or adoption?"


def _stream_gguf(system_prompt, user_message, max_tokens, temperature):
    prompt = f"System: {system_prompt}\nUser: {user_message}\nAssistant:"
    for chunk in _llm(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=0.9,
        repeat_penalty=1.15,
        stop=["User:", "\nUser"],
        stream=True,
    ):
        token = chunk["choices"][0]["text"]
        if token:
            yield token


# ── LoRA inference ──────────────────────────────────────────────────────────

def _generate_lora(system_prompt, user_message, max_tokens, temperature):
    import torch

    prompt = f"System: {system_prompt}\nUser: {user_message}\nAssistant:"
    inputs = _lora_tokenizer(prompt, return_tensors="pt").to(_lora_model.device)

    with torch.no_grad():
        outputs = _lora_model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            repetition_penalty=1.15,
            do_sample=True,
            pad_token_id=_lora_tokenizer.eos_token_id,
        )

    full = _lora_tokenizer.decode(outputs[0], skip_special_tokens=True)
    reply = full.split("Assistant:")[-1].strip()
    return reply or "I'm sorry, I didn't quite understand that. Could you rephrase your question about pet care or adoption?"


def _stream_lora(system_prompt, user_message, max_tokens, temperature):
    import torch
    from transformers import TextIteratorStreamer

    prompt = f"System: {system_prompt}\nUser: {user_message}\nAssistant:"
    inputs = _lora_tokenizer(prompt, return_tensors="pt").to(_lora_model.device)

    streamer = TextIteratorStreamer(_lora_tokenizer, skip_prompt=True, skip_special_tokens=True)
    gen_kwargs = dict(
        **inputs,
        max_new_tokens=max_tokens,
        temperature=temperature,
        top_p=0.9,
        repetition_penalty=1.15,
        do_sample=True,
        pad_token_id=_lora_tokenizer.eos_token_id,
        streamer=streamer,
    )

    thread = threading.Thread(target=_lora_generate_thread, args=(gen_kwargs,))
    thread.start()

    for token_text in streamer:
        if token_text:
            yield token_text

    thread.join()


def _lora_generate_thread(kwargs):
    import torch
    with torch.no_grad():
        _lora_model.generate(**kwargs)
