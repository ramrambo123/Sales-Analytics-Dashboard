@echo off
REM India E-Commerce Analytics Dashboard Launcher
REM This script sets up and runs the Streamlit dashboard

echo.
echo ========================================
echo   India E-Commerce Analytics Dashboard
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install requirements if not already installed
echo [*] Checking dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [*] Installing statsmodels (if needed)...
pip install -q statsmodels

echo.
echo [OK] All dependencies installed
echo.
echo Launching dashboard at http://localhost:8501
echo.

python -m streamlit run src/app.py

pause

