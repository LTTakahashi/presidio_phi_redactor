@echo off
REM PHI Redaction Tool - Windows Launcher
REM This script sets up and launches the PHI redaction GUI

echo =======================================
echo    PHI Redaction Tool - Starting...
echo =======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from python.org
    pause
    exit /b 1
)

REM Set up virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import presidio_analyzer" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies... This may take a few minutes on first run.
    pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )

    echo Downloading spaCy language model...
    python -m spacy download en_core_web_md
    if %errorlevel% neq 0 (
        echo ERROR: Failed to download language model
        pause
        exit /b 1
    )
)

REM Launch the GUI application
echo.
echo Starting PHI Redaction Tool...
echo =======================================
python src/gui/app.py

REM Check if the application exited with an error
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Application exited with an error
    pause
)

deactivate