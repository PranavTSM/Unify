@echo off
echo ========================================
echo  Starting All Services
echo ========================================
echo.

echo [1/4] Starting MCP Server (Port 8000)...
start "MCP Server" cmd /k "python run_server.py --mode fastapi"
timeout /t 8 /nobreak >nul

echo [2/4] Starting LLM Service (Port 8002)...
start "LLM Service" cmd /k "cd llm_service && python -m uvicorn app:app --host 0.0.0.0 --port 8002"
timeout /t 5 /nobreak >nul

echo [3/4] Starting Aggregator (Port 8001)...
start "Aggregator" cmd /k "cd aggregator && python app.py"
timeout /t 5 /nobreak >nul

echo [4/4] Starting Frontend (Port 5173/5174)...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo  All services started!
echo ========================================
echo.
echo Services running in separate windows:
echo  ✓ MCP Server    - http://localhost:8000
echo  ✓ LLM Service   - http://localhost:8002
echo  ✓ Aggregator    - http://localhost:8001
echo  ✓ Frontend      - http://localhost:5173 or 5174
echo.
echo Wait 10-15 seconds for all services to be ready
echo Then open: http://localhost:5173 or http://localhost:5174
echo.
pause

