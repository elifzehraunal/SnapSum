@echo off
title SnapSum Launcher
cd /d "c:\Users\ibrah\Documents\GitHub\SnapSum"
echo ===================================================
echo           SnapSum Intelligent Summarizer
echo ===================================================
echo.
echo [1/2] Checking environment...
if exist ".venv\Scripts\activate.bat" (
    echo [2/2] Activating Virtual Environment (.venv)...
    call ".venv\Scripts\activate.bat"
) else (
    echo [2/2] Virtual environment (.venv) not found. Running with system Python...
)
echo.
echo Starting application...
python mobile/main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo ===================================================
    echo [ERROR] SnapSum encountered an error during execution.
    echo Please make sure all requirements are installed:
    echo.
    echo   pip install -r requirements.txt
    echo ===================================================
    echo.
    pause
)
