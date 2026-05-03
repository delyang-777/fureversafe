"""
FurEverSafe - LoRA to GGUF Conversion Script (Memory-Efficient)
================================================================
Merges TinyLlama + LoRA adapter → saves full model → converts to GGUF.

Uses a low-memory path: loads the model with low_cpu_mem_usage=True and
avoids holding two full copies in RAM at once.

Run once:  python convert_to_gguf.py
Output:    datasets/fureversafe.gguf
"""

import os
import sys
import subprocess
import urllib.request

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
LORA_PATH     = os.path.join(BASE_DIR, "datasets", "fureversafe_lora_model")
MERGED_PATH   = os.path.join(BASE_DIR, "datasets", "fureversafe_merged_model")
GGUF_OUTPUT   = os.path.join(BASE_DIR, "datasets", "fureversafe.gguf")
CONVERT_SCRIPT = os.path.join(BASE_DIR, "datasets", "convert_hf_to_gguf.py")
BASE_MODEL    = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"


def step1_merge_lora():
    print("\n" + "=" * 60)
    print("STEP 1/3 — Merging LoRA adapter into base model")
    print("=" * 60)

    if os.path.exists(MERGED_PATH) and os.path.isfile(os.path.join(MERGED_PATH, "config.json")):
        print(f"  ✓ Merged model already exists at: {MERGED_PATH}")
        print("  Skipping merge step.")
        return

    import gc
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel

    print(f"  Loading base model (low memory mode): {BASE_MODEL}")
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        dtype=torch.float32,
        low_cpu_mem_usage=True,
    )

    print("  Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    print(f"  Attaching LoRA adapter from: {LORA_PATH}")
    model = PeftModel.from_pretrained(base_model, LORA_PATH)

    print("  Merging weights (merge_and_unload)...")
    merged = model.merge_and_unload()

    # Free the PEFT model object immediately to save RAM before saving
    del model
    gc.collect()

    print(f"  Saving merged model to: {MERGED_PATH}")
    os.makedirs(MERGED_PATH, exist_ok=True)
    merged.save_pretrained(MERGED_PATH, safe_serialization=True)
    tokenizer.save_pretrained(MERGED_PATH)

    del merged
    gc.collect()

    print("  ✓ Merge complete!")


def step2_get_convert_script():
    """Download llama.cpp's official HF→GGUF conversion script if not present."""
    if os.path.exists(CONVERT_SCRIPT):
        print(f"  ✓ Convert script already exists: {CONVERT_SCRIPT}")
        return

    url = "https://raw.githubusercontent.com/ggerganov/llama.cpp/master/convert_hf_to_gguf.py"
    print(f"  Downloading convert_hf_to_gguf.py from llama.cpp GitHub...")
    urllib.request.urlretrieve(url, CONVERT_SCRIPT)
    print(f"  ✓ Saved to: {CONVERT_SCRIPT}")

    # Also ensure gguf package is installed
    print("  Installing gguf package...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "gguf", "sentencepiece", "-q"],
        check=False
    )


def step3_convert_to_gguf():
    print("\n" + "=" * 60)
    print("STEP 2/3 — Converting merged model to GGUF (f16)")
    print("=" * 60)

    if os.path.exists(GGUF_OUTPUT):
        print(f"  ✓ GGUF file already exists: {GGUF_OUTPUT}")
        print("  Skipping conversion step.")
        return

    step2_get_convert_script()

    cmd = [
        sys.executable, CONVERT_SCRIPT,
        MERGED_PATH,
        "--outfile", GGUF_OUTPUT,
        "--outtype", "f16",
    ]
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError("GGUF conversion failed — check output above.")
    print(f"  ✓ GGUF written: {GGUF_OUTPUT}")


def step4_verify():
    print("\n" + "=" * 60)
    print("STEP 3/3 — Verifying GGUF file")
    print("=" * 60)

    if not os.path.exists(GGUF_OUTPUT):
        print("  ✗ GGUF file not found! Conversion may have failed.")
        return False

    size_mb = os.path.getsize(GGUF_OUTPUT) / (1024 * 1024)
    print(f"  ✓ GGUF exists:  {GGUF_OUTPUT}")
    print(f"  ✓ Size:         {size_mb:.1f} MB")

    try:
        from llama_cpp import Llama
        print("  Testing llama-cpp-python load...")
        llm = Llama(model_path=GGUF_OUTPUT, n_ctx=256, n_threads=4, verbose=False)
        out = llm("Hello", max_tokens=10, echo=False)
        snippet = out["choices"][0]["text"].strip()[:60]
        print(f"  ✓ Test inference OK: '{snippet}'")
        del llm
    except ImportError:
        print("  ⚠ llama-cpp-python not importable in this env — install it in the venv.")
    except Exception as e:
        print(f"  ⚠ Inference test skipped: {e}")

    print("\n" + "=" * 60)
    print("✅ GGUF model ready!")
    print(f"   {GGUF_OUTPUT}")
    print("=" * 60)
    return True


if __name__ == "__main__":
    step1_merge_lora()
    step3_convert_to_gguf()
    step4_verify()
