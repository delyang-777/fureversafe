@echo off
REM FureverSafe - Server Launcher
REM Starts the Flask app with the AI model loaded in-process (GGUF or LoRA)

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
if exist "%SCRIPT_DIR%datasets\ai_model\fureversafe_q4_k_m.gguf" (
    echo [OK] GGUF model found - will use fast quantized inference
) else (
    echo [INFO] GGUF model not found - will try LoRA fallback
)

echo.
echo ============================================================
echo Starting FureverSafe on http://127.0.0.1:8000
echo ============================================================
echo.

set FLASK_APP=app.py
set FLASK_ENV=development

cd /d "%SCRIPT_DIR%"

python app.py
