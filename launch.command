#!/bin/bash
# PHI Redaction Tool - macOS/Linux Launcher
# This script sets up and launches the PHI redaction GUI

echo "======================================="
echo "   PHI Redaction Tool - Starting..."
echo "======================================="
echo

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or later"
    read -p "Press Enter to exit..."
    exit 1
fi

# Set up virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
python -c "import presidio_analyzer" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies... This may take a few minutes on first run."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        read -p "Press Enter to exit..."
        exit 1
    fi

    echo "Downloading spaCy language model..."
    python -m spacy download en_core_web_md
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to download language model"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Launch the GUI application
echo
echo "Starting PHI Redaction Tool..."
echo "======================================="
python src/gui/app.py

# Check if the application exited with an error
if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Application exited with an error"
    read -p "Press Enter to exit..."
fi

deactivate