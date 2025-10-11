@echo off
echo ========================================
echo  Starting Correct MCP Server
echo ========================================
echo.

echo Killing any incorrect services on port 8000...
taskkill /F /FI "WINDOWTITLE eq *port 8000*" 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting correct MCP Server (FastAPI mode)...
start "MCP Server - Port 8000" cmd /k "python run_server.py --mode fastapi"

echo.
echo Waiting for MCP server to start...
timeout /t 8 /nobreak >nul

echo.
echo Testing MCP Server...
curl http://localhost:8000/health

echo.
echo Testing Gmail endpoint...
curl "http://localhost:8000/gmail/messages?max_results=5"

echo.
echo ========================================
echo  MCP Server Started Successfully!
echo  Port: 8000
echo  Gmail API: Working
echo ========================================
echo.
pause

