@echo off
echo ========================================
echo  Unified Inbox - Service Status Check
echo ========================================
echo.

echo Checking MCP Server (Port 8000)...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] MCP Server is running
) else (
    echo [ERROR] MCP Server is NOT running
)
echo.

echo Checking Aggregator (Port 8001)...
curl -s http://localhost:8001/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Aggregator is running
    curl -s http://localhost:8001/health
) else (
    echo [ERROR] Aggregator is NOT running
    echo Please start: cd aggregator ^&^& python app.py
)
echo.

echo Checking LLM Service (Port 8002)...
curl -s http://localhost:8002/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] LLM Service is running
) else (
    echo [ERROR] LLM Service is NOT running
    echo Please start: cd llm_service ^&^& python -m uvicorn app:app --host 0.0.0.0 --port 8002
)
echo.

echo Checking Frontend (Port 5173/5174)...
curl -s http://localhost:5174 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend is running on port 5174
) else (
    curl -s http://localhost:5173 >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Frontend is running on port 5173
    ) else (
        echo [ERROR] Frontend is NOT running
        echo Please start: cd frontend ^&^& npm run dev
    )
)
echo.

echo ========================================
echo  Service Status Complete
echo ========================================
echo.
echo To fix CORS errors:
echo 1. Make sure aggregator is restarted after CORS changes
echo 2. Run: restart_aggregator.bat
echo 3. Refresh browser (Ctrl + Shift + R)
echo.
pause

