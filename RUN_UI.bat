@echo off
title Accident Detection UI
color 0A
cls

echo.
echo ================================================================
echo    ACCIDENT DETECTION - STARTING UI
echo ================================================================
echo.

cd /d "%~dp0"

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo Starting UI application...
echo.
echo ================================================================
echo    WINDOW SHOULD APPEAR - CHECK YOUR SCREEN!
echo ================================================================
echo.

python video_test_ui.py

echo.
echo Application closed.
pause
