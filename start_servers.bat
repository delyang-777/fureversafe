@echo off
REM FureverSafe - Dual Server Launcher
REM Starts the standalone AI service and the Flask app in separate terminals

echo.
echo ============================================================
echo FureverSafe - Dual Server Launcher
echo ============================================================
echo.

set SCRIPT_DIR=%~dp0
set AI_SERVER_PORT=5000
set AI_SERVER_URL=http://127.0.0.1:%AI_SERVER_PORT%

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
python -c "import flask, fastapi, requests" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Missing dependencies! Run setup.bat first.
    pause
    exit /b 1
)

echo [OK] Dependencies found
echo.

REM Check model availability
if exist "%SCRIPT_DIR%datasets\ai_model\fureversafe-q4_k_m-v2.gguf" (
    echo [OK] GGUF v2 model found - will use the official local AI model
) else if exist "%SCRIPT_DIR%datasets\ai_model\fureversafe_q4_k_m.gguf" (
    echo [OK] Legacy GGUF model found - AI service will use fallback quantized inference
) else (
    echo [INFO] No GGUF model found - AI service will try the LoRA fallback
)

echo.
echo Starting AI service on %AI_SERVER_URL% ...
start "FureverSafe AI Server" cmd /k "cd /d ""%SCRIPT_DIR%"" && call venv\Scripts\activate.bat && set AI_SERVER_PORT=%AI_SERVER_PORT% && python ai_server.py"

echo Waiting for AI service startup...
timeout /t 5 /nobreak >nul

echo Starting Flask app on http://127.0.0.1:8000 ...
start "FureverSafe Flask App" cmd /k "cd /d ""%SCRIPT_DIR%"" && call venv\Scripts\activate.bat && set FLASK_APP=app.py && set FLASK_ENV=development && set AI_SERVER_URL=%AI_SERVER_URL% && python app.py"

echo.
echo ============================================================
echo Services launched
echo   Flask App : http://127.0.0.1:8000
echo   AI Server : %AI_SERVER_URL%
echo ============================================================
echo.
