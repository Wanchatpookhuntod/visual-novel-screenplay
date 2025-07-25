# PowerShell script to build Visual Novel Node Editor to EXE
# Usage: .\build_exe.ps1

Write-Host "Building Visual Novel Node Editor to EXE..." -ForegroundColor Green
Write-Host ""

# Get Python executable from environment
$pythonExe = "C:/Users/TRU-5/Envs/nonthop/Scripts/python.exe"

# Check if Python is available
if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: Python not found at $pythonExe" -ForegroundColor Red
    Write-Host "Please check your Python environment"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if PyInstaller is installed
try {
    & $pythonExe -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PyInstaller not found, installing..." -ForegroundColor Yellow
        & $pythonExe -m pip install pyinstaller
        Write-Host ""
    }
} catch {
    Write-Host "Error checking PyInstaller" -ForegroundColor Red
    exit 1
}

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "Visual_Novel_Editor.exe") { Remove-Item -Force "Visual_Novel_Editor.exe" }
Write-Host ""

# Build executable
Write-Host "Building executable with PyInstaller..." -ForegroundColor Green
Write-Host "This may take several minutes..." -ForegroundColor Yellow
Write-Host ""

try {
    & $pythonExe -m PyInstaller build_exe.spec
    
    # Check if build was successful
    if (Test-Path "dist\Visual_Novel_Editor.exe") {
        Write-Host ""
        Write-Host "✓ Build successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Executable created: dist\Visual_Novel_Editor.exe" -ForegroundColor Cyan
        
        $fileSize = (Get-Item "dist\Visual_Novel_Editor.exe").Length
        $fileSizeMB = [Math]::Round($fileSize / 1MB, 2)
        Write-Host "File size: $fileSizeMB MB" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "You can now distribute this single .exe file!" -ForegroundColor Green
        Write-Host ""
        Write-Host "To test the executable:" -ForegroundColor Yellow
        Write-Host "  cd dist" -ForegroundColor Gray
        Write-Host "  .\Visual_Novel_Editor.exe" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "✗ Build failed!" -ForegroundColor Red
        Write-Host "Check the error messages above." -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host ""
    Write-Host "✗ Build failed with error:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit"
