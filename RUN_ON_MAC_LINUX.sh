#!/bin/bash

# Run this file to set up and start the Sensitive Data Detection app
# On macOS/Linux, run: bash RUN_ON_MAC_LINUX.sh

echo ""
echo "========================================"
echo "Sensitive Data Detection & Compliance"
echo "Assistant - macOS/Linux Setup"
echo "========================================"
echo ""

# Check if Python is installed
echo "Checking if Python is installed..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "ERROR: Python 3 is not installed."
    echo ""
    echo "Install it with:"
    echo "  macOS (Homebrew): brew install python3"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-venv"
    echo "  Fedora: sudo dnf install python3"
    echo ""
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION found!"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created!"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Could not activate virtual environment."
    echo ""
    exit 1
fi
echo "✅ Virtual environment activated!"
echo ""

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip -q
echo "✅ pip upgraded!"
echo ""

# Install requirements
echo "Installing dependencies (this takes 2-5 minutes)..."
echo ""
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install dependencies."
    echo ""
    exit 1
fi
echo ""
echo "✅ All dependencies installed!"
echo ""

# Run the app
echo ""
echo "========================================"
echo "🎉 Starting the app..."
echo "========================================"
echo ""
echo "The app will open in your browser at:"
echo "http://localhost:8501"
echo ""
echo "To stop the app, press Ctrl+C"
echo ""

streamlit run app.py
