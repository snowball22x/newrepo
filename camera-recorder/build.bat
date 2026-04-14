@echo off
:: Build script for camera-recorder
:: Requirements: Python 3.8+, pip install pyinstaller
:: Run this on a Windows machine to produce recorder.exe

echo ============================================
echo  camera-recorder build script
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.8+ and add to PATH.
    pause
    exit /b 1
)

:: Install PyInstaller if needed
echo Installing/updating PyInstaller...
pip install --upgrade pyinstaller >nul 2>&1

:: Build
echo Building recorder.exe...
pyinstaller recorder.spec --clean

if %errorlevel% == 0 (
    echo.
    echo BUILD SUCCESS!
    echo Output: dist\recorder.exe
    echo.
    echo Next steps:
    echo   1. Copy dist\recorder.exe to your deployment folder
    echo   2. Download ffmpeg.exe from https://www.gyan.dev/ffmpeg/builds/
    echo      and place it in the same folder as recorder.exe
    echo   3. Edit config.json with your camera name and schedules
    echo   4. Run list_cameras.bat to find your camera name
    echo   5. Run test_recording.bat to verify everything works
    echo   6. Run install_startup.bat to start at login (optional)
) else (
    echo.
    echo BUILD FAILED. Check the output above for errors.
)
echo.
pause
