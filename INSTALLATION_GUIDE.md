# 🐾 FureverSafe - Complete Installation & Setup Guide

**Last Updated:** May 3, 2026  
**Status:** ✅ Ready to Use  
**Estimated Setup Time:** 5-10 minutes (first time only)

---

## 📖 TABLE OF CONTENTS

1. [Quick Start (30 seconds)](#-quick-start)
2. [Prerequisites](#-prerequisites)
3. [Detailed Setup](#-detailed-setup)
4. [Batch Files Explained](#-batch-files)
5. [Testing & Verification](#-testing)
6. [Troubleshooting](#-troubleshooting)
7. [Architecture](#-architecture)

---

## 🚀 QUICK START

### All-in-One Command

```bash
run.bat
```

That's it! This will:
1. ✅ Create virtual environment (first time only)
2. ✅ Install all dependencies
3. ✅ Start AI Server (port 5000)
4. ✅ Start Flask App (port 8000)
5. ✅ Open browser to http://127.0.0.1:8000

**First Run:** Takes ~10 minutes (downloading PyTorch)  
**Subsequent Runs:** Takes ~5 seconds

---

## ⚙️ Prerequisites

Before you start, make sure you have:

### 1. **Python 3.8+**
```bash
# Check if installed
python --version

# If not installed, download from:
# https://www.python.org/
# ⚠️ IMPORTANT: Check "Add Python to PATH" during installation
```

### 2. **Git** (Optional but recommended)
```bash
git --version
# Download from: https://git-scm.com/
```

### 3. **Administrator Access** (For virtual environment creation)
- Run Command Prompt as Administrator
- Or disable UAC

---

## 🔧 DETAILED SETUP

### Step 1: Navigate to Project Directory

```bash
# Open Command Prompt and navigate to project folder
cd C:\Users\YourName\OneDrive\Desktop\commision\fureversafe1
```

### Step 2: Run Setup (Choose One)

#### Option A: Fully Automatic (Recommended)
```bash
run.bat
# This handles everything automatically
```

#### Option B: Manual Installation
```bash
# Run setup
setup.bat

# Then start servers
start_servers.bat
```

#### Option C: Step-by-Step
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate

# 3. Install main requirements
pip install -r requirements.txt

# 4. Install AI model requirements
pip install -r datasets\dataset_requirements.txt

# 5. Start AI server (Terminal 1)
python ai_server.py

# 6. Start Flask app (Terminal 2)
python app.py

# 7. Open browser
start http://127.0.0.1:8000
```

---

## 📋 BATCH FILES EXPLAINED

### 1. **run.bat** ⭐ (Main Entry Point)
**Purpose:** One-command setup and launch

**What it does:**
- Checks if venv exists
- Runs setup.bat if first time
- Launches start_servers.bat
- Handles everything automatically

**When to use:** Always use this first

```bash
run.bat
```

---

### 2. **setup.bat** (Installation)
**Purpose:** Install all dependencies

**What it does:**
- Creates virtual environment
- Activates it
- Installs requirements.txt
- Installs dataset_requirements.txt
- Verifies all packages
- Checks model files

**When to use:** First time or to reinstall

```bash
setup.bat
```

**Time:** 5-10 minutes first run

---

### 3. **start_servers.bat** (Launch Servers)
**Purpose:** Start both AI and Flask servers

**What it does:**
- Activates virtual environment
- Checks dependencies
- Starts AI Server (Terminal 1)
- Starts Flask App (Terminal 2)
- Opens browser to localhost

**When to use:** After setup.bat completes

```bash
start_servers.bat
```

**Result:** Two terminals open:
- Terminal 1: AI Server logs
- Terminal 2: Flask app logs (stays open)

---

### 4. **verify.bat** (Testing)
**Purpose:** Verify all components are installed

**What it does:**
- Checks Python installation
- Checks virtual environment
- Lists all installed packages
- Verifies model files
- Tests imports

**When to use:** To troubleshoot issues

```bash
verify.bat
```

---

## ✅ TESTING & VERIFICATION

### Quick Test After Setup

```bash
# 1. Check AI server health
curl http://127.0.0.1:5000/health
# Expected: {"status":"ok","model_loaded":true}

# 2. Open browser
http://127.0.0.1:8000

# 3. Test chatbot widget
# Find chatbot in bottom corner and send a message

# 4. Should get response within 10-15 seconds
```

### Detailed Verification

```bash
# Run verification script
verify.bat

# Should show [OK] for all items:
# - Python installed
# - Flask installed
# - FastAPI installed
# - PyTorch installed
# - Model files present
```

### Test Model Locally

```bash
# Go to datasets folder
cd datasets

# Run test script
python test_model.py

# This opens interactive chatbot
# Type messages, press Ctrl+C to exit
```

---

## 🐛 TROUBLESHOOTING

### Issue: "Python not found"
```bash
# Solution:
# 1. Install Python from https://www.python.org/
# 2. During installation: CHECK "Add Python to PATH"
# 3. Restart Command Prompt
# 4. Try again: python --version
```

### Issue: "pip: command not found"
```bash
# Solution: Use python -m pip instead
python -m pip install -r requirements.txt
```

### Issue: "venv creation failed"
```bash
# Solution: Try with python -m
python -m venv venv

# If still fails:
# - Run as Administrator
# - Check disk space (needs ~500MB)
# - Run: python -m venv venv --clear
```

### Issue: "Cannot install packages (slow download)"
```bash
# This is normal! PyTorch is large (~2GB)
# First run: 5-10 minutes
# Subsequent runs: <1 minute

# To speed up:
pip install --upgrade pip
pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

### Issue: "Permission denied" errors
```bash
# Solution: Run Command Prompt as Administrator
# Right-click cmd.exe → Run as administrator
# Then run: run.bat
```

### Issue: "Port 5000 already in use"
```bash
# Check what's using it:
netstat -ano | find "5000"

# Kill the process:
taskkill /PID <PID_NUMBER> /F

# Or change port in start_servers.bat:
set AI_SERVER_PORT=5001
```

### Issue: "Cannot connect to AI server" after startup
```bash
# Verify AI server started:
curl http://127.0.0.1:5000/health

# Check both terminals are still running
# Restart everything: run.bat
```

### Issue: Model files not found
```bash
# Check model files exist:
dir datasets\fureversafe_lora_model\

# Should show:
# adapter_config.json
# adapter_model.safetensors

# Check directory structure with:
tree datasets /F
```

### Issue: "Module not found" errors
```bash
# Re-run setup:
setup.bat

# Or manually reinstall:
venv\Scripts\activate
pip install -r requirements.txt
pip install -r datasets\dataset_requirements.txt
```

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────┐
│            Browser (User Access)                │
│          http://127.0.0.1:8000                  │
└──────────────────┬────────────────────────────┘
                   │
                   │ Web Request
                   ▼
        ┌──────────────────────────┐
        │  Flask Web App (8000)    │
        │  - Web Pages             │
        │  - API Routes            │
        │  - Sessions              │
        └──────────┬───────────────┘
                   │
                   │ HTTP POST /api/chat
                   │ {message, max_tokens}
                   ▼
        ┌──────────────────────────┐
        │  AI Server (5000)        │
        │  - Model Inference       │
        │  - Token Generation      │
        │  - Streaming Response    │
        └──────────┬───────────────┘
                   │
                   │ Uses
                   ▼
        ┌──────────────────────────┐
        │  AI Models               │
        │  - Base: TinyLlama 1.1B  │
        │  - Adapter: LoRA         │
        │  - Alternative: GGUF     │
        └──────────────────────────┘
```

---

## 📊 INSTALLATION BREAKDOWN

### What Gets Installed

**Main Packages (requirements.txt):**
- Flask 2.3.2 - Web framework
- FastAPI 0.109+ - API framework
- Uvicorn - ASGI server
- SQLAlchemy 3.0+ - Database
- WTForms 3.0+ - Forms
- Markdown 3.4+ - Content processing
- Requests 2.31+ - HTTP client
- (+ 10 more)

**AI Model Packages (dataset_requirements.txt):**
- PyTorch 2.5+ - Deep learning (largest: ~2GB)
- Transformers 4.48+ - LLM library
- PEFT 0.15+ - LoRA adapters
- Accelerate 1.2+ - GPU optimization
- Safetensors 0.4+ - Model format

**Optional for Speed:**
- llama-cpp-python - GGUF inference

### Installation Time
- First run: 5-10 minutes (downloading PyTorch)
- Subsequent runs: <1 minute (cached)
- With fast internet: 5-7 minutes
- With slow internet: 10-20 minutes

### Disk Space Required
- Virtual environment: ~500MB
- PyTorch cache: ~2GB
- Model files: ~2GB
- Total: ~5GB minimum

---

## 🎯 QUICK REFERENCE

| Task | Command | Time |
|------|---------|------|
| First Time Setup | `run.bat` | 10 min |
| Daily Start | `run.bat` or `start_servers.bat` | 5 sec |
| Verify Installation | `verify.bat` | 30 sec |
| Test Model Locally | `cd datasets && python test_model.py` | 5 sec |
| Reinstall Everything | Delete venv, then `run.bat` | 10 min |
| Check AI Server | `curl http://127.0.0.1:5000/health` | 1 sec |

---

## 📚 ADDITIONAL RESOURCES

Inside the project:

- **BATCH_FILES_GUIDE.md** - Detailed batch file documentation
- **DUAL_SERVER_SETUP.md** - Architecture and deployment guide
- **AI_INTEGRATION_QUICKREF.md** - API reference
- **QUICK_START.md** - 30-second quick start
- **INTEGRATION_CHECKLIST.md** - Step-by-step verification

---

## ✨ FEATURES INCLUDED

After setup, you get:

✅ **Web Interface**
- Pet adoption listings
- Lost & found reports
- Educational resources
- User dashboard

✅ **AI Chatbot**
- Real-time responses
- Streaming tokens
- Pet care advice
- Adoption guidance

✅ **Admin Panel**
- Dashboard with statistics
- Incident management
- User approval system
- Resource creation

✅ **Dual Server Architecture**
- Independent scaling
- Better performance
- Production-ready

---

## 🎓 HOW IT WORKS

### First Time Running run.bat

```
run.bat
  ├─ Check: venv exists? NO
  │  └─ Call setup.bat
  │     ├─ Create venv
  │     ├─ pip install -r requirements.txt
  │     ├─ pip install -r datasets/dataset_requirements.txt
  │     └─ Verify all packages
  │
  └─ Call start_servers.bat
     ├─ Terminal 1: python ai_server.py
     ├─ Terminal 2: python app.py
     └─ Open browser to http://127.0.0.1:8000
```

### Subsequent Runs

```
run.bat
  ├─ Check: venv exists? YES
  ├─ Skip setup (already installed)
  │
  └─ Call start_servers.bat
     ├─ Terminal 1: python ai_server.py
     ├─ Terminal 2: python app.py
     └─ Open browser to http://127.0.0.1:8000
```

---

## 📞 SUPPORT

If you encounter issues:

1. **Read the logs** - Both terminals show detailed error messages
2. **Run verify.bat** - Check if all components installed correctly
3. **Check documentation** - See BATCH_FILES_GUIDE.md
4. **Manual setup** - Follow Option C in Detailed Setup section
5. **Internet connection** - Ensure stable for package downloads

---

## ✅ SETUP CHECKLIST

Before considering setup complete:

- [ ] run.bat executed successfully
- [ ] No errors in either terminal
- [ ] Browser opened to http://127.0.0.1:8000
- [ ] Flask page loaded (shows FureverSafe)
- [ ] Chatbot widget appears (usually bottom-right)
- [ ] Can send message to chatbot
- [ ] Chatbot responds within 15 seconds

If all checked: **✅ Setup is complete!**

---

## 🚀 NEXT STEPS

After successful setup:

1. **Explore the Web Interface**
   - Visit http://127.0.0.1:8000
   - Create an account (or use admin:admin123)
   - Try the chatbot

2. **Test Different Features**
   - Browse adoption listings
   - Submit lost & found reports
   - Read educational content
   - Try admin dashboard

3. **Optional: Faster Inference**
   ```bash
   # For 3x faster AI responses:
   pip install llama-cpp-python
   ```

4. **Optional: GPU Support**
   ```bash
   # If you have NVIDIA GPU:
   pip install torch[cuda]
   ```

---

## 📝 NOTES

- Virtual environment must be activated before running Python scripts
- Both servers must be running for chatbot to work
- First request to AI server takes longer (model loading)
- Subsequent requests are faster
- Models are cached on first download (500MB+)

---

**Status: ✅ Ready to Use**

**Next Command:** `run.bat`

Enjoy FureverSafe! 🐾
