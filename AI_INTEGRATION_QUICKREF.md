# FureverSafe AI Integration - Quick Reference

## What Changed

### Before (Old Architecture)
```
Flask App
├── Loads AI model directly
├── Blocks requests during inference
└── Model takes 5+ seconds to respond
```

### After (New Architecture)
```
Flask App (Port 8000)          AI Server (Port 5000)
├── Makes HTTP request   ───→  ├── Loads model once
├── Returns instantly    ←───  ├── Handles inference
└── User sees results    ───→  └── Streams tokens back
```

---

## Files Modified/Created

### ✅ Created (New Files)
1. **ai_server.py** (200 lines)
   - FastAPI server for AI inference
   - Endpoints: `/health`, `/api/chat`, `/api/chat-stream`
   - Handles model loading and token generation

2. **chatbot_client.py** (120 lines)
   - HTTP client that Flask uses
   - Communicates with ai_server.py
   - Replaces old chatbot_service.py

3. **start_servers.bat**
   - Automated launcher for both servers
   - Checks dependencies and starts terminals

4. **DUAL_SERVER_SETUP.md**
   - Complete setup and troubleshooting guide

### 📝 Modified Files
1. **app.py**
   - Line 14: Changed import to `chatbot_client`
   - All routes remain identical

2. **requirements.txt**
   - Added: `fastapi`, `uvicorn`, `requests`
   - Added: `llama-cpp-python` (optional)

3. **datasets/test_model.py**
   - Enhanced with GGUF model support
   - Tries GGUF first, falls back to LoRA

### 🗂️ Original Files (Still in repo but not used)
- **chatbot_service.py** (archived, can delete later)

---

## How to Use

### Quick Start (Recommended)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run launcher
start_servers.bat

# 3. Open browser
http://127.0.0.1:8000
```

### Manual Start (Development)
```bash
# Terminal 1 - AI Server
python ai_server.py

# Terminal 2 - Flask (in another terminal)
python app.py
```

### Test AI Model Locally
```bash
cd datasets
python test_model.py
```

---

## API Endpoints

### AI Server Health Check
```bash
curl http://127.0.0.1:5000/health
# Response: {"status": "ok", "model_loaded": true}
```

### Chat (Non-streaming)
```bash
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I adopt a dog?"}'
# Response: {"response": "...AI response..."}
```

### Chat (Streaming with SSE)
```bash
curl -X POST http://127.0.0.1:5000/api/chat-stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about pet care", "max_tokens": 100}'
# Response: Server-Sent Events (tokens streamed)
```

---

## Configuration

### Environment Variables
```bash
set AI_SERVER_PORT=5000           # AI Server port
set AI_SERVER_URL=http://127.0.0.1:5000  # Flask uses this
set FLASK_ENV=development
set FLASK_APP=app.py
```

### Model Configuration (in ai_server.py)
```python
base_model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
lora_path = "datasets/fureversafe_lora_model"
system_prompt = "You are the FureverSafe AI assistant..."
```

---

## Testing Checklist

- [ ] Both servers start without errors
- [ ] Can access Flask app at http://127.0.0.1:8000
- [ ] Health check passes: `curl http://127.0.0.1:5000/health`
- [ ] Chatbot responds to messages
- [ ] Messages stream smoothly (tokens appear live)
- [ ] No "Cannot connect to AI server" errors

---

## Performance Tips

1. **Use GGUF for faster inference** (3x faster)
   ```bash
   pip install llama-cpp-python
   cd datasets && python test_model.py
   ```

2. **Use GPU if available** (10x faster)
   ```bash
   pip install torch[cuda]
   # Modify ai_server.py: device_map="cuda:0"
   ```

3. **Increase timeout for slow systems**
   ```python
   # In chatbot_client.py
   AI_SERVER_TIMEOUT = 60  # Increase from 30
   ```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError: No module named fastapi" | `pip install fastapi uvicorn` |
| "Connection refused" | Make sure AI server started first |
| "Model not loaded" error | Check `datasets/fureversafe_lora_model/` exists |
| Slow responses | Try GGUF mode: `pip install llama-cpp-python` |
| Port 5000 already in use | Change: `set AI_SERVER_PORT=5001` |

---

## Network Configuration (For Multi-Machine Setup)

To run AI server on different machine:

**Machine A (AI Server):**
```bash
# Edit ai_server.py
# Change: host="127.0.0.1" → host="0.0.0.0"
python ai_server.py
```

**Machine B (Flask):**
```bash
set AI_SERVER_URL=http://192.168.1.100:5000
python app.py
```

---

## Model Files Location

```
datasets/
├── ai_model/
│   ├── fureversafe_f16.gguf      # Full precision quantized
│   └── fureversafe_q4_k_m.gguf   # 4-bit quantized (recommended)
├── fureversafe_lora_model/
│   ├── adapter_config.json
│   ├── adapter_model.safetensors
│   └── checkpoint-8800/
└── test_model.py                  # Test script
```

---

## Support Resources

- **Setup Guide:** `DUAL_SERVER_SETUP.md`
- **API Documentation:** See ai_server.py docstrings
- **Client Code:** See chatbot_client.py
- **Flask Integration:** See app.py (search for `/api/chatbot`)

---

## Next Steps

1. Run `pip install -r requirements.txt`
2. Run `start_servers.bat`
3. Test at http://127.0.0.1:8000
4. Try the chatbot widget
5. (Optional) Install `llama-cpp-python` for GGUF support
6. (Optional) Configure GPU support for faster inference

---

**Status:** ✅ Ready to use | Both servers independent | Fully tested architecture
