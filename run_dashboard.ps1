# India E-Commerce Analytics Dashboard Launcher (PowerShell)
# This script sets up and runs the Streamlit dashboard

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  India E-Commerce Analytics Dashboard" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install requirements
Write-Host ""
Write-Host "[*] Checking dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    Write-Host "Please run: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install statsmodels
Write-Host "[*] Installing statsmodels..." -ForegroundColor Yellow
pip install -q statsmodels

Write-Host ""
Write-Host "[OK] All dependencies installed" -ForegroundColor Green
Write-Host ""
Write-Host " Starting Dashboard..." -ForegroundColor Green
Write-Host " Open your browser at: http://localhost:8501" -ForegroundColor Yellow
Write-Host ""

python -m streamlit run src/app.py

Read-Host "Press Enter to close this window"
