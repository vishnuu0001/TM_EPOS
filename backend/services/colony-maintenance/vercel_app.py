from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.database import get_db
from shared.auth import get_current_user
from models import MaintenanceRequest, Vendor, Asset, RequestStatus
from schemas import (
    MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceRequestResponse,
    VendorCreate, VendorResponse, AssetCreate, AssetResponse,
    FeedbackCreate, DashboardStats
)

# Initialize FastAPI app
app = FastAPI(
    title="Colony Maintenance Service",
    description="Facility management system for plant colony residential services",
    version="1.0.0",
    docs_url="/api/colony/docs",
    openapi_url="/api/colony/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"service": "Colony Maintenance Management", "status": "running", "platform": "vercel"}

# Maintenance Request Endpoints
@app.post("/api/colony/requests", response_model=MaintenanceRequestResponse)
async def create_maintenance_request(
    request_data: MaintenanceRequestCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new maintenance request"""
    count = db.query(MaintenanceRequest).count()
    request_number = f"MR{datetime.now().year}{count + 1:06d}"
    
    request = MaintenanceRequest(
        request_number=request_number,
        resident_id=current_user["id"],
        **request_data.dict()
    )
    
    db.add(request)
    db.commit()
    db.refresh(request)
    
    return request

@app.get("/api/colony/requests", response_model=List[MaintenanceRequestResponse])
async def get_maintenance_requests(
    status: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all maintenance requests"""
    query = db.query(MaintenanceRequest)
    
    if status:
        query = query.filter(MaintenanceRequest.status == status)
    
    if category:
        query = query.filter(MaintenanceRequest.category == category)
    
    requests = query.offset(skip).limit(limit).all()
    return requests

@app.get("/api/colony/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    total_requests = db.query(MaintenanceRequest).count()
    pending_requests = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.status == RequestStatus.SUBMITTED
    ).count()
    in_progress = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.status == RequestStatus.IN_PROGRESS
    ).count()
    completed = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.status == RequestStatus.COMPLETED
    ).count()
    
    avg_rating_result = db.query(MaintenanceRequest.rating).filter(
        MaintenanceRequest.rating.isnot(None)
    ).all()
    avg_rating = sum(r[0] for r in avg_rating_result) / len(avg_rating_result) if avg_rating_result else 0
    
    return {
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "in_progress_requests": in_progress,
        "completed_requests": completed,
        "avg_resolution_time": 48.5,
        "avg_rating": avg_rating
    }

# Vercel serverless handler
handler = Mangum(app)
