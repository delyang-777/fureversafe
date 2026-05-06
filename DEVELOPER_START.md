# FureverSafe Developer Start Guide

This guide is for developers who already have the repository cloned and want the fastest safe workflow for updating and running the project on Windows PowerShell.

## Daily Workflow

### 1. Open the project

```powershell
cd C:\Users\fosta\OneDrive\Desktop\commision\fureversafe
```

### 2. Pull the latest code from `main`

```powershell
git checkout main
git pull origin main
```

### 3. Run setup

This refreshes the local virtual environment and installs any missing dependencies.

```powershell
.\setup.bat
```

### 4. Start the full system

This starts both required services:
- Flask web app on `http://127.0.0.1:8000`
- AI server on `http://127.0.0.1:5000`

```powershell
.\start_servers.bat
```

### 5. Open the app

Go to:

```text
http://127.0.0.1:8000
```

## First-Time Notes

### AI model files are not stored in Git

The local chatbot model is intentionally not committed to the repository.

Expected primary model path:

```text
datasets\ai_model\fureversafe-q4_k_m-v2.gguf
```

If the model is missing, the app can still start, but the chatbot service will show as offline until a valid GGUF model or fallback LoRA assets are available locally.

### Required terminals

`start_servers.bat` opens two separate terminal windows:
- one for `ai_server.py`
- one for `app.py`

Keep both running while testing the chatbot.

## Quick Verification

After startup:

1. Open `http://127.0.0.1:8000`
2. Confirm the homepage loads
3. Open the chatbot widget
4. Confirm the status changes to `AI service online`

You can also verify the AI server directly:

```powershell
curl http://127.0.0.1:5000/health
```

Expected result:

```json
{"status":"ok","model_loaded":true,"backend":"gguf"}
```

## Common Commands

### Activate the virtual environment manually

```powershell
.\venv\Scripts\activate
```

### Run the Flask app only

```powershell
python app.py
```

### Run the AI server only

```powershell
python ai_server.py
```

## Troubleshooting

### Chatbot says `AI service offline`

Check that:
- `.\start_servers.bat` was used instead of only `python app.py`
- the AI server window is still open
- the local GGUF model exists at `datasets\ai_model\fureversafe-q4_k_m-v2.gguf`

### Setup fails on `llama-cpp-python`

Run:

```powershell
.\setup.bat
```

The setup script is already configured to prefer binary wheels and keep the known-good `llama-cpp-python==0.3.1` dependency.

### Port already in use

Close older terminals that are still running Flask or the AI server, then run:

```powershell
.\start_servers.bat
```

## Recommended Update Sequence

For most developers, this is the only sequence you need:

```powershell
git checkout main
git pull origin main
.\setup.bat
.\start_servers.bat
```
