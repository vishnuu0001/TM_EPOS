@echo off
echo ================================================
echo   ePOS - Quick Start Script
echo   Enterprise Plant Operations System
echo ================================================
echo.

:MENU
echo Please select an option:
echo.
echo 1. Setup Backend (First Time)
echo 2. Setup Frontend (First Time)
echo 3. Start API Gateway
echo 4. Start Colony Maintenance Service
echo 5. Start Frontend Development Server
echo 6. Start All with Docker Compose
echo 7. View Project Structure
echo 8. Exit
echo.
set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto SETUP_BACKEND
if "%choice%"=="2" goto SETUP_FRONTEND
if "%choice%"=="3" goto START_GATEWAY
if "%choice%"=="4" goto START_COLONY
if "%choice%"=="5" goto START_FRONTEND
if "%choice%"=="6" goto DOCKER_START
if "%choice%"=="7" goto VIEW_STRUCTURE
if "%choice%"=="8" goto END
goto MENU

:SETUP_BACKEND
echo.
echo Setting up Python backend...
echo.
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
echo Activating virtual environment...
call venv\Scripts\activate
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Creating .env file from example...
if not exist .env (
    copy .env.example .env
    echo Please edit backend\.env with your configuration!
)
echo.
echo Backend setup complete!
echo.
pause
goto MENU

:SETUP_FRONTEND
echo.
echo Setting up React frontend...
echo.
cd frontend
echo Installing Node dependencies...
npm install
echo.
echo Creating .env file from example...
if not exist .env (
    copy .env.example .env
)
echo.
echo Frontend setup complete!
echo.
pause
goto MENU

:START_GATEWAY
echo.
echo Starting API Gateway on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
cd backend\api-gateway
call ..\venv\Scripts\activate
python main.py
pause
goto MENU

:START_COLONY
echo.
echo Starting Colony Maintenance Service on http://localhost:8001
echo API Documentation: http://localhost:8001/docs
echo.
cd backend\services\colony-maintenance
call ..\..\venv\Scripts\activate
python main.py
pause
goto MENU

:START_FRONTEND
echo.
echo Starting React Development Server on http://localhost:3000
echo.
cd frontend
npm run dev
pause
goto MENU

:DOCKER_START
echo.
echo Starting all services with Docker Compose...
echo.
echo Frontend: http://localhost:3000
echo API Gateway: http://localhost:8000
echo PostgreSQL: localhost:5432
echo.
docker-compose up -d
echo.
echo All services started! View logs with: docker-compose logs -f
echo Stop services with: docker-compose down
echo.
pause
goto MENU

:VIEW_STRUCTURE
echo.
echo Project Structure:
echo.
tree /F /A
echo.
pause
goto MENU

:END
echo.
echo Thank you for using ePOS!
echo.
exit

