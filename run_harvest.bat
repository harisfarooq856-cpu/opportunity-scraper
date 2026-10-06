@echo off
title Opportunity Scraper - Multi-Platform Harvester
echo ======================================================================
echo  OPPORTUNITY SCRAPER & MULTI-SOURCE INTELLIGENCE ENGINE
echo ======================================================================
echo.

set /p PLATFORM="Enter Platform [all / gmb / linkedin / upwork / facebook / reddit / quora] (default: all): "
if "%PLATFORM%"=="" set PLATFORM=all

set /p LOCATION="Enter Target Metro / City (default: Richmond, VA): "
if "%LOCATION%"=="" set LOCATION=Richmond, VA

set /p INDUSTRY="Enter Industry / Niche (default: HVAC): "
if "%INDUSTRY%"=="" set INDUSTRY=HVAC

echo.
echo Launching Harvester: Platform=[%PLATFORM%], Location=[%LOCATION%], Industry=[%INDUSTRY%]...
echo.

python harvest.py --platform "%PLATFORM%" --location "%LOCATION%" --industry "%INDUSTRY%"

echo.
echo ======================================================================
echo  Harvesting Complete! Check the 'output' folder for your reports.
echo ======================================================================
pause
