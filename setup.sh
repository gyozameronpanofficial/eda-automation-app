#!/bin/bash
echo "========================================"
echo "EDA Automation App Setup Script"
echo "========================================"
echo

# Check if Python is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed."
    echo "Please install Python 3.8 or higher:"
    echo "- macOS: brew install python3"
    echo "- Or download from: https://www.python.org/downloads/"
    exit 1
fi

echo "Python is installed successfully."
python3 --version
echo

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies."
    exit 1
fi

echo
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo
echo "Virtual environment has been created and dependencies installed."
echo
echo "To start the application:"
echo "    ./run.sh"
echo
echo "To stop the application:"
echo "    Press Ctrl+C"
echo