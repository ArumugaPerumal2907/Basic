@echo off
REM Run this file to set up and start the Sensitive Data Detection app on Windows
REM ============================================================================

echo.
echo ========================================
echo Sensitive Data Detection & Compliance
echo Assistant - Windows Setup
echo ========================================
echo.

REM Check if Python is installed
echo Checking if Python is installed...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH.
    echo.
    echo Please download and install Python from: https://www.python.org/downloads/
    echo Make sure to CHECK "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo ✅ Python found!
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo ✅ Virtual environment created!
) else (
    echo ✅ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo.
    echo ERROR: Could not activate virtual environment.
    echo Try running PowerShell as Administrator and run:
    echo   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    echo.
    pause
    exit /b 1
)
echo ✅ Virtual environment activated!
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip -q
echo ✅ pip upgraded!
echo.

REM Install requirements
echo Installing dependencies (this takes 2-5 minutes)...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies.
    echo.
    pause
    exit /b 1
)
echo.
echo ✅ All dependencies installed!
echo.

REM Run the app
echo.
echo ========================================
echo 🎉 Starting the app...
echo ========================================
echo.
echo The app will open in your browser at:
echo http://localhost:8501
echo.
echo To stop the app, press Ctrl+C in this window.
echo.
pause

streamlit run app.py
