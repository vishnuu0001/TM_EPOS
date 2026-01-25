#!/bin/bash

echo "================================================"
echo "  ePOS - Quick Start Script"
echo "  Enterprise Plant Operations System"
echo "================================================"
echo ""

if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY="9xp5cNa3iTm2NgX/mmFcHeK3yXjRVhpDfyiR+SslNPM="
fi

show_menu() {
    echo "Please select an option:"
    echo ""
    echo "1. Setup Backend (First Time)"
    echo "2. Setup Frontend (First Time)"
    echo "3. Start API Gateway"
    echo "4. Start Colony Maintenance Service"
    echo "5. Start Frontend Development Server"
    echo "6. Start All with Docker Compose"
    echo "7. View Project Structure"
    echo "8. Exit"
    echo ""
}

setup_backend() {
    echo ""
    echo "Setting up Python backend..."
    echo ""
    cd backend
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
    echo "Creating .env file from example..."
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo "Please edit backend/.env with your configuration!"
    fi
    echo ""
    echo "Backend setup complete!"
    echo ""
    read -p "Press enter to continue..."
    cd ..
}

setup_frontend() {
    echo ""
    echo "Setting up React frontend..."
    echo ""
    cd frontend
    echo "Installing Node dependencies..."
    npm install
    echo ""
    echo "Creating .env file from example..."
    if [ ! -f ".env" ]; then
        cp .env.example .env
    fi
    echo ""
    echo "Frontend setup complete!"
    echo ""
    read -p "Press enter to continue..."
    cd ..
}

start_gateway() {
    echo ""
    echo "Starting API Gateway on http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo ""
    cd backend/api-gateway
    source ../venv/bin/activate
    python main.py
}

start_colony() {
    echo ""
    echo "Starting Colony Maintenance Service on http://localhost:8001"
    echo "API Documentation: http://localhost:8001/docs"
    echo ""
    cd backend/services/colony-maintenance
    source ../../venv/bin/activate
    python main.py
}

start_frontend() {
    echo ""
    echo "Starting React Development Server on http://localhost:3000"
    echo ""
    cd frontend
    npm run dev
}

docker_start() {
    echo ""
    echo "Starting all services with Docker Compose..."
    echo ""
    echo "Frontend: http://localhost:3000"
    echo "API Gateway: http://localhost:8000"
    echo "PostgreSQL: localhost:5432"
    echo ""
    docker-compose up -d
    echo ""
    echo "All services started! View logs with: docker-compose logs -f"
    echo "Stop services with: docker-compose down"
    echo ""
    read -p "Press enter to continue..."
}

view_structure() {
    echo ""
    echo "Project Structure:"
    echo ""
    tree -L 3 -I 'node_modules|venv|__pycache__|*.pyc'
    echo ""
    read -p "Press enter to continue..."
}

while true; do
    show_menu
    read -p "Enter your choice (1-8): " choice
    case $choice in
        1) setup_backend ;;
        2) setup_frontend ;;
        3) start_gateway ;;
        4) start_colony ;;
        5) start_frontend ;;
        6) docker_start ;;
        7) view_structure ;;
        8) echo "Thank you for using ePOS!"; exit 0 ;;
        *) echo "Invalid option. Please try again." ;;
    esac
done
