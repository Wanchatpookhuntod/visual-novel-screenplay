@echo off
echo Building Visual Novel Node Editor to EXE...
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found, installing...
    python -m pip install pyinstaller
    echo.
)

:: Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "Visual_Novel_Editor.exe" del /q "Visual_Novel_Editor.exe"
echo.

:: Build executable
echo Building executable with PyInstaller...
echo This may take several minutes...
echo.

python -m PyInstaller build_exe.spec

:: Check if build was successful
if exist "dist\Visual_Novel_Editor.exe" (
    echo.
    echo ✓ Build successful!
    echo.
    echo Executable created: dist\Visual_Novel_Editor.exe
    echo File size: 
    for %%I in ("dist\Visual_Novel_Editor.exe") do echo   %%~zI bytes
    echo.
    echo You can now distribute this single .exe file!
    echo.
    echo To test the executable:
    echo   cd dist
    echo   Visual_Novel_Editor.exe
    echo.
) else (
    echo.
    echo ✗ Build failed!
    echo Check the error messages above.
    echo.
)

pause
