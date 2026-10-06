@echo off
title Opportunity Scraper - Environment Setup
echo ======================================================================
echo  TARGET: Setting up Opportunity Scraper Engine on Local Machine
echo ======================================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

echo [1/3] Installing Python dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install pip packages.
    pause
    exit /b 1
)

echo.
echo [2/3] Installing Headless Chromium Browser (Playwright)...
playwright install chromium
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Playwright browser.
    pause
    exit /b 1
)

echo.
echo [3/3] Testing Engine Configuration...
python -c "from engines import harvest_gmb, harvest_upwork, harvest_facebook; print('All scraper engines loaded successfully!')"

echo.
echo ======================================================================
echo  SUCCESS: Scraper Engine is Ready to Use!
echo ======================================================================
echo You can now run:
echo   python harvest.py --platform all --location "Richmond, VA" --industry "HVAC"
echo.
pause
