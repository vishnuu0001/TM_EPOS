from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
import sys
import qrcode
import io
import base64
import os
import tempfile
sys.path.append('../..')

from shared.database import get_db, init_db
from shared.auth import get_current_user
from shared.middleware import setup_cors, setup_gzip, setup_exception_handlers
from shared.config import settings
from shared.file_handler import save_upload_file

from models import (
    VisitorRequest, SafetyTraining, TrainingCertificate, 
    MedicalClearance, GatePass, EntryExit,
    RequestStatus, TrainingStatus, GatePassStatus, EntryExitType
)
from schemas import (
    VisitorRequestCreate, VisitorRequestUpdate, VisitorRequestResponse,
    SafetyTrainingCreate, SafetyTrainingUpdate, SafetyTrainingResponse,
    TrainingCertificateCreate, TrainingCertificateResponse,
    MedicalClearanceCreate, MedicalClearanceUpdate, MedicalClearanceResponse,
    GatePassCreate, GatePassUpdate, GatePassResponse,
    EntryExitCreate, EntryExitResponse,
    DashboardStats
)

# Initialize FastAPI app
app = FastAPI(
    title="Visitor Gate Pass Management Service",
    description="Complete visitor management with safety training, medical clearance, and gate pass generation",
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
    if _should_seed() and _should_seed_first_boot("visitor"):
        db = next(get_db())
        try:
            _seed_visitor_data(db)
            _mark_seeded("visitor")
        finally:
            db.close()


def _should_seed() -> bool:
    return os.getenv("SEED_DATA_ON_STARTUP", "true").strip().lower() in {"1", "true", "yes"}


def _require_seed_token(request: Request) -> None:
    token = os.getenv("SEED_ENDPOINT_TOKEN")
    if not token:
        raise HTTPException(status_code=403, detail="Seed endpoint disabled")
    provided = request.headers.get("x-seed-token") or request.query_params.get("token")
    if provided != token:
        raise HTTPException(status_code=401, detail="Invalid seed token")


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


def _seed_visitor_data(db: Session) -> None:
    """Seed visitor requests when empty or below target count."""
    target = int(os.getenv("SEED_VISITOR_COUNT", "1000"))
    existing = db.query(VisitorRequest).count()
    if existing >= target:
        return

    base_index = existing + 1
    now = datetime.utcnow()
    visitor_types = [
        RequestStatus.SUBMITTED,
        RequestStatus.TRAINING_PENDING,
        RequestStatus.PENDING_APPROVAL,
        RequestStatus.APPROVED,
    ]
    type_cycle = ["contractor", "vendor", "consultant", "guest", "official"]

    records = []
    for i in range(base_index, target + 1):
        records.append(
            VisitorRequest(
                request_number=f"VR{now.year}{i:06d}",
                visitor_name=f"Visitor {i}",
                visitor_company="Acme Partners",
                visitor_phone=f"98{(i % 100000000):08d}",
                visitor_email=f"visitor{i}@example.com",
                visitor_type=type_cycle[i % len(type_cycle)],
                sponsor_employee_id="EMP0001",
                sponsor_name="Admin User",
                sponsor_department="Operations",
                purpose_of_visit="Routine plant visit",
                visit_date=now + timedelta(days=(i % 30)),
                expected_duration=2 + (i % 6),
                areas_to_visit="Main Plant",
                safety_required=True,
                medical_required=False,
                status=visitor_types[i % len(visitor_types)],
            )
        )

    db.add_all(records)
    db.commit()


@app.get("/")
async def root():
    return {"service": "Visitor Gate Pass Management", "status": "running", "port": 8006}


@app.post("/admin/seed")
async def seed_visitor_data(request: Request, current_user: dict = Depends(get_current_user)):
    _require_seed_token(request)
    db = next(get_db())
    try:
        _seed_visitor_data(db)
        return {"seeded": True}
    finally:
        db.close()


# ========== Visitor Request Endpoints ==========

@app.post("/requests", response_model=VisitorRequestResponse)
async def create_visitor_request(
    request_data: VisitorRequestCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new visitor request"""
    # Generate request number
    count = db.query(VisitorRequest).count()
    request_number = f"VR{datetime.now().year}{count + 1:06d}"
    
    # Create request
    request = VisitorRequest(
        request_number=request_number,
        **request_data.dict()
    )
    
    db.add(request)
    db.commit()
    db.refresh(request)
    
    # Create safety training record if required
    if request.safety_required:
        training = SafetyTraining(request_id=request.id)
        db.add(training)
        request.status = RequestStatus.TRAINING_PENDING
    
    # Update status if medical required but no training
    if request.medical_required and not request.safety_required:
        request.status = RequestStatus.MEDICAL_PENDING
    
    db.commit()
    db.refresh(request)
    
    return request


@app.get("/requests", response_model=List[VisitorRequestResponse])
async def get_visitor_requests(
    status: Optional[str] = None,
    visitor_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all visitor requests"""
    query = db.query(VisitorRequest)
    
    if status:
        query = query.filter(VisitorRequest.status == status)
    
    if visitor_type:
        query = query.filter(VisitorRequest.visitor_type == visitor_type)
    
    requests = query.order_by(VisitorRequest.created_at.desc()).offset(skip).limit(limit).all()
    return requests


@app.get("/requests/{request_id}", response_model=VisitorRequestResponse)
async def get_visitor_request(
    request_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific visitor request"""
    request = db.query(VisitorRequest).filter(VisitorRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@app.put("/requests/{request_id}", response_model=VisitorRequestResponse)
async def update_visitor_request(
    request_id: str,
    request_data: VisitorRequestUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a visitor request"""
    request = db.query(VisitorRequest).filter(VisitorRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    for field, value in request_data.dict(exclude_unset=True).items():
        setattr(request, field, value)
    
    request.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(request)
    
    return request


@app.post("/requests/{request_id}/approve")
async def approve_request(
    request_id: str,
    level: str = Query(..., description="sponsor, safety, or security"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve visitor request at different levels"""
    request = db.query(VisitorRequest).filter(VisitorRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if level == "sponsor":
        request.approved_by_sponsor = True
    elif level == "safety":
        request.approved_by_safety = True
    elif level == "security":
        request.approved_by_security = True
    else:
        raise HTTPException(status_code=400, detail="Invalid approval level")
    
    # Check if all approvals are complete
    all_approved = (
        request.approved_by_sponsor and
        request.approved_by_safety and
        request.approved_by_security
    )
    
    if all_approved:
        request.status = RequestStatus.APPROVED
        request.final_approved_by = current_user["id"]
        request.final_approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(request)
    
    return {"message": f"Request approved at {level} level", "request": request}


# ========== Safety Training Endpoints ==========

@app.get("/training/{request_id}", response_model=SafetyTrainingResponse)
async def get_safety_training(
    request_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get safety training details for a request"""
    training = db.query(SafetyTraining).filter(SafetyTraining.request_id == request_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training record not found")
    return training


@app.post("/training/{request_id}/complete-video")
async def complete_video_training(
    request_id: str,
    watch_duration: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark video training as completed"""
    training = db.query(SafetyTraining).filter(SafetyTraining.request_id == request_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training record not found")
    
    training.video_watched = True
    training.watch_duration = watch_duration
    training.video_completed_at = datetime.utcnow()
    training.status = TrainingStatus.IN_PROGRESS
    
    db.commit()
    db.refresh(training)
    
    return {"message": "Video training completed", "training": training}


@app.post("/training/{request_id}/submit-quiz")
async def submit_quiz(
    request_id: str,
    score: int,
    total: int = 10,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit quiz results"""
    training = db.query(SafetyTraining).filter(SafetyTraining.request_id == request_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training record not found")
    
    training.quiz_attempted = True
    training.quiz_score = score
    training.quiz_total = total
    training.quiz_attempts += 1
    training.quiz_passed = (score / total) >= 0.7  # 70% passing score
    training.quiz_completed_at = datetime.utcnow()
    
    if training.quiz_passed:
        training.status = TrainingStatus.COMPLETED
        
        # Generate certificate
        cert_count = db.query(TrainingCertificate).count()
        certificate_number = f"SC{datetime.now().year}{cert_count + 1:06d}"
        
        request = db.query(VisitorRequest).filter(VisitorRequest.id == request_id).first()
        
        certificate = TrainingCertificate(
            training_id=training.id,
            certificate_number=certificate_number,
            visitor_name=request.visitor_name,
            issue_date=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(days=365)
        )
        
        db.add(certificate)
        training.certificate_issued = True
        training.certificate_number = certificate_number
        training.certificate_issued_at = datetime.utcnow()
        
        # Update request status
        request.status = RequestStatus.TRAINING_COMPLETED
        if request.medical_required:
            request.status = RequestStatus.MEDICAL_PENDING
        else:
            request.status = RequestStatus.PENDING_APPROVAL
    else:
        training.status = TrainingStatus.FAILED
    
    db.commit()
    db.refresh(training)
    
    return {
        "message": "Quiz submitted successfully",
        "passed": training.quiz_passed,
        "training": training
    }


# ========== Medical Clearance Endpoints ==========

@app.post("/medical", response_model=MedicalClearanceResponse)
async def upload_medical_clearance(
    request_id: str = Query(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload medical clearance document"""
    # Save file
    file_path = await save_upload_file(file, "medical_documents")
    
    # Check if medical clearance already exists
    medical = db.query(MedicalClearance).filter(MedicalClearance.request_id == request_id).first()
    
    if medical:
        # Update existing record
        medical.document_name = file.filename
        medical.document_path = file_path
        medical.document_type = file.content_type
        medical.document_size = file.size
        medical.uploaded_at = datetime.utcnow()
    else:
        # Create new record
        medical = MedicalClearance(
            request_id=request_id,
            document_name=file.filename,
            document_path=file_path,
            document_type=file.content_type,
            document_size=file.size,
            uploaded_at=datetime.utcnow()
        )
        db.add(medical)
    
    # Update request status
    request = db.query(VisitorRequest).filter(VisitorRequest.id == request_id).first()
    request.status = RequestStatus.MEDICAL_UPLOADED
    
    db.commit()
    db.refresh(medical)
    
    return medical


@app.get("/medical/{request_id}", response_model=MedicalClearanceResponse)
async def get_medical_clearance(
    request_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get medical clearance details"""
    medical = db.query(MedicalClearance).filter(MedicalClearance.request_id == request_id).first()
    if not medical:
        raise HTTPException(status_code=404, detail="Medical clearance not found")
    return medical


@app.post("/medical/{medical_id}/verify")
async def verify_medical_clearance(
    medical_id: str,
    verified: bool,
    verification_notes: Optional[str] = None,
    valid_until: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify medical clearance"""
    medical = db.query(MedicalClearance).filter(MedicalClearance.id == medical_id).first()
    if not medical:
        raise HTTPException(status_code=404, detail="Medical clearance not found")
    
    medical.verified = verified
    medical.verified_by = current_user["id"]
    medical.verified_at = datetime.utcnow()
    medical.verification_notes = verification_notes
    medical.valid_from = datetime.utcnow()
    medical.valid_until = valid_until or (datetime.utcnow() + timedelta(days=180))
    
    # Update request status
    request = db.query(VisitorRequest).filter(VisitorRequest.id == medical.request_id).first()
    if verified:
        request.status = RequestStatus.PENDING_APPROVAL
    
    db.commit()
    db.refresh(medical)
    
    return {"message": "Medical clearance verified", "medical": medical}


# ========== Gate Pass Endpoints ==========

def generate_qr_code(data: str) -> str:
    """Generate QR code and return as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()


@app.post("/gate-pass", response_model=GatePassResponse)
async def generate_gate_pass(
    pass_data: GatePassCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate gate pass with QR code"""
    # Check if request is approved
    request = db.query(VisitorRequest).filter(VisitorRequest.id == pass_data.request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request.status != RequestStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Request not approved yet")
    
    # Generate pass number
    count = db.query(GatePass).count()
    pass_number = f"GP{datetime.now().year}{count + 1:06d}"
    
    # Create gate pass
    gate_pass = GatePass(
        pass_number=pass_number,
        issued_by=current_user["id"],
        **pass_data.dict()
    )
    
    # Generate QR code
    qr_data = f"{pass_number}|{pass_data.visitor_name}|{pass_data.visitor_phone}|{pass_data.valid_from}|{pass_data.valid_until}"
    gate_pass.qr_data = qr_data
    gate_pass.qr_code = generate_qr_code(qr_data)
    
    db.add(gate_pass)
    
    # Update request status
    request.status = RequestStatus.GATE_PASS_ISSUED
    
    db.commit()
    db.refresh(gate_pass)
    
    return gate_pass


@app.get("/gate-pass", response_model=List[GatePassResponse])
async def get_gate_passes(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all gate passes"""
    query = db.query(GatePass)
    
    if status:
        query = query.filter(GatePass.status == status)
    
    passes = query.order_by(GatePass.created_at.desc()).offset(skip).limit(limit).all()
    return passes


@app.get("/gate-pass/{pass_id}", response_model=GatePassResponse)
async def get_gate_pass(
    pass_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific gate pass"""
    gate_pass = db.query(GatePass).filter(GatePass.id == pass_id).first()
    if not gate_pass:
        raise HTTPException(status_code=404, detail="Gate pass not found")
    return gate_pass


@app.get("/gate-pass/number/{pass_number}", response_model=GatePassResponse)
async def get_gate_pass_by_number(
    pass_number: str,
    db: Session = Depends(get_db)
):
    """Get gate pass by pass number (for QR scanning)"""
    gate_pass = db.query(GatePass).filter(GatePass.pass_number == pass_number).first()
    if not gate_pass:
        raise HTTPException(status_code=404, detail="Gate pass not found")
    return gate_pass


# ========== Entry/Exit Log Endpoints ==========

@app.post("/entry-exit", response_model=EntryExitResponse)
async def log_entry_exit(
    log_data: EntryExitCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log visitor entry or exit"""
    # Verify gate pass
    gate_pass = db.query(GatePass).filter(GatePass.id == log_data.gate_pass_id).first()
    if not gate_pass:
        raise HTTPException(status_code=404, detail="Gate pass not found")
    
    if gate_pass.status != GatePassStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Gate pass is not active")
    
    # Check validity
    now = datetime.utcnow()
    if now < gate_pass.valid_from or now > gate_pass.valid_until:
        raise HTTPException(status_code=400, detail="Gate pass is not valid at this time")
    
    # Create log entry
    log = EntryExit(**log_data.dict())
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return log


@app.get("/entry-exit", response_model=List[EntryExitResponse])
async def get_entry_exit_logs(
    request_id: Optional[str] = None,
    gate_pass_id: Optional[str] = None,
    log_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get entry/exit logs"""
    query = db.query(EntryExit)
    
    if request_id:
        query = query.filter(EntryExit.request_id == request_id)
    
    if gate_pass_id:
        query = query.filter(EntryExit.gate_pass_id == gate_pass_id)
    
    if log_type:
        query = query.filter(EntryExit.log_type == log_type)
    
    logs = query.order_by(EntryExit.timestamp.desc()).offset(skip).limit(limit).all()
    return logs


@app.get("/entry-exit/active-visitors")
async def get_active_visitors(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of currently active visitors (entered but not exited)"""
    # Find all entries without corresponding exits
    entries = db.query(EntryExit).filter(
        EntryExit.log_type == EntryExitType.ENTRY
    ).all()
    
    active_visitors = []
    for entry in entries:
        # Check if there's a corresponding exit
        exit_log = db.query(EntryExit).filter(
            and_(
                EntryExit.gate_pass_id == entry.gate_pass_id,
                EntryExit.log_type == EntryExitType.EXIT,
                EntryExit.timestamp > entry.timestamp
            )
        ).first()
        
        if not exit_log:
            gate_pass = db.query(GatePass).filter(GatePass.id == entry.gate_pass_id).first()
            active_visitors.append({
                "entry_id": entry.id,
                "gate_pass": gate_pass,
                "entry_time": entry.timestamp,
                "gate_number": entry.gate_number
            })
    
    return {"active_visitors": active_visitors, "count": len(active_visitors)}


@app.get("/active")
async def get_active_visitors_simple(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of currently active visitors - simplified endpoint"""
    # Get all approved requests for today
    today = datetime.now().date()
    active = db.query(VisitorRequest).filter(
        and_(
            VisitorRequest.status == RequestStatus.APPROVED,
            func.date(VisitorRequest.visit_date) == today
        )
    ).all()
    return active


# ========== Dashboard Endpoints ==========

@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    total_requests = db.query(VisitorRequest).count()
    
    pending_approvals = db.query(VisitorRequest).filter(
        VisitorRequest.status.in_([
            RequestStatus.PENDING_APPROVAL,
            RequestStatus.MEDICAL_UPLOADED,
            RequestStatus.TRAINING_COMPLETED
        ])
    ).count()
    
    completed_visits = db.query(VisitorRequest).filter(
        VisitorRequest.status == RequestStatus.GATE_PASS_ISSUED
    ).count()
    
    training_pending = db.query(VisitorRequest).filter(
        VisitorRequest.status == RequestStatus.TRAINING_PENDING
    ).count()
    
    medical_pending = db.query(VisitorRequest).filter(
        VisitorRequest.status == RequestStatus.MEDICAL_PENDING
    ).count()
    
    gate_passes_issued = db.query(GatePass).filter(
        GatePass.status == GatePassStatus.ACTIVE
    ).count()
    
    # Active visitors (entries without exits)
    today = datetime.utcnow().date()
    entries = db.query(EntryExit).filter(
        and_(
            EntryExit.log_type == EntryExitType.ENTRY,
            func.date(EntryExit.timestamp) == today
        )
    ).all()
    
    active_count = 0
    for entry in entries:
        exit_log = db.query(EntryExit).filter(
            and_(
                EntryExit.gate_pass_id == entry.gate_pass_id,
                EntryExit.log_type == EntryExitType.EXIT,
                EntryExit.timestamp > entry.timestamp
            )
        ).first()
        if not exit_log:
            active_count += 1
    
    today_entries = db.query(EntryExit).filter(
        and_(
            EntryExit.log_type == EntryExitType.ENTRY,
            func.date(EntryExit.timestamp) == today
        )
    ).count()
    
    today_exits = db.query(EntryExit).filter(
        and_(
            EntryExit.log_type == EntryExitType.EXIT,
            func.date(EntryExit.timestamp) == today
        )
    ).count()
    
    return DashboardStats(
        total_requests=total_requests,
        pending_approvals=pending_approvals,
        active_visitors=active_count,
        completed_visits=completed_visits,
        training_pending=training_pending,
        medical_pending=medical_pending,
        gate_passes_issued=gate_passes_issued,
        today_entries=today_entries,
        today_exits=today_exits
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
