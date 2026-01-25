from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import sys
import os
import tempfile
sys.path.append('../..')

from shared.database import get_db, init_db
from shared.auth import get_current_user
from shared.middleware import setup_cors, setup_gzip, setup_exception_handlers
from shared.config import settings
from shared.file_handler import save_upload_file

from models import (
    MaintenanceRequest, Vendor, Asset, ServiceCategory,
    RequestAttachment, RecurringMaintenance, RequestStatus,
    RequestStatusHistory, Technician
)
from schemas import (
    MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceRequestResponse,
    VendorCreate, VendorUpdate, VendorResponse,
    AssetCreate, AssetUpdate, AssetResponse,
    FeedbackCreate, DashboardStats,
    ServiceCategoryCreate, ServiceCategoryUpdate, ServiceCategoryResponse,
    RecurringMaintenanceCreate, RecurringMaintenanceUpdate, RecurringMaintenanceResponse,
    MaintenanceStatusChange, MaintenanceRequestAssign, RequestStatusHistoryResponse,
    TechnicianCreate, TechnicianUpdate, TechnicianResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="Colony Maintenance Management Service",
    description="Facility management system for plant colony residential services",
    version="1.0.0"
)

# Setup middleware
setup_cors(app, settings.CORS_ORIGINS)
setup_gzip(app)
setup_exception_handlers(app)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    if _should_seed() and _should_seed_first_boot("colony"):
        db = next(get_db())
        try:
            _seed_colony_data(db)
            _mark_seeded("colony")
        finally:
            db.close()


def _should_seed() -> bool:
    return os.getenv("SEED_DATA_ON_STARTUP", "true").strip().lower() in {"1", "true", "yes"}


def _should_seed_first_boot(service_name: str) -> bool:
    flag = os.getenv("SEED_ON_FIRST_BOOT", "false").strip().lower() in {"1", "true", "yes"}
    if not flag:
        return True
    marker_dir = os.getenv("SEED_MARKER_DIR") or tempfile.gettempdir()
    marker_path = os.path.join(marker_dir, f"epos_seeded_{service_name}.flag")
    return not os.path.exists(marker_path)


def _mark_seeded(service_name: str) -> None:
    flag = os.getenv("SEED_ON_FIRST_BOOT", "false").strip().lower() in {"1", "true", "yes"}
    if not flag:
        return
    marker_dir = os.getenv("SEED_MARKER_DIR") or tempfile.gettempdir()
    os.makedirs(marker_dir, exist_ok=True)
    marker_path = os.path.join(marker_dir, f"epos_seeded_{service_name}.flag")
    with open(marker_path, "w", encoding="utf-8") as handle:
        handle.write("seeded")


def _seed_colony_data(db: Session) -> None:
    """Seed colony reference data when empty."""
    # Categories
    if db.query(ServiceCategory).count() == 0:
        categories = [
            {"name": "Electrical", "description": "Wiring, lights, power issues", "sla_hours": 24, "icon": "bolt"},
            {"name": "Plumbing", "description": "Pipes, leaks, faucets", "sla_hours": 24, "icon": "faucet"},
            {"name": "HVAC", "description": "AC and ventilation", "sla_hours": 48, "icon": "snowflake"},
        ]
        for item in categories:
            db.add(ServiceCategory(**item))
        db.commit()

    category_ids = [c.id for c in db.query(ServiceCategory).all()]

    # Vendors
    if db.query(Vendor).count() == 0:
        vendors = [
            {
                "name": "Ravi Singh",
                "company_name": "Ravi Electricals",
                "email": "ravi.electricals@example.com",
                "phone": "9876543210",
                "service_categories": ",".join(category_ids[:2]) if category_ids else "",
                "rating": 4.3,
                "total_jobs": 12,
            },
            {
                "name": "Priya Sharma",
                "company_name": "Sharma Plumbing Co.",
                "email": "priya.plumbing@example.com",
                "phone": "9876543211",
                "service_categories": ",".join(category_ids[1:]) if category_ids else "",
                "rating": 4.1,
                "total_jobs": 8,
            },
        ]
        for item in vendors:
            db.add(Vendor(**item))
        db.commit()

    vendor = db.query(Vendor).first()

    # Assets
    if db.query(Asset).count() == 0:
        assets = [
            {
                "asset_number": "AC-1001",
                "asset_type": "AC",
                "quarter_number": "A-101",
                "make": "LG",
                "model": "DualCool",
                "serial_number": "LGAC-001",
                "installation_date": datetime.utcnow() - timedelta(days=365),
                "warranty_expiry": datetime.utcnow() + timedelta(days=365),
                "status": "active",
            },
            {
                "asset_number": "GY-2001",
                "asset_type": "Geyser",
                "quarter_number": "B-202",
                "make": "Havells",
                "model": "Calisto",
                "serial_number": "HVGY-002",
                "installation_date": datetime.utcnow() - timedelta(days=200),
                "warranty_expiry": datetime.utcnow() + timedelta(days=165),
                "status": "active",
            },
        ]
        for item in assets:
            db.add(Asset(**item))
        db.commit()

    # Technicians
    if db.query(Technician).count() == 0:
        technicians = [
            {
                "name": "Amit Kumar",
                "phone": "9876543212",
                "email": "amit.tech@example.com",
                "specialization": "Electrical",
                "vendor_id": vendor.id if vendor else None,
                "rating": 4.2,
            },
            {
                "name": "Sana Ali",
                "phone": "9876543213",
                "email": "sana.tech@example.com",
                "specialization": "Plumbing",
                "vendor_id": vendor.id if vendor else None,
                "rating": 4.0,
            },
        ]
        for item in technicians:
            db.add(Technician(**item))
        db.commit()

    # Recurring Maintenance
    if db.query(RecurringMaintenance).count() == 0:
        recurring = [
            {
                "name": "Quarterly AC Service",
                "description": "Filter cleaning and gas check",
                "category": "HVAC",
                "frequency": "quarterly",
                "next_schedule_date": datetime.utcnow() + timedelta(days=30),
                "assigned_vendor_id": vendor.id if vendor else None,
                "is_active": True,
            }
        ]
        for item in recurring:
            db.add(RecurringMaintenance(**item))
        db.commit()

    # Maintenance Requests
    target_requests = int(os.getenv("SEED_COLONY_REQUESTS", "1000"))
    existing_requests = db.query(MaintenanceRequest).count()
    if existing_requests < target_requests:
        base_index = existing_requests + 1
        status_cycle = [
            RequestStatus.SUBMITTED,
            RequestStatus.ASSIGNED,
            RequestStatus.IN_PROGRESS,
            RequestStatus.COMPLETED,
        ]
        for i in range(base_index, target_requests + 1):
            db.add(
                MaintenanceRequest(
                    request_number=f"MR{datetime.utcnow().year}{i:06d}",
                    resident_id="EMP0001",
                    quarter_number=f"Q-{(i % 250) + 1}",
                    category="Electrical",
                    sub_category="Wiring",
                    description="Auto-seeded maintenance request",
                    priority="medium",
                    status=status_cycle[i % len(status_cycle)],
                )
            )
        db.commit()


def _log_status_change(db: Session, request_id: str, status: RequestStatus, user_id: Optional[str], notes: Optional[str] = None):
    """Create a status history record."""
    history = RequestStatusHistory(
        request_id=request_id,
        status=status,
        notes=notes,
        changed_by=user_id,
        changed_at=datetime.utcnow()
    )
    db.add(history)
    return history


@app.get("/")
async def root():
    return {"service": "Colony Maintenance Management", "status": "running"}


# Maintenance Request Endpoints
@app.post("/requests", response_model=MaintenanceRequestResponse)
async def create_maintenance_request(
    request_data: MaintenanceRequestCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new maintenance request"""
    # Generate request number
    count = db.query(MaintenanceRequest).count()
    request_number = f"MR{datetime.now().year}{count + 1:06d}"
    
    # Create request
    request = MaintenanceRequest(
        request_number=request_number,
        resident_id=current_user["id"],
        **request_data.dict()
    )
    
    db.add(request)
    db.commit()
    db.refresh(request)

    _log_status_change(db, request.id, request.status, current_user.get("id"))
    db.commit()
    
    return request


@app.get("/requests", response_model=List[MaintenanceRequestResponse])
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
    
    # Filter by status
    if status:
        query = query.filter(MaintenanceRequest.status == status)
    
    # Filter by category
    if category:
        query = query.filter(MaintenanceRequest.category == category)
    
    # Get requests
    requests = query.order_by(MaintenanceRequest.created_at.desc()).offset(skip).limit(limit).all()
    return requests


@app.get("/requests/{request_id}", response_model=MaintenanceRequestResponse)
async def get_maintenance_request(
    request_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific maintenance request"""
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return request


@app.put("/requests/{request_id}", response_model=MaintenanceRequestResponse)
async def update_maintenance_request(
    request_id: str,
    request_data: MaintenanceRequestUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a maintenance request"""
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    payload = request_data.dict(exclude_unset=True)
    new_status = payload.pop("status", None)

    for field, value in payload.items():
        setattr(request, field, value)

    if new_status:
        request.status = new_status
        _log_status_change(db, request.id, request.status, current_user.get("id"))
        if new_status == RequestStatus.COMPLETED:
            request.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(request)
    
    return request


@app.post("/requests/{request_id}/assign", response_model=MaintenanceRequestResponse)
async def assign_maintenance_request(
    request_id: str,
    assign_data: MaintenanceRequestAssign,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign vendor/technician and move to ASSIGNED."""
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    for field, value in assign_data.dict(exclude_unset=True).items():
        setattr(request, field, value)

    request.assigned_at = datetime.utcnow()
    request.status = RequestStatus.ASSIGNED
    _log_status_change(db, request.id, request.status, current_user.get("id"))

    db.commit()
    db.refresh(request)
    return request


@app.post("/requests/{request_id}/status", response_model=RequestStatusHistoryResponse)
async def change_request_status(
    request_id: str,
    status_change: MaintenanceStatusChange,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change request status with history and optional notes/cost."""
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    request.status = status_change.status
    if status_change.actual_cost is not None:
        request.actual_cost = status_change.actual_cost
    if status_change.status == RequestStatus.COMPLETED:
        request.completed_at = datetime.utcnow()

    history = _log_status_change(db, request.id, request.status, current_user.get("id"), status_change.notes)
    db.commit()
    db.refresh(history)
    return history


@app.post("/requests/{request_id}/feedback")
async def submit_feedback(
    request_id: str,
    feedback_data: FeedbackCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for a completed request"""
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request.rating = feedback_data.rating
    request.feedback = feedback_data.feedback
    
    db.commit()
    return {"message": "Feedback submitted successfully"}


@app.post("/requests/{request_id}/upload")
async def upload_attachment(
    request_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload attachment for maintenance request"""
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Save file
    file_info = await save_upload_file(file, folder="colony-maintenance")
    
    # Create attachment record
    attachment = RequestAttachment(
        request_id=request_id,
        file_name=file_info["filename"],
        file_path=file_info["file_path"],
        file_type=file_info["content_type"],
        file_size=file_info["file_size"],
        uploaded_by=current_user["id"]
    )
    
    db.add(attachment)
    db.commit()
    
    return {"message": "File uploaded successfully", "file": file_info}


# Vendor Endpoints
@app.post("/vendors", response_model=VendorResponse)
async def create_vendor(
    vendor_data: VendorCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new vendor"""
    vendor = Vendor(**vendor_data.dict())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@app.get("/vendors", response_model=List[VendorResponse])
async def get_vendors(
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all vendors"""
    query = db.query(Vendor)
    
    if is_active is not None:
        query = query.filter(Vendor.is_active == is_active)
    
    vendors = query.all()
    return vendors

@app.put("/vendors/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: str,
    vendor_data: VendorUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    for field, value in vendor_data.dict(exclude_unset=True).items():
        setattr(vendor, field, value)

    db.commit()
    db.refresh(vendor)
    return vendor


# Asset Endpoints
@app.post("/assets", response_model=AssetResponse)
async def create_asset(
    asset_data: AssetCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new asset"""
    asset = Asset(**asset_data.dict())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@app.get("/assets", response_model=List[AssetResponse])
async def get_assets(
    quarter_number: Optional[str] = None,
    asset_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all assets"""
    query = db.query(Asset)
    
    if quarter_number:
        query = query.filter(Asset.quarter_number == quarter_number)
    
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    
    assets = query.all()
    return assets

@app.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    asset_data: AssetUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    for field, value in asset_data.dict(exclude_unset=True).items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)
    return asset


# Dashboard Endpoints
@app.get("/dashboard/stats", response_model=DashboardStats)
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
    
    overdue_requests = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.status.in_([RequestStatus.SUBMITTED, RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS])
    ).count()

    active_recurring = db.query(RecurringMaintenance).filter(RecurringMaintenance.is_active == True).count()

    open_assignments = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.status == RequestStatus.ASSIGNED
    ).count()
    
    # Calculate average rating
    avg_rating_result = db.query(MaintenanceRequest.rating).filter(
        MaintenanceRequest.rating.isnot(None)
    ).all()
    avg_rating = sum(r[0] for r in avg_rating_result) / len(avg_rating_result) if avg_rating_result else 0
    
    return {
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "in_progress_requests": in_progress,
        "completed_requests": completed,
        "avg_resolution_time": 48.5,  # Placeholder
        "avg_rating": avg_rating,
        "overdue_requests": overdue_requests,
        "active_recurring": active_recurring,
        "open_assignments": open_assignments
    }


# Service Categories
@app.post("/categories", response_model=ServiceCategoryResponse)
async def create_category(
    category_data: ServiceCategoryCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = ServiceCategory(**category_data.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@app.get("/categories", response_model=List[ServiceCategoryResponse])
async def get_categories(
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ServiceCategory)
    if is_active is not None:
        query = query.filter(ServiceCategory.is_active == is_active)
    return query.order_by(ServiceCategory.name).all()


@app.put("/categories/{category_id}", response_model=ServiceCategoryResponse)
async def update_category(
    category_id: str,
    category_data: ServiceCategoryUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = db.query(ServiceCategory).filter(ServiceCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in category_data.dict(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


# Recurring Maintenance
@app.post("/recurring", response_model=RecurringMaintenanceResponse)
async def create_recurring(
    recurring_data: RecurringMaintenanceCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rec = RecurringMaintenance(**recurring_data.dict())
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@app.get("/recurring", response_model=List[RecurringMaintenanceResponse])
async def list_recurring(
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(RecurringMaintenance)
    if is_active is not None:
        query = query.filter(RecurringMaintenance.is_active == is_active)
    return query.order_by(RecurringMaintenance.next_schedule_date).all()


@app.put("/recurring/{recurring_id}", response_model=RecurringMaintenanceResponse)
async def update_recurring(
    recurring_id: str,
    recurring_data: RecurringMaintenanceUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rec = db.query(RecurringMaintenance).filter(RecurringMaintenance.id == recurring_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recurring maintenance not found")
    for field, value in recurring_data.dict(exclude_unset=True).items():
        setattr(rec, field, value)
    db.commit()
    db.refresh(rec)
    return rec


# Technicians
@app.post("/technicians", response_model=TechnicianResponse)
async def create_technician(
    technician_data: TechnicianCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tech = Technician(**technician_data.dict())
    db.add(tech)
    db.commit()
    db.refresh(tech)
    return tech


@app.get("/technicians", response_model=List[TechnicianResponse])
async def list_technicians(
    vendor_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Technician)
    if vendor_id:
        query = query.filter(Technician.vendor_id == vendor_id)
    if is_active is not None:
        query = query.filter(Technician.is_active == is_active)
    return query.order_by(Technician.name).all()


@app.put("/technicians/{technician_id}", response_model=TechnicianResponse)
async def update_technician(
    technician_id: str,
    technician_data: TechnicianUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tech = db.query(Technician).filter(Technician.id == technician_id).first()
    if not tech:
        raise HTTPException(status_code=404, detail="Technician not found")
    for field, value in technician_data.dict(exclude_unset=True).items():
        setattr(tech, field, value)
    db.commit()
    db.refresh(tech)
    return tech


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
