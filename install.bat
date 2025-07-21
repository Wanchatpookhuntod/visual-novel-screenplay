@echo off
echo Installing Visual Novel Node Editor Dependencies...
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Show Python version
echo Using Python version:
python --version
echo.

:: Upgrade pip to latest version
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

:: Install requirements
echo Installing project dependencies...
python -m pip install -r requirements.txt
echo.

:: Verify installation
echo Verifying installation...
python -c "import PySide6; print('✓ PySide6 installed successfully')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ PySide6 installation failed
) else (
    echo ✓ PySide6 ready
)

python -c "import reportlab; print('✓ ReportLab installed successfully')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ ReportLab installation failed
) else (
    echo ✓ ReportLab ready
)

python -c "import PIL; print('✓ Pillow installed successfully')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ Pillow installation failed
) else (
    echo ✓ Pillow ready
)

echo.
echo Installation complete! 
echo.
echo To run the Visual Novel Node Editor:
echo   python main_clean.py
echo.
pause
