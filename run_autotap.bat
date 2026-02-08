@echo off
title AutoTap Universal Launcher
color 0A

echo =====================================
echo   AutoTap Launcher - CreatorIna
echo =====================================
echo.

REM ===============================
REM Auto Detect Python
REM ===============================
where python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Python tidak ditemukan!
    echo Install Python dulu dan centang "Add Python to PATH"
    pause
    exit
)

echo ✅ Python ditemukan
echo.

REM ===============================
REM Upgrade PIP
REM ===============================
echo 🔄 Update pip...
python -m pip install --upgrade pip >nul

REM ===============================
REM Install Required Libraries
REM ===============================
echo 🔄 Mengecek library...

python -m pip install pyautogui opencv-python numpy watchdog pillow

echo.
echo ✅ Semua library siap
echo.

REM ===============================
REM Cek File Script
REM ===============================
IF NOT EXIST launcher_watch.py (
    echo ❌ launcher_watch.py tidak ditemukan!
    pause
    exit
)

IF NOT EXIST auto_tap.py (
    echo ❌ auto_tap.py tidak ditemukan!
    pause
    exit
)

IF NOT EXIST templates (
    echo ⚠ Folder templates belum ada - membuat folder...
    mkdir templates
)

echo.
echo 🚀 Menjalankan AutoTap...
echo Tekan CTRL+C untuk stop
echo.

python launcher_watch.py

pause
