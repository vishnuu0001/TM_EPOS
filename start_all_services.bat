@echo off
echo Starting all backend services...

cd /d "%~dp0backend"

echo Starting API Gateway on port 8000...
start "API Gateway (8000)" cmd /k "python api-gateway/main.py"
timeout /t 2 /nobreak >nul

echo Starting Colony Maintenance on port 8001...
start "Colony Maintenance (8001)" cmd /k "cd services/colony-maintenance && python main.py"
timeout /t 2 /nobreak >nul

echo Starting Guest House on port 8002...
start "Guest House (8002)" cmd /k "cd services/guesthouse && python main.py"
timeout /t 2 /nobreak >nul

echo Starting Equipment on port 8003...
start "Equipment (8003)" cmd /k "cd services/equipment && python main.py"
timeout /t 2 /nobreak >nul

echo Starting Vigilance on port 8004...
start "Vigilance (8004)" cmd /k "cd services/vigilance && python main.py"
timeout /t 2 /nobreak >nul

echo Starting Vehicle on port 8005...
start "Vehicle (8005)" cmd /k "cd services/vehicle && python main.py"
timeout /t 2 /nobreak >nul

echo Starting Visitor on port 8006...
start "Visitor (8006)" cmd /k "cd services/visitor && python main.py"
timeout /t 2 /nobreak >nul

echo Starting Canteen on port 8007...
start "Canteen (8007)" cmd /k "cd services/canteen && python main.py"
timeout /t 2 /nobreak >nul

echo.
echo All services started!
echo Check the individual windows for startup status.
pause
