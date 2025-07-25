#!/bin/bash

echo "Building Visual Novel Node Editor to executable..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python 3.8+"
        exit 1
    else
        PYTHON_CMD=python
    fi
else
    PYTHON_CMD=python3
fi

# Check if PyInstaller is installed
if ! $PYTHON_CMD -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found, installing..."
    $PYTHON_CMD -m pip install pyinstaller
    echo
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist Visual_Novel_Editor
echo

# Build executable
echo "Building executable with PyInstaller..."
echo "This may take several minutes..."
echo

$PYTHON_CMD -m PyInstaller build_exe.spec

# Check if build was successful
if [ -f "dist/Visual_Novel_Editor" ]; then
    echo
    echo "✓ Build successful!"
    echo
    echo "Executable created: dist/Visual_Novel_Editor"
    echo "File size: $(stat -f%z 'dist/Visual_Novel_Editor' 2>/dev/null || stat -c%s 'dist/Visual_Novel_Editor' 2>/dev/null) bytes"
    echo
    echo "You can now distribute this single executable file!"
    echo
    echo "To test the executable:"
    echo "  cd dist"
    echo "  ./Visual_Novel_Editor"
    echo
else
    echo
    echo "✗ Build failed!"
    echo "Check the error messages above."
    echo
fi
