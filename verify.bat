@echo off
REM FureverSafe - Verification Script
REM Tests all components before running

setlocal enabledelayedexpansion

cls
echo.
echo ============================================================
echo FureverSafe - System Verification
echo ============================================================
echo.

set SCRIPT_DIR=%~dp0

echo Step 1: Checking Python Installation
echo =============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

python --version
echo [OK] Python is installed
echo.

echo Step 2: Checking Virtual Environment
echo =============================================
echo.

if exist "%SCRIPT_DIR%venv" (
    echo [OK] Virtual environment exists
) else (
    echo [MISSING] Virtual environment not found - run setup.bat
)
echo.

echo Step 3: Activating Virtual Environment
echo =============================================
echo.

if exist "%SCRIPT_DIR%venv\Scripts\activate.bat" (
    call "%SCRIPT_DIR%venv\Scripts\activate.bat"
    echo [OK] Virtual environment activated
) else (
    echo [SKIP] Cannot activate venv
)
echo.

echo Step 4: Checking Python Packages
echo =============================================
echo.

REM Check Flask
python -c "import flask" 2>nul
if %errorlevel% equ 0 (
    echo [OK] Flask
) else (
    echo [MISSING] Flask
)

REM Check llama-cpp-python (GGUF support)
python -c "from llama_cpp import Llama" 2>nul
if %errorlevel% equ 0 (
    echo [OK] llama-cpp-python (GGUF inference)
) else (
    echo [MISSING] llama-cpp-python - run setup.bat
)

REM Check PyTorch (LoRA fallback)
python -c "import torch" 2>nul
if %errorlevel% equ 0 (
    echo [OK] PyTorch (LoRA fallback)
) else (
    echo [INFO] PyTorch not installed (only needed for LoRA fallback)
)

REM Check Transformers (LoRA fallback)
python -c "import transformers" 2>nul
if %errorlevel% equ 0 (
    echo [OK] Transformers (LoRA fallback)
) else (
    echo [INFO] Transformers not installed (only needed for LoRA fallback)
)

REM Check Requests
python -c "import requests" 2>nul
if %errorlevel% equ 0 (
    echo [OK] Requests
) else (
    echo [MISSING] Requests
)

echo.
echo Step 5: Checking Model Files
echo =============================================
echo.

if exist "%SCRIPT_DIR%datasets\ai_model\fureversafe_q4_k_m.gguf" (
    echo [OK] GGUF model: fureversafe_q4_k_m.gguf (primary)
) else (
    echo [MISSING] GGUF model not found at datasets\ai_model\fureversafe_q4_k_m.gguf
)

if exist "%SCRIPT_DIR%datasets\fureversafe_lora_model\adapter_config.json" (
    echo [OK] LoRA adapter config (fallback)
) else (
    echo [MISSING] LoRA adapter_config.json
)

if exist "%SCRIPT_DIR%datasets\fureversafe_lora_model\adapter_model.safetensors" (
    echo [OK] LoRA adapter weights (fallback)
) else (
    echo [MISSING] LoRA adapter_model.safetensors
)

echo.
echo Step 6: Checking File Structure
echo =============================================
echo.

if exist "%SCRIPT_DIR%app.py" (echo [OK] app.py) else (echo [ERROR] app.py not found)
if exist "%SCRIPT_DIR%chatbot_service.py" (echo [OK] chatbot_service.py) else (echo [ERROR] chatbot_service.py not found)
if exist "%SCRIPT_DIR%config.py" (echo [OK] config.py) else (echo [ERROR] config.py not found)
if exist "%SCRIPT_DIR%requirements.txt" (echo [OK] requirements.txt) else (echo [ERROR] requirements.txt not found)

echo.
echo ============================================================
echo Verification Summary
echo ============================================================
echo.
echo If everything shows [OK]:
echo   Run: start_servers.bat
echo   Open: http://127.0.0.1:8000
echo.
echo If anything shows [MISSING] or [ERROR]:
echo   Run: setup.bat first
echo.

pause
