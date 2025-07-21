#!/bin/bash

echo "Installing Visual Novel Node Editor Dependencies..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python 3.8+ from https://python.org"
        exit 1
    else
        PYTHON_CMD=python
    fi
else
    PYTHON_CMD=python3
fi

# Show Python version
echo "Using Python version:"
$PYTHON_CMD --version
echo

# Upgrade pip to latest version
echo "Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip
echo

# Install requirements
echo "Installing project dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt
echo

# Verify installation
echo "Verifying installation..."

if $PYTHON_CMD -c "import PySide6" 2>/dev/null; then
    echo "✓ PySide6 ready"
else
    echo "✗ PySide6 installation failed"
fi

if $PYTHON_CMD -c "import reportlab" 2>/dev/null; then
    echo "✓ ReportLab ready"
else
    echo "✗ ReportLab installation failed"
fi

if $PYTHON_CMD -c "import PIL" 2>/dev/null; then
    echo "✓ Pillow ready"
else
    echo "✗ Pillow installation failed"
fi

echo
echo "Installation complete!"
echo
echo "To run the Visual Novel Node Editor:"
echo "  $PYTHON_CMD main_clean.py"
echo
