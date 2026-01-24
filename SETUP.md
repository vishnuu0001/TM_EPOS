# ePOS - Setup Guide

## Prerequisites

### Required Software
- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18+**: [Download Node.js](https://nodejs.org/)
- **Redis** (Optional): [Download Redis](https://redis.io/download)

### Recommended Tools
- **VS Code**: [Download VS Code](https://code.visualstudio.com/)
- **Postman**: For API testing
- **pgAdmin**: PostgreSQL GUI tool
SQLite Browser**: For viewing SQLite database
## Quick Start (Development)

### 1. Clone the Repository
```bash
cd e:\TechDev2026_POS
```

### 2. Setup Database

#### Initialize SQLite Database

SQLite requires no installation - it's file-based and included with Python.

```bash
cd backend
python init_db.py
```

This will:
- Create the database file at `backend/data/epos.db`
- Create all necessary tables  
- Create default admin user (admin@epos.com / Admin@123)
- Create default roles

### 3. Setup Backend

#### Create Virtual Environment
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment
```bash
# Copy example env file
copy .env.example .env

# Edit .env file with your configuration
# Important: Change SECRET_KEY in production!
```

#### Run API Gateway
```bash
cd api-gateway
python main.py
```

The API Gateway will start at: http://localhost:8000
API Documentation: http://localhost:8000/docs

#### Run Colony Maintenance Service
Open a new terminal:
```bash
cd backend/services/colony-maintenance
python main.py
```

Service will start at: http://localhost:8001

### 4. Setup Frontend

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Configure Environment
```bash
# Copy example env file
copy .env.example .env
```

#### Run Development Server
```bash
npm run dev
```

Frontend will start at: http://localhost:3000

## Default Login Credentials

- **Email**: admin@epos.com
- **Password**: Admin@123

## Docker Deployment (Production)

### Using Docker Compose
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Project Structure

```
TechDev2026_POS/
├── backend/
│   ├── api-gateway/          # API Gateway service
│   ├── services/             # Microservices
│   │   ├── colony-maintenance/
│   │   ├── guest-house/
│   │   ├── equipment/
│   │   ├── vigilance/
│   │   ├── vehicle/
│   │   ├── visitor/
│   │   └── canteen/
│   ├── shared/               # Shared utilities
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   ├── store/            # Redux store
│   │   └── main.tsx          # Entry point
│   └── package.json          # Node dependencies
├── infrastructure/
│   └── postgres/
│       └── init.sql          # Database initialization
├── docker-compose.yml        # Docker orchestration
└── README.md                 # Documentation
```

## Module Development Status

### ✅ Completed
- Project architecture and structure
- Shared backend utilities (auth, database, notifications)
- API Gateway with authentication
- Colony Maintenance Service (basic implementation)
- React frontend with Material-UI
- Login and Dashboard pages
- Redux state management
- API service layer

### 🚧 In Progress
- Colony Maintenance full features
- Guest House Management service
- Equipment Management service
- Vigilance Reporting service
- Vehicle Requisition service
- Visitor Gate Pass service
- Canteen Management service

### 📋 Pending
- Module-specific UI components
- Advanced workflows and approvals
- GPS tracking integration
- RFID integration
- Biometric integration
- SAP integration
- Mobile applications

## Running Individual Services

### API Gateway Only
```bash
cd backend/api-gateway
uvicorn main:app --reload --port 8000
```

### Colony Maintenance Service
```bash
cd backend/services/colony-maintenance
uvicorn main:app --reload --port 8001
```

### Frontend Only
```bash
cd frontend
npm run dev
```

## Testing

### Backend Tests
```bash
cd backend
pytest services/*/tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Building for Production

### Backend
```bash
cd backend
# Each service can be built separately
docker build -t epos-api-gateway api-gateway/
docker build -t epos-colony-service services/colony-maintenance/
```

### Frontend
```bash
cd frontend
npm run build
# Built files will be in dist/ directory
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env file
- Verify database user permissions

### Port Already in Use
```bash
# Check which process is using the port
netstat -ano | findstr :8000

# Kill the process (Windows)
taskkill /PID <process_id> /F
```

### Module Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python path configuration

### Frontend Build Errors
- Clear node_modules: `rm -rf node_modules`
- Clear cache: `npm cache clean --force`
- Reinstall: `npm install`

## Next Steps

1. **Complete remaining microservices**: Implement all 7 modules
2. **Add comprehensive UI components**: Forms, tables, dashboards for each module
3. **Implement workflows**: Approval processes, notifications, escalations
4. **Add integration points**: SAP, biometric devices, GPS trackers
5. **Deploy to staging**: Test in production-like environment
6. **User acceptance testing**: Gather feedback and iterate
7. **Production deployment**: Deploy to production servers

## Support

For issues or questions, contact the development team or refer to the inline documentation.

## License

Proprietary - Internal Use Only
