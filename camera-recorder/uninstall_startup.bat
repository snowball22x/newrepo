@echo off
set "REG_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
set "REG_NAME=CameraRecorder"

echo Removing CameraRecorder from Windows startup...
reg delete "%REG_KEY%" /v "%REG_NAME%" /f

if %errorlevel% == 0 (
    echo.
    echo SUCCESS: CameraRecorder removed from startup.
) else (
    echo.
    echo NOTE: Registry entry not found or already removed.
)
echo.
pause
