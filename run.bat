@echo off
title Telegram Chat & Account Cleaner
chcp 65001 >nul
echo Dang kiem tra moi truong Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python! Vui long cai dat Python tai https://www.python.org/
    pause
    exit /b
)

echo Dang kiem tra thu vien...
pip install -r requirements.txt >nul 2>&1

echo Khoi dong Tool...
python auto_leave_telegram.py
pause
