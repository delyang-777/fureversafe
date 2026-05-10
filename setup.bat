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

echo.
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
echo Step 3: Installing Core Dependencies
echo ============================================================
echo.

echo Installing from requirements.txt...
pip install --prefer-binary -r "%SCRIPT_DIR%requirements.txt"

if %errorlevel% neq 0 (
    echo ERROR: Failed to install core requirements.
    echo Please check your Python version (3.8+ required) and internet connection.
    pause
    exit /b 1
)

echo [OK] Core requirements installed

echo.
echo ============================================================
echo Step 4: Installing AI Model Engine (llama-cpp-python)
echo ============================================================
echo.
echo This package requires no C++ compiler - using prebuilt CPU wheels...
echo.

REM Try the official prebuilt CPU wheel index first
pip install llama-cpp-python --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --quiet
if %errorlevel% equ 0 (
    echo [OK] llama-cpp-python installed via prebuilt CPU wheel
    goto :llama_done
)

echo [INFO] Prebuilt wheel not found for your Python version. Trying generic binary...
pip install "llama-cpp-python>=0.3.1" --prefer-binary --quiet
if %errorlevel% equ 0 (
    echo [OK] llama-cpp-python installed via binary fallback
    goto :llama_done
)

echo.
echo [WARNING] llama-cpp-python could not be installed automatically.
echo The chatbot will run in RULE-BASED mode (no AI generation).
echo All other features of the app will work normally.
echo.
echo To install it manually later (requires Visual Studio Build Tools):
echo   1. Download Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo      (Select "Desktop development with C++" workload)
echo   2. Restart this setup.bat
echo.
echo OR install a pre-built wheel directly from GitHub releases:
echo   https://github.com/abetlen/llama-cpp-python/releases

:llama_done

echo.
echo ============================================================
echo Step 5: Verifying Installation
echo ============================================================
echo.

python -c "import flask; print('[OK] Flask verified')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Flask import failed - check requirements install
)

python -c "import llama_cpp; print('[OK] llama-cpp-python verified')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] llama-cpp-python not available - chatbot runs in rule-based mode
) else (
    echo [OK] llama-cpp-python verified
)

echo.
echo ============================================================
echo Step 6: Checking Model Files
echo ============================================================
echo.

if exist "%SCRIPT_DIR%datasets\ai_model\fureversafe-q8.gguf" (
    echo [OK] Retrained Q8 GGUF model found (primary)
) else if exist "%SCRIPT_DIR%datasets\ai_model\fureversafe_q4_k_m.gguf" (
    echo [OK] Q4_K_M GGUF model found (production model)
) else (
    echo [WARNING] No GGUF model found in datasets\ai_model\
    echo The chatbot will run in rule-based intent mode until the model is placed there.
    echo See CHATBOT_GUIDE.md for instructions.
)

if exist "%SCRIPT_DIR%datasets\fureversafe_lora_model\adapter_config.json" (
    echo [OK] LoRA adapter found (fallback)
) else (
    echo [INFO] No LoRA adapter found - this is OK if GGUF model is present
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
