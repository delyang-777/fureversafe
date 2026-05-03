# FurEverSafe AI Model - Setup Instructions

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 2 GB free disk space (for model files and dependencies)

## Quick Start

### 1. Set Up Hugging Face Access Token

The LoRA fallback downloads the TinyLlama base model from Hugging Face.
To avoid rate limits and speed up downloads, create an access token:

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Set the name to anything (e.g. "fureversafe")
4. Set the type to **Read**
5. Click "Generate"
6. Copy the token

Then log in from your terminal:

```bash
pip install huggingface_hub
huggingface-cli login
```

Paste your token when prompted. This is optional if you are only using
the GGUF model, but required if you need the LoRA fallback.

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

**Standard install (GGUF inference only):**

```bash
pip install -r requirements.txt
```

This installs:
- `llama-cpp-python` - GGUF model inference (primary backend, fast)
- `flask` and web dependencies - Web application server
- `fastapi` + `uvicorn` - Optional standalone AI server

**Note:** `llama-cpp-python` compiles C++ code during installation.
On Windows, you may need Microsoft Visual C++ Build Tools:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

If the install fails, try a prebuilt wheel:
```bash
pip install llama-cpp-python --prefer-binary
```

**Optional: LoRA fallback (only if GGUF is unavailable):**

```bash
pip install -r requirements-lora.txt
```

This adds `torch`, `transformers`, `peft`, `accelerate`, and
`safetensors` (~3-5 GB download). Only install this if the GGUF model
file is missing or you need to work with the LoRA adapter directly.
The LoRA fallback also requires the TinyLlama base model, which is
downloaded automatically from Hugging Face on first run (~2 GB).
Having a Hugging Face access token (Step 1) speeds this up.

### 4. Verify Model Files

Make sure these files exist:

```
datasets/
  ai_model/
    fureversafe_q4_k_m.gguf    <-- Primary model (4-bit quantized)
    fureversafe_f16.gguf        <-- Full precision model (optional)
  fureversafe_lora_model/
    adapter_config.json         <-- LoRA config (fallback)
    adapter_model.safetensors   <-- LoRA weights (fallback)
```

### 5. Run the Application

**Windows (recommended):**

After setup is complete, just double-click `run.bat` or open Command
Prompt in the project folder and type:

```
.\run.bat
```

That's it. `run.bat` handles everything — activates the virtual
environment, checks dependencies, loads the AI model, and starts the
server. The app opens automatically at http://127.0.0.1:8000.

On first run, `run.bat` will also run `setup.bat` automatically if the
virtual environment doesn't exist yet.

**Manual start (any OS):**

```bash
# Activate the virtual environment first
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Start the server
python app.py
```

Then open http://127.0.0.1:8000 in your browser.

The GGUF model loads automatically on startup (~2 seconds). If the GGUF
file is missing or `llama-cpp-python` is not installed, it falls back to
the LoRA adapter (slower startup, requires ~4 GB RAM for the base
TinyLlama model download from Hugging Face).

### Windows Batch Files

| File | Purpose |
|---|---|
| `run.bat` | Main entry point — runs setup if needed, then starts the server |
| `setup.bat` | Installs dependencies and verifies model files |
| `start_servers.bat` | Starts the web server (skips setup) |
| `verify.bat` | Checks that everything is configured correctly |

For day-to-day use, just run `.\run.bat` every time.

## Configuration

Environment variables (set in `.env` or system environment):

| Variable | Default | Description |
|---|---|---|
| `GGUF_MODEL_PATH` | `datasets/ai_model/fureversafe_q4_k_m.gguf` | Path to GGUF model |
| `GGUF_N_GPU_LAYERS` | `-1` | GPU layers (-1 = all, 0 = CPU only) |
| `GGUF_N_CTX` | `512` | Context window size |
| `AI_MAX_NEW_TOKENS` | `200` | Max tokens per response |
| `AI_TEMPERATURE` | `0.2` | Generation temperature |

## Troubleshooting

**"No AI model could be loaded"**
- Check that `datasets/ai_model/fureversafe_q4_k_m.gguf` exists
- Run `pip install llama-cpp-python` if not installed

**Slow startup (30+ seconds)**
- You are likely using the LoRA fallback. Install `llama-cpp-python`
  and ensure the GGUF file is present for fast startup (~2 seconds).

**"llama-cpp-python fails to install"**
- On Windows: install Visual C++ Build Tools first
- Try: `pip install llama-cpp-python --prefer-binary`
- On macOS with Apple Silicon: `CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python`

**LoRA fallback is slow to download TinyLlama**
- Set up a Hugging Face access token (see Step 1) to avoid rate limits
- The base model (~2 GB) only downloads once and is cached locally

**"401 Unauthorized" when downloading from Hugging Face**
- Run `huggingface-cli login` and paste a valid Read token
- Get a token at https://huggingface.co/settings/tokens
