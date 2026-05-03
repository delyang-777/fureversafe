# FureverSafe - Batch File Setup Guide

## 🚀 Quick Start (One Command)

```bash
run.bat
```

That's it! This single command will:
1. Check if virtual environment exists
2. Run full setup if it's the first time
3. Start both AI and Flask servers
4. Open browser to http://127.0.0.1:8000

---

## 📋 Batch Files Included

### 1. **run.bat** ⭐ (MAIN ENTRY POINT)
**Use this to start everything!**

What it does:
- ✅ Checks if venv exists
- ✅ Runs setup.bat automatically on first run
- ✅ Launches start_servers.bat to run both servers
- ✅ Activates virtual environment

**When to use:** Every time you want to run FureverSafe

```bash
run.bat
```

---

### 2. **setup.bat** (Installation)
**Use this to install/reinstall dependencies**

What it does:
- ✅ Creates virtual environment if it doesn't exist
- ✅ Installs main requirements.txt
- ✅ Installs dataset_requirements.txt
- ✅ Verifies all dependencies
- ✅ Checks for model files
- ✅ Shows next steps

**When to use:** 
- First time setup
- After updating requirements
- To reinstall dependencies

```bash
setup.bat
```

**Installation steps:**
1. Creates venv
2. Activates venv
3. Runs `pip install -r requirements.txt`
4. Runs `pip install -r datasets/dataset_requirements.txt`
5. Verifies installations
6. Checks model files

**Time:** 5-10 minutes (depending on internet)

---

### 3. **start_servers.bat** (Launch Servers)
**Use this to start servers after setup is done**

What it does:
- ✅ Activates virtual environment
- ✅ Checks all dependencies are installed
- ✅ Starts AI Server (port 5000) in new terminal
- ✅ Starts Flask App (port 8000) in new terminal
- ✅ Opens browser to Flask app
- ✅ Shows both server URLs

**When to use:** 
- Daily development
- After setup.bat completes

```bash
start_servers.bat
```

**Important:** Creates TWO terminals:
- Terminal 1: AI Server output
- Terminal 2: Flask app output (stays open)

---

## 🎯 Usage Scenarios

### Scenario 1: First Time Setup (Easiest)

```bash
# Just run this one command
run.bat

# It will:
# 1. Create venv
# 2. Install all dependencies
# 3. Start both servers
# 4. Open browser
```

**Time:** First run takes 5-10 minutes, subsequent runs take 3-5 seconds

---

### Scenario 2: Daily Development

```bash
# After first setup, just use:
run.bat

# Or directly:
start_servers.bat
```

---

### Scenario 3: Reinstall Dependencies

```bash
# Delete venv and run setup fresh:
rmdir /s /q venv
setup.bat

# Then:
start_servers.bat
```

---

### Scenario 4: Troubleshooting

```bash
# Verify all dependencies installed:
setup.bat

# Check if servers start:
start_servers.bat

# Manual terminal 1 (AI Server):
venv\Scripts\activate
python ai_server.py

# Manual terminal 2 (Flask):
venv\Scripts\activate
python app.py
```

---

## 📊 File Structure

```
fureversafe1/
├── run.bat                          ⭐ START HERE (first time)
├── setup.bat                        📦 Install dependencies
├── start_servers.bat                ▶️ Launch servers
├── START_SERVERS_MANUAL.bat         📖 Manual instructions
├── requirements.txt                 📋 Main dependencies
├── datasets/
│   ├── dataset_requirements.txt      📋 AI model dependencies
│   ├── ai_model/
│   │   └── *.gguf                  🤖 GGUF models
│   ├── fureversafe_lora_model/
│   │   └── *.safetensors           🤖 LoRA adapter
│   └── test_model.py               🧪 Test script
├── ai_server.py                     🖥️ AI server
├── chatbot_client.py                💬 Flask ↔ AI bridge
└── app.py                           🌐 Flask web app
```

---

## ⚙️ What Gets Installed

### By setup.bat

**Main Requirements (requirements.txt):**
- Flask 2.3.2 - Web framework
- FastAPI 0.109+ - AI server framework
- Uvicorn - ASGI server
- SQLAlchemy - Database ORM
- Requests - HTTP client
- And 10+ more packages

**Dataset Requirements (dataset_requirements.txt):**
- torch 2.5+ - Deep learning
- transformers 4.48+ - LLM library
- peft 0.15+ - LoRA adapter
- accelerate - GPU optimization
- safetensors - Model serialization

**Total Install Size:** ~3-5 GB (mainly PyTorch)
**Installation Time:** 5-10 minutes first time

---

## 🔧 Virtual Environment Management

### What is venv?
Virtual environment (venv) isolates Python packages so they don't conflict with system Python.

### Created by: setup.bat
Location: `fenv/` folder

### Activated by:
- setup.bat (automatic)
- start_servers.bat (automatic)
- ai_server.py launch command
- app.py launch command

### To activate manually:
```bash
venv\Scripts\activate
```

### To deactivate:
```bash
deactivate
```

---

## ✅ Verification Checklist

After run setup.bat completes, verify:

```bash
# Check Python in venv
venv\Scripts\python --version
# Should show Python 3.x

# Check Flask installed
venv\Scripts\python -c "import flask; print(flask.__version__)"
# Should show 2.3.2

# Check FastAPI installed
venv\Scripts\python -c "import fastapi; print(fastapi.__version__)"
# Should show 0.109+

# Check model libraries
venv\Scripts\python -c "import torch, transformers; print('✓')"
# Should print: ✓

# Check model files exist
dir datasets\fureversafe_lora_model\
# Should show: adapter_config.json, adapter_model.safetensors
```

---

## 🐛 Troubleshooting

### Problem: "Python not found"
```bash
# Solution: Install Python from https://www.python.org/
# Make sure to check "Add Python to PATH" during installation
```

### Problem: "venv creation failed"
```bash
# Solution: Try manual creation
python -m venv venv
setup.bat
```

### Problem: "pip install is very slow"
```bash
# Solution: This is normal first time (downloading PyTorch, etc.)
# First run: 5-10 minutes
# Subsequent runs: <1 minute
```

### Problem: "Permission denied" in venv\Scripts
```bash
# Solution: Run Command Prompt as Administrator
# Right-click cmd.exe → Run as administrator
# Then run: run.bat
```

### Problem: "Port 5000/8000 already in use"
```bash
# Check what's using it:
netstat -ano | find "5000"

# Or change port in start_servers.bat:
set AI_SERVER_PORT=5001
```

### Problem: Servers won't start after setup
```bash
# Solution: Run setup again to verify installation
setup.bat

# Then try servers:
start_servers.bat
```

---

## 📝 Environment Variables (Automatic)

The batch files automatically set:

```bash
FLASK_APP=app.py
FLASK_ENV=development
AI_SERVER_PORT=5000
AI_SERVER_URL=http://127.0.0.1:5000
PYTHONPATH=%SCRIPT_DIR%
```

To use different values, edit the batch files or set manually before running:

```bash
set AI_SERVER_PORT=5001
run.bat
```

---

## 🔄 How Batch Files Work Together

```
┌─────────────┐
│   run.bat   │ ⭐ START HERE
└──────┬──────┘
       │
       ├─ Check: Does venv exist?
       │
       ├─ NO  ─→ Call setup.bat ─────────┐
       │         (Install everything)    │
       │                                 │
       ├─ YES ──────────────────────────┤
       │                                 │
       └─────────────────────────────────┤
                                         │
                      Call start_servers.bat
                      │
         ┌────────────┼────────────┐
         │            │            │
         │            ├─ Activate venv
         │            │
         │            ├─ Terminal 1: AI Server
         │            │  $ python ai_server.py
         │            │
         │            ├─ Terminal 2: Flask
         │            │  $ python app.py
         │            │
         │            └─ Open browser
         │               http://127.0.0.1:8000
```

---

## 🎓 Key Concepts

### First Run vs. Subsequent Runs

**First Run (run.bat):**
```
1. Detect venv doesn't exist
2. Run setup.bat (5-10 min)
   - Create venv
   - pip install all packages
   - Verify installations
3. Run start_servers.bat (3-5 sec)
   - Activate venv
   - Start servers
   - Open browser
Total Time: ~10 minutes
```

**Subsequent Runs (run.bat or start_servers.bat):**
```
1. venv already exists
2. Skip setup
3. Run start_servers.bat (3-5 sec)
   - Activate venv
   - Start servers
   - Open browser
Total Time: ~5 seconds
```

### Virtual Environment Activation

Each process needs venv activated:

```bash
# AI Server terminal activation
cd /d "%SCRIPT_DIR%" && call venv\Scripts\activate.bat && python ai_server.py

# Flask terminal activation
cd /d "%SCRIPT_DIR%" && call "%SCRIPT_DIR%venv\Scripts\activate.bat"
```

The batch files do this automatically!

---

## 💾 Cleanup & Reset

### Keep everything installed (fastest):
```bash
run.bat
```

### Clean and reinstall:
```bash
# Delete venv
rmdir /s /q venv

# Run setup fresh
setup.bat

# Then start
start_servers.bat
```

### Clean everything (if needed):
```bash
# Delete virtual environment
rmdir /s /q venv

# Delete pycache
cd /d your_project_directory
for /d /r . %d in (__pycache__) do @if exist "%d" rmdir /s /q "%d"

# Then fresh start
run.bat
```

---

## 📞 Support

If batch files don't work:

1. **Manual Setup:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r datasets/dataset_requirements.txt
   ```

2. **Manual Start:**
   ```bash
   # Terminal 1
   venv\Scripts\activate && python ai_server.py

   # Terminal 2
   venv\Scripts\activate && python app.py
   ```

3. **Check Status:**
   ```bash
   curl http://127.0.0.1:5000/health
   ```

---

## ✅ Summary

| Task | Command | Time |
|------|---------|------|
| First Time Setup | `run.bat` | 10 min |
| Daily Start | `run.bat` or `start_servers.bat` | 5 sec |
| Reinstall | `rmdir /s /q venv && run.bat` | 10 min |
| Manual Setup | `setup.bat` | 10 min |
| Just Launch | `start_servers.bat` | 5 sec |

**Recommended:** Use `run.bat` for everything - it handles all cases!

---

**Status: ✅ READY | All batch files configured and tested**

Just run: `run.bat`
