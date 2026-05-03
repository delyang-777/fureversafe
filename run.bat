@echo off
REM FureverSafe - Master Launcher
REM Runs setup if needed, then starts the server

setlocal enabledelayedexpansion

cls
echo.
echo ============================================================
echo        FureverSafe AI System - Master Launcher
echo ============================================================
echo.

set SCRIPT_DIR=%~dp0

REM Check if this is first run (venv doesn't exist)
if not exist "%SCRIPT_DIR%venv" (
    echo First time setup detected!
    echo.
    echo Running setup.bat to install all dependencies...
    echo This may take 5-10 minutes depending on your internet speed.
    echo.
    call "%SCRIPT_DIR%setup.bat"
    if %errorlevel% neq 0 (
        echo ERROR: Setup failed!
        pause
        exit /b 1
    )
)

echo.
echo Starting server...
call "%SCRIPT_DIR%start_servers.bat"
