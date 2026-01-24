# Enterprise Plant Operations System (ePOS)

## 🏭 Overview
Comprehensive modularized microservices-based enterprise management system for plant operations with Python backend and React frontend.

## 📋 Modules
1. **Colony Maintenance Management** - Facility management and maintenance requests
2. **Guest House Management** - Room bookings, housekeeping, and billing
3. **Heavy Equipment Management** - Equipment scheduling and safety compliance
4. **Night Vigilance Reporting** - Security patrol tracking and incident reporting
5. **Vehicle Requisition System** - Fleet management and GPS tracking
6. **Visitor Gate Pass Management** - Visitor registration and safety training
7. **Canteen Management System** - Meal ordering and consumption tracking

## 🏗️ Architecture

### Microservices Architecture
```
├── api-gateway/          # API Gateway (FastAPI)
├── services/
│   ├── colony-maintenance/
│   ├── guest-house/
│   ├── equipment/
│   ├── vigilance/
│   ├── vehicle/
│   ├── visitor/
│   └── canteen/
├── shared/               # Shared libraries
├── frontend/             # React Application
└── infrastructure/       # Docker, configs
```

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite with SQLAlchemy ORM (upgradeable to PostgreSQL)
- **Authentication**: JWT tokens
- **API Documentation**: Swagger/OpenAPI
- **Background Tasks**: Celery with Redis
- **File Storage**: Local filesystem
- **Real-time**: WebSocket support

#### Frontend
- **Framework**: React 18+ with TypeScript
- **UI Library**: Material-UI (MUI)
- **State Management**: Redux Toolkit
- **Routing**: React Router v6
- **API Client**: Axios with React Query
- **Forms**: React Hook Form with Zod validation
- **Charts**: Recharts / Chart.js

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional for caching)
- Docker & Docker Compose (recommended)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Docker Deployment
```bash
docker-compose up -d
```

## 📁 Project Structure

### Backend Services
Each microservice follows the same structure:
```
service-name/
├── api/              # API routes
├── models/           # Database models
├── schemas/          # Pydantic schemas
├── services/         # Business logic
├── repositories/     # Data access layer
├── utils/            # Utilities
├── tests/            # Unit tests
└── main.py           # Service entry point
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/   # Reusable components
│   ├── modules/      # Module-specific components
│   ├── services/     # API services
│   ├── store/        # Redux store
│   ├── hooks/        # Custom hooks
│   ├── utils/        # Utilities
│   └── App.tsx       # Main app
```

## 🔐 Security Features
- JWT-based authentication
- Role-based access control (RBAC)
- API rate limiting
- Input validation and sanitization
- CORS configuration
- Encrypted sensitive data

## 📊 Key Features

### Common Features Across Modules
- Multi-level approval workflows
- Real-time notifications (Email/SMS)
- Document upload and management
- Analytics and reporting dashboards
- Mobile-responsive design
- Audit trail and logging
- Export to Excel/PDF

### Module-Specific Highlights
- **Colony**: Asset tracking, vendor ratings, escalation matrix
- **Guest House**: Cost center validation, housekeeping automation
- **Equipment**: Operator certification, safety compliance
- **Vigilance**: RFID checkpoints, live GPS tracking
- **Vehicle**: GPS tracking, DOA-based approvals
- **Visitor**: Safety training, medical clearance
- **Canteen**: Biometric authentication, kiosk integration

## 🔌 Integration Points
- SAP integration for cost centers and financial data (Phase 1)
- HR system integration for employee master data
- Email/SMS gateway for notifications
- Biometric device integration
- GPS tracking devices
- RFID readers

## 📈 Phased Implementation

### Phase 1 (MVP)
- Core functionality for all modules
- Basic approval workflows
- Essential reporting

### Phase 2 (Advanced)
- GPS/RFID integration
- Advanced analytics
- Cost optimization features
- Mobile apps

## 🧪 Testing
```bash
# Backend tests
pytest services/*/tests/

# Frontend tests
npm test
```

## 📚 API Documentation
Once services are running, access API docs at:
- API Gateway: http://localhost:8000/docs
- Individual services: http://localhost:800X/docs

## 🤝 Contributing
Follow modular development approach - each service is independently deployable.

## 📝 License
Proprietary - Internal Use Only

## 👥 Support
Contact: IT Department
