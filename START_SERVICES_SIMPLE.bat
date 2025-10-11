@echo off
echo ========================================
echo Starting Unify Services
echo ========================================
echo.

echo Step 1: Starting MCP Server (port 8000)...
start "MCP Server" cmd /k "cd mcp_server && ..\.venv\Scripts\python.exe app.py"
timeout /t 3 /nobreak >nul

echo Step 2: Starting LLM Service (port 8002)...
start "LLM Service" cmd /k "cd llm_service && ..\.venv\Scripts\python.exe app.py"
timeout /t 3 /nobreak >nul

echo Step 3: Starting Aggregator (port 8001)...
start "Aggregator" cmd /k "cd aggregator && ..\.venv\Scripts\python.exe app.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo MCP Server:    http://localhost:8000
echo Aggregator:    http://localhost:8001
echo LLM Service:   http://localhost:8002
echo.
echo Press any key to exit...
pause >nul

