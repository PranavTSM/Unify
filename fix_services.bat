@echo off
REM Quick fix for service issues

echo ========================================
echo Service Diagnostic and Fix
echo ========================================
echo.

echo Step 1: Checking which services are running...
echo.

REM Check MCP Server
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] MCP Server is running
) else (
    echo [X] MCP Server is NOT running
    echo.
    echo PROBLEM: MCP Server (port 8000) is not responding
    echo This is why you're getting timeouts!
    echo.
    echo FIX: Open a new terminal and run:
    echo      cd mcp_server
    echo      python app.py
    echo.
    pause
    exit /b 1
)

REM Check Aggregator
curl -s http://localhost:8001/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Aggregator is running
) else (
    echo [X] Aggregator is NOT running
)

REM Check LLM Service
curl -s http://localhost:8002/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] LLM Service is running
) else (
    echo [X] LLM Service is NOT running
)

echo.
echo Step 2: Running detailed diagnostic...
echo.

python check_mcp_server.py

echo.
echo ========================================
echo NEXT STEPS
echo ========================================
echo.
echo 1. Make sure MCP Server is running (port 8000)
echo 2. Authenticate if needed:
echo    - Google:    http://localhost:8000/google/auth
echo    - Microsoft: http://localhost:8000/msgraph/auth
echo 3. Restart aggregator if needed
echo.

pause

