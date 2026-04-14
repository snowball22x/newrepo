@echo off
:: Adds recorder.exe to the Windows Registry startup key so it runs at login
:: Run this script as Administrator for best results

set "EXE_PATH=%~dp0recorder.exe"
set "REG_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
set "REG_NAME=CameraRecorder"

echo Installing CameraRecorder to Windows startup...
reg add "%REG_KEY%" /v "%REG_NAME%" /t REG_SZ /d "\"%EXE_PATH%\"" /f

if %errorlevel% == 0 (
    echo.
    echo SUCCESS: CameraRecorder will now start automatically at login.
    echo Location: %EXE_PATH%
) else (
    echo.
    echo ERROR: Failed to add registry entry. Try running as Administrator.
)
echo.
pause
