@echo off
title Accident Detection UI - Debug Mode
color 0E
cls

echo.
echo ================================================================
echo    ACCIDENT DETECTION - DEBUG MODE
echo ================================================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python...
python --version
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)
echo [OK] Python found
echo.

echo [2/4] Testing Tkinter...
python -c "import tkinter; print('Tkinter OK')" 2>&1
if errorlevel 1 (
    echo [ERROR] Tkinter not available!
    pause
    exit /b 1
)
echo [OK] Tkinter available
echo.

echo [3/4] Testing imports...
python -c "import sys; sys.path.insert(0, '.'); from video_test_ui import AccidentDetectionUI; print('Imports OK')" 2>&1
if errorlevel 1 (
    echo [WARNING] Import error - but continuing...
)
echo.

echo [4/4] Starting UI...
echo.
echo ================================================================
echo    WINDOW SHOULD APPEAR NOW!
echo    If not, check error messages above
echo ================================================================
echo.

python video_test_ui.py

echo.
echo ================================================================
echo Application closed.
echo ================================================================
pause
