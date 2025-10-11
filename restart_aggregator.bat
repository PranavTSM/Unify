@echo off
echo ========================================
echo  Restarting Aggregator Service
echo ========================================
echo.

echo Stopping any running aggregator processes...
taskkill /F /FI "WINDOWTITLE eq Aggregator*" /T 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting aggregator service...
cd aggregator
start "Aggregator Service" cmd /k "python app.py"

echo.
echo Waiting for service to start...
timeout /t 5 /nobreak >nul

echo.
echo Checking health...
curl http://localhost:8001/health

echo.
echo ========================================
echo  Aggregator service restarted!
echo  CORS is now configured for port 5174
echo ========================================
echo.
pause

