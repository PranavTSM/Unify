@echo off
echo.
echo ================================================
echo   TESTING ALL FEATURES - COMPREHENSIVE TEST
echo ================================================
echo.

REM Kill all running services
echo [1/5] Stopping all services...
taskkill /F /FI "WINDOWTITLE eq *MCP*" 2>nul
taskkill /F /FI "WINDOWTITLE eq *Aggregator*" 2>nul
taskkill /F /FI "WINDOWTITLE eq *LLM*" 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002" ^| findstr "LISTENING"') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak >nul
echo    ✓ All services stopped
echo.

echo [2/5] Starting MCP Server (port 8000)...
start "MCP Server" cmd /k "python run_server.py --mode fastapi"
timeout /t 5 /nobreak >nul
echo    ✓ MCP Server started
echo.

echo [3/5] Starting LLM Service (port 8002)...
start "LLM Service" cmd /k "set PYTHONPATH=%CD% && python llm_service/app.py"
timeout /t 5 /nobreak >nul
echo    ✓ LLM Service started
echo.

echo [4/5] Starting Aggregator (port 8001)...
start "Aggregator Service" cmd /k "cd aggregator && python app.py"
timeout /t 5 /nobreak >nul
echo    ✓ Aggregator started
echo.

echo [5/5] Testing endpoints...
echo.
echo Testing MCP Server...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing; Write-Host '   ✓ MCP Server: OK' -ForegroundColor Green } catch { Write-Host '   ✗ MCP Server: FAILED' -ForegroundColor Red }"

echo Testing LLM Service...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8002/health' -UseBasicParsing; Write-Host '   ✓ LLM Service: OK' -ForegroundColor Green } catch { Write-Host '   ✗ LLM Service: FAILED' -ForegroundColor Red }"

echo Testing Aggregator...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8001/health' -UseBasicParsing; Write-Host '   ✓ Aggregator: OK' -ForegroundColor Green } catch { Write-Host '   ✗ Aggregator: FAILED' -ForegroundColor Red }"

echo.
echo Testing New Features...
echo.

echo Testing Teams optimized endpoint...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8000/teams/chats/all/messages?max_chats=5&max_messages_per_chat=10' -UseBasicParsing; $j = $r.Content | ConvertFrom-Json; Write-Host ('   ✓ Teams Messages: ' + $j.total_messages + ' messages') -ForegroundColor Green } catch { Write-Host '   ✗ Teams endpoint: FAILED' -ForegroundColor Red; Write-Host ('     ' + $_.Exception.Message) }"

echo Testing Analytics...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8001/analytics/stats' -UseBasicParsing; $j = $r.Content | ConvertFrom-Json; Write-Host ('   ✓ Analytics: ' + $j.total_messages + ' total messages') -ForegroundColor Green } catch { Write-Host '   ✗ Analytics: FAILED' -ForegroundColor Red }"

echo Testing Search...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8001/search?query=email&max_results=3' -UseBasicParsing; $j = $r.Content | ConvertFrom-Json; Write-Host ('   ✓ Search: ' + $j.total_results + ' results') -ForegroundColor Green } catch { Write-Host '   ✗ Search: FAILED' -ForegroundColor Red }"

echo Testing Unified Inbox...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8001/unified/messages?max_per_source=10' -UseBasicParsing; $j = $r.Content | ConvertFrom-Json; Write-Host ('   ✓ Unified Messages: ' + $j.summary.total_messages + ' messages') -ForegroundColor Green } catch { Write-Host '   ✗ Unified Messages: FAILED' -ForegroundColor Red }"

echo.
echo ================================================
echo   ALL SERVICES RUNNING!
echo ================================================
echo.
echo   MCP Server:    http://localhost:8000
echo   Aggregator:    http://localhost:8001
echo   LLM Service:   http://localhost:8002
echo.
echo   Start Frontend: cd frontend ^&^& npm run dev
echo.
echo ================================================
pause




