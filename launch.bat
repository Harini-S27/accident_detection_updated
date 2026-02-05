@echo off
title Accident Detection UI
color 0A
cls

echo.
echo ================================================================
echo    ACCIDENT DETECTION - LAUNCHING UI
echo ================================================================
echo.

cd /d "%~dp0"

echo [CHECK] Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)
echo [OK] Python found

echo.
echo [CHECK] Model file...
if exist "runs\train\accident_severity_yolov11\weights\best.pt" (
    echo [OK] Model found
) else (
    echo [WARNING] Model not found - using default
)

echo.
echo [LAUNCH] Starting UI application...
echo.
echo ================================================================
echo    WINDOW SHOULD APPEAR NOW - CHECK YOUR SCREEN!
echo ================================================================
echo.

python video_test_ui.py

echo.
echo Application closed.
pause

