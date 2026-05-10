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
echo Step 3: Upgrading pip
echo ============================================================
echo.
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded

echo.
echo ============================================================
echo Step 4: Installing Core Dependencies
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
echo Step 5: Installing AI Model Engine (llama-cpp-python)
echo ============================================================
echo.

REM Check if already installed - skip if so
python -c "import llama_cpp" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] llama-cpp-python already installed - skipping
    goto :llama_done
)

REM Detect Python version for wheel selection
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
    set PYMAJ=%%a
    set PYMIN=%%b
)
echo Detected Python %PYVER%

echo.
echo [1/3] Trying official prebuilt CPU wheels index...
pip install llama-cpp-python --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --quiet
python -c "import llama_cpp" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] llama-cpp-python installed via CPU wheel index
    goto :llama_done
)

echo [2/3] Trying PyPI binary wheel...
pip install "llama-cpp-python>=0.3.1,<0.4.0" --prefer-binary --only-binary :all: --quiet
python -c "import llama_cpp" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] llama-cpp-python installed via PyPI binary
    goto :llama_done
)

echo [3/3] Trying latest version with binary preference...
pip install llama-cpp-python --prefer-binary --quiet
python -c "import llama_cpp" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] llama-cpp-python installed
    goto :llama_done
)

echo.
echo ============================================================
echo [WARNING] llama-cpp-python could not be auto-installed
echo ============================================================
echo.
echo The chatbot will run in RULE-BASED mode (no AI text generation).
echo All other app features (adoption, shelter, users) work normally.
echo.
echo === MANUAL FIX (pick one) ===
echo.
echo Option A - Install Visual Studio Build Tools, then re-run setup.bat:
echo   https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo   (Select: "Desktop development with C++" workload)
echo.
echo Option B - Download a prebuilt .whl for your Python %PYMAJ%.%PYMIN% from:
echo   https://github.com/abetlen/llama-cpp-python/releases
echo   Then run: venv\Scripts\pip install path\to\the.whl
echo.

:llama_done

echo.
echo ============================================================
echo Step 6: Final Verification
echo ============================================================
echo.

python -c "import flask; print('[OK] Flask')" 2>nul || echo [FAIL] Flask not found
python -c "import fastapi; print('[OK] FastAPI')" 2>nul || echo [FAIL] FastAPI not found
python -c "import sqlalchemy; print('[OK] SQLAlchemy')" 2>nul || echo [FAIL] SQLAlchemy not found
python -c "import llama_cpp; print('[OK] llama-cpp-python (AI engine ready)')" 2>nul || echo [WARNING] llama-cpp-python not available - chatbot in rule-based mode

echo.
echo ============================================================
echo Step 7: Checking Model Files
echo ============================================================
echo.

if exist "%SCRIPT_DIR%datasets\ai_model\fureversafe-q8.gguf" (
    echo [OK] Retrained Q8 model found (primary)
) else if exist "%SCRIPT_DIR%datasets\ai_model\fureversafe_q4_k_m.gguf" (
    echo [OK] Q4_K_M model found (production)
) else if exist "%SCRIPT_DIR%datasets\ai_model\fureversafe-q4_k_m-v2.gguf" (
    echo [OK] Q4_K_M v2 model found
) else (
    echo [WARNING] No GGUF model found in datasets\ai_model\
    echo The chatbot will use rule-based responses until the model file is placed there.
    echo See CHATBOT_GUIDE.md for instructions.
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
