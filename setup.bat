@echo off
REM FureverSafe Complete Setup Script
REM Installs virtual environment and all dependencies

setlocal enabledelayedexpansion

cls
echo.
echo ============================================================
echo FureverSafe - Complete System Setup
echo ============================================================
echo.

set SCRIPT_DIR=%~dp0

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ============================================================
echo Step 1: Checking Virtual Environment
echo ============================================================
echo.

if exist "%SCRIPT_DIR%venv" (
    echo [OK] Virtual environment already exists
) else (
    echo Creating virtual environment...
    python -m venv "%SCRIPT_DIR%venv"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo.
echo ============================================================
echo Step 2: Activating Virtual Environment
echo ============================================================
echo.

call "%SCRIPT_DIR%venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment activated

echo.
echo ============================================================
echo Step 3: Installing Dependencies
echo ============================================================
echo.

echo Installing from requirements.txt...
echo Using existing compatible packages when already installed.
echo Preferring binary wheels to avoid Windows long-path build failures.
pip install --prefer-binary -r "%SCRIPT_DIR%requirements.txt"

if %errorlevel% neq 0 (
    echo ERROR: Failed to install requirements
    echo.
    echo Common Windows fix:
    echo   1. Enable Windows Long Paths
    echo   2. Re-run setup.bat
    echo.
    echo Project note:
    echo   This setup now prefers binary wheels and avoids forced upgrades.
    echo   If llama-cpp-python is already installed, it should be kept as-is.
    pause
    exit /b 1
)

echo [OK] Requirements installed

echo.
echo ============================================================
echo Step 4: Verifying Installation
echo ============================================================
echo.

python -c "import flask; import llama_cpp; print('[OK] Core dependencies verified')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Could not verify all imports
    echo Some dependencies may not be installed correctly
    echo Try running this setup script again
) else (
    echo [OK] All core dependencies verified
)

echo.
echo ============================================================
echo Step 5: Checking Model Files
echo ============================================================
echo.

if exist "%SCRIPT_DIR%datasets\ai_model\fureversafe-q4_k_m-v2.gguf" (
    echo [OK] GGUF v2 model found (primary - fast inference)
) else if exist "%SCRIPT_DIR%datasets\ai_model\fureversafe_q4_k_m.gguf" (
    echo [OK] Legacy GGUF model found (fallback quantized inference)
) else (
    echo [WARNING] GGUF model not found at datasets\ai_model\fureversafe-q4_k_m-v2.gguf
    echo The chatbot will try LoRA fallback, which is slower.
)

if exist "%SCRIPT_DIR%datasets\fureversafe_lora_model\adapter_config.json" (
    echo [OK] LoRA model found (fallback)
) else (
    echo [WARNING] LoRA model not found at datasets\fureversafe_lora_model\
)

echo.
echo ============================================================
echo SETUP COMPLETE
echo ============================================================
echo.
echo Next Steps:
echo   1. Run: start_servers.bat
echo   2. Open: http://127.0.0.1:8000
echo   3. Test the chatbot!
echo.
echo ============================================================
echo.

pause
