@echo off
REM FureverSafe - Manual Setup Instructions
REM Shows commands to run if the automated scripts don't work

cls
echo.
echo ============================================================
echo FureverSafe - Manual Setup Guide
echo ============================================================
echo.
echo STEP 1: Install Dependencies
echo ============================================================
echo.
echo   python -m venv venv
echo   venv\Scripts\activate
echo   pip install -r requirements.txt
echo.
echo ============================================================
echo STEP 2: Start the Server
echo ============================================================
echo.
echo   cd "%cd%"
echo   venv\Scripts\activate
echo   python app.py
echo.
echo   The AI model (GGUF) loads automatically on startup.
echo   If the GGUF model is missing, it falls back to LoRA.
echo.
echo ============================================================
echo STEP 3: Access the Application
echo ============================================================
echo.
echo   Web App:  http://127.0.0.1:8000
echo.
echo ============================================================
echo OPTIONAL: Run AI Server Standalone (FastAPI)
echo ============================================================
echo.
echo   If you want to run the AI model as a separate service:
echo.
echo   Terminal 1:  python ai_server.py     (port 5000)
echo   Terminal 2:  python app.py           (port 8000)
echo.
echo ============================================================
echo TROUBLESHOOTING
echo ============================================================
echo.
echo Q: "Module not found errors"
echo A: Run: pip install -r requirements.txt
echo.
echo Q: "GGUF model not found"
echo A: Check that datasets\ai_model\fureversafe_q4_k_m.gguf exists
echo.
echo Q: "llama-cpp-python fails to install"
echo A: Try: pip install llama-cpp-python --no-cache-dir
echo    On some systems you may need Visual C++ Build Tools installed.
echo.
echo ============================================================
echo.

pause
