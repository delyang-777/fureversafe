@echo off
REM FureverSafe - Server Launcher
REM Starts the Flask app with the AI model loaded in-process (GGUF or LoRA)

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo FureverSafe - Server Launcher
echo ============================================================
echo.

set SCRIPT_DIR=%~dp0

REM Check if venv exists
if not exist "%SCRIPT_DIR%venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run setup.bat first:
    echo   1. Run: setup.bat
    echo   2. Wait for installation to complete
    echo   3. Then run: start_servers.bat
    echo.
    pause
    exit /b 1
)

echo Activating virtual environment...
call "%SCRIPT_DIR%venv\Scripts\activate.bat"

echo Checking dependencies...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Missing dependencies! Run setup.bat first.
    pause
    exit /b 1
)

echo [OK] Dependencies found
echo.

REM Check model availability
set "MODEL_STATUS=none"
if exist "%SCRIPT_DIR%datasets\ai_model\fureversafe_q4_k_m.gguf" set "MODEL_STATUS=gguf"
if "!MODEL_STATUS!"=="none" if exist "%SCRIPT_DIR%datasets\fureversafe_lora_model\adapter_config.json" set "MODEL_STATUS=lora"

if "!MODEL_STATUS!"=="gguf" echo [OK] GGUF model found - will use fast quantized inference
if "!MODEL_STATUS!"=="lora" echo [INFO] No GGUF model - will use LoRA fallback (slower startup)
if "!MODEL_STATUS!"=="none" echo [WARNING] No AI model found - chatbot will be unavailable

echo.
echo ============================================================
echo Starting FureverSafe on http://127.0.0.1:8000
echo ============================================================
echo.

set FLASK_APP=app.py
set FLASK_ENV=development

cd /d "%SCRIPT_DIR%"

REM Open browser after a short delay
start /b cmd /c "timeout /t 4 /nobreak >nul && start http://127.0.0.1:8000"

python app.py
