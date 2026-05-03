# FureverSafe - Dual Server Architecture Setup Guide

## Overview

FureverSafe now uses a **decoupled architecture** where:
- **AI Server** (FastAPI) runs on port **5000** - handles all AI/chatbot inference
- **Flask App** runs on port **8000** - handles web requests and calls the AI server

This separation provides:
- ✅ **Independent scaling** - run multiple Flask instances with one AI server
- ✅ **Better performance** - AI server doesn't block web requests
- ✅ **Easier debugging** - separate logs for each service
- ✅ **Production ready** - can deploy on different machines

---

## Quick Start

### Option 1: Automated Launch (Easiest)

```bash
# Run the batch file
start_servers.bat
```

This will:
1. Activate virtual environment
2. Check dependencies
3. Start AI Server (Terminal 1)
4. Start Flask App (Terminal 2)
5. Display URLs for both services

**Access the app at:** http://127.0.0.1:8000

---

### Option 2: Manual Launch (For Development)

**Terminal 1 - Start AI Server:**
```bash
# Activate virtual environment
venv\Scripts\activate

# Start AI Server on port 5000
python ai_server.py
```

**Terminal 2 - Start Flask App:**
```bash
# Activate virtual environment (in another terminal)
venv\Scripts\activate

# Start Flask App on port 8000
python app.py
```

---

### Option 3: Using Environment Variables

If you need to run servers on different ports:

**Terminal 1:**
```bash
set AI_SERVER_PORT=5000
python ai_server.py
```

**Terminal 2:**
```bash
set AI_SERVER_URL=http://127.0.0.1:5000
python app.py
```

---

## Installation & Setup

### 1. Install Dependencies

```bash
# Activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install all requirements (including FastAPI and uvicorn)
pip install -r requirements.txt
```

### 2. Optional: GGUF Model Support (Faster Inference)

For faster, more efficient inference using quantized GGUF models:

```bash
pip install llama-cpp-python
```

This enables the `test_model.py` to use the GGUF models directly (faster than LoRA).

### 3. Verify Installation

```bash
# Check AI Server dependencies
python -c "import fastapi; import uvicorn; print('✓ FastAPI ready')"

# Check AI Model dependencies
python -c "import torch; import transformers; from peft import PeftModel; print('✓ AI model ready')"

# Check Flask dependencies
python -c "import flask; import flask_sqlalchemy; print('✓ Flask ready')"
```

---

## Architecture Details

### AI Server (`ai_server.py`)

**Purpose:** Handles all AI model inference

**Endpoints:**
- `GET /health` - Check if server and model are ready
- `POST /api/chat` - Send message, get response (non-streaming)
- `POST /api/chat-stream` - Send message, get streaming response (Server-Sent Events)

**Configuration:**
```python
AI_SERVER_URL = os.environ.get("AI_SERVER_URL", "http://127.0.0.1:5000")
AI_SERVER_PORT = int(os.environ.get("AI_SERVER_PORT", 5000))
```

**Example Request:**
```bash
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I adopt a dog?", "max_tokens": 100, "temperature": 0.2}'
```

### Flask App (Modified)

**Old Way:** Flask loaded AI models directly → blocked web requests

**New Way:** Flask makes HTTP requests to AI Server → instant web response

**Modified Files:**
- `app.py` - Now imports `chatbot_client` instead of `chatbot_service`
- `chatbot_client.py` - HTTP wrapper for AI server communication
- `chatbot_service.py` - Can be archived (no longer used)

**Backward Compatible:** All Flask routes remain the same; only internal communication changed.

---

## Testing the AI Model Locally

### Test with LoRA Model (Full Precision)

```bash
cd datasets
python test_model.py
```

This uses the fine-tuned LoRA adapter on top of TinyLlama.

### Test with GGUF Model (Quantized - Faster)

```bash
# First install llama-cpp-python
pip install llama-cpp-python

cd datasets
python test_model.py
```

The script will automatically try GGUF first (if available), then fall back to LoRA.

---

## Troubleshooting

### "Cannot connect to AI server"

**Problem:** Flask can't reach AI server

**Solution:**
```bash
# 1. Check AI server is running
curl http://127.0.0.1:5000/health

# 2. Check correct port in Flask
# Make sure AI_SERVER_URL matches

# 3. Check firewall isn't blocking port 5000
```

### AI Server startup fails with "Model not loaded"

**Problem:** LoRA model files missing

**Solution:**
```bash
# Check files exist
dir datasets\fureversafe_lora_model\

# Must have: adapter_config.json and adapter_model.safetensors
```

### "llama-cpp-python installation failed"

**Problem:** Requires C++ compiler on Windows

**Solution:**
- Download and install: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Then retry: `pip install llama-cpp-python`
- Or skip GGUF support and use LoRA instead

### Flask starts but chatbot is slow

**Problem:** Might be using CPU inference

**Optimization Options:**
1. Install GGUF support for faster quantized inference
2. Install GPU support: `pip install torch[cuda]` (if you have NVIDIA GPU)
3. Increase max_tokens parameter if response is truncated

---

## Performance Comparison

| Mode | Speed | Quality | Memory | Requirements |
|------|-------|---------|--------|--------------|
| **LoRA (Full)** | Slow | Best | High (3GB) | transformers + peft |
| **GGUF (Q4_K_M)** | Fast | Good | Low (1GB) | llama-cpp-python |
| **GGUF (F16)** | Medium | Best | Medium (2GB) | llama-cpp-python |

---

## Deployment Guide

### Production Setup

For production, use a process manager like PM2 or systemd:

**create_services.bat** (Optional - for advanced setup):
```batch
@echo off
REM Start AI Server with auto-restart
start "FureverSafe AI" cmd /k "python ai_server.py & pause"

REM Start Flask with Gunicorn (production server)
start "FureverSafe Web" cmd /k "gunicorn --workers 4 --bind 0.0.0.0:8000 app:app"
```

### Docker Deployment

Both services can be containerized:

**Dockerfile.ai**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "ai_server.py"]
```

**Dockerfile.web**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV AI_SERVER_URL=http://ai-service:5000
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "app:app"]
```

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `AI_SERVER_PORT` | 5000 | AI server port |
| `AI_SERVER_URL` | http://127.0.0.1:5000 | AI server URL (Flask needs this) |
| `FLASK_ENV` | development | Flask environment |
| `FLASK_APP` | app.py | Flask app file |

---

## File Changes Summary

### New Files
- `ai_server.py` - FastAPI AI server (200 lines)
- `chatbot_client.py` - HTTP client for AI server (120 lines)
- `start_servers.bat` - Batch launcher for both servers
- `DUAL_SERVER_SETUP.md` - This file

### Modified Files
- `app.py` - Changed import from `chatbot_service` to `chatbot_client`
- `requirements.txt` - Added fastapi, uvicorn, requests
- `datasets/test_model.py` - Enhanced with GGUF support

### Archived (Still in codebase but no longer used)
- `chatbot_service.py` - Replaced by ai_server.py + chatbot_client.py

---

## Next Steps

1. ✅ Run `pip install -r requirements.txt` to install new dependencies
2. ✅ Run `start_servers.bat` to launch both servers
3. ✅ Visit http://127.0.0.1:8000 to test the web app
4. ✅ Test chatbot to confirm AI server communication works
5. ✅ (Optional) Install `llama-cpp-python` for GGUF support

---

## Support

For issues or questions:
- Check logs in both terminal windows
- Verify both servers started successfully
- Test health endpoint: `curl http://127.0.0.1:5000/health`
- Check console output for specific error messages
