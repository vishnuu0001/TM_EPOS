from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
import sys
import qrcode
import io
import base64
sys.path.append('../..')

from shared.database import get_db, init_db
from shared.auth import get_current_user
from shared.middleware import setup_cors, setup_gzip, setup_exception_handlers
from shared.config import settings
from shared.file_handler import save_upload_file

from models import (
    DutyRoster, Checkpoint, PatrolLog, Incident, IncidentAttachment, SOSAlert,
    DutyStatus, PatrolStatus, IncidentStatus, SOSStatus, ShiftType
)
from schemas import (
    DutyRosterCreate, DutyRosterUpdate, DutyRosterResponse,
    CheckpointCreate, CheckpointUpdate, CheckpointResponse,
    PatrolLogCreate, PatrolLogResponse,
    IncidentCreate, IncidentUpdate, IncidentResponse,
    SOSAlertCreate, SOSAlertUpdate, SOSAlertResponse,
    DashboardStats
)

# Initialize FastAPI app
app = FastAPI(
    title="Night Vigilance Management Service",
    description="Security patrol, incident reporting, and emergency response system",
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


@app.get("/")
async def root():
    return {"service": "Night Vigilance Management", "status": "running", "port": 8004}


# ========== Duty Roster Endpoints ==========

@app.post("/roster", response_model=DutyRosterResponse)
async def create_duty_roster(
    roster_data: DutyRosterCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new duty roster"""
    # Generate roster number
    count = db.query(DutyRoster).count()
    roster_number = f"DR{datetime.now().year}{count + 1:06d}"
    
    # Create roster
    roster = DutyRoster(
        roster_number=roster_number,
        created_by=current_user["id"],
        **roster_data.dict()
    )
    
    db.add(roster)
    db.commit()
    db.refresh(roster)
    
    return roster


@app.get("/roster", response_model=List[DutyRosterResponse])
async def get_duty_rosters(
    status: Optional[str] = None,
    shift_type: Optional[str] = None,
    guard_id: Optional[str] = None,
    date: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all duty rosters"""
    query = db.query(DutyRoster)
    
    if status:
        query = query.filter(DutyRoster.status == status)
    
    if shift_type:
        query = query.filter(DutyRoster.shift_type == shift_type)
    
    if guard_id:
        query = query.filter(DutyRoster.guard_id == guard_id)
    
    if date:
        target_date = datetime.fromisoformat(date).date()
        query = query.filter(func.date(DutyRoster.duty_date) == target_date)
    
    rosters = query.order_by(DutyRoster.duty_date.desc()).offset(skip).limit(limit).all()
    return rosters


@app.get("/roster/{roster_id}", response_model=DutyRosterResponse)
async def get_duty_roster(
    roster_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific duty roster"""
    roster = db.query(DutyRoster).filter(DutyRoster.id == roster_id).first()
    if not roster:
        raise HTTPException(status_code=404, detail="Duty roster not found")
    return roster


@app.put("/roster/{roster_id}", response_model=DutyRosterResponse)
async def update_duty_roster(
    roster_id: str,
    roster_data: DutyRosterUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a duty roster"""
    roster = db.query(DutyRoster).filter(DutyRoster.id == roster_id).first()
    if not roster:
        raise HTTPException(status_code=404, detail="Duty roster not found")
    
    for field, value in roster_data.dict(exclude_unset=True).items():
        setattr(roster, field, value)
    
    roster.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(roster)
    
    return roster


@app.post("/roster/{roster_id}/check-in")
async def check_in_duty(
    roster_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Guard checks in for duty"""
    roster = db.query(DutyRoster).filter(DutyRoster.id == roster_id).first()
    if not roster:
        raise HTTPException(status_code=404, detail="Duty roster not found")
    
    roster.check_in_time = datetime.utcnow()
    roster.status = DutyStatus.ACTIVE
    
    db.commit()
    db.refresh(roster)
    
    return {"message": "Checked in successfully", "roster": roster}


@app.post("/roster/{roster_id}/check-out")
async def check_out_duty(
    roster_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Guard checks out from duty"""
    roster = db.query(DutyRoster).filter(DutyRoster.id == roster_id).first()
    if not roster:
        raise HTTPException(status_code=404, detail="Duty roster not found")
    
    roster.check_out_time = datetime.utcnow()
    roster.status = DutyStatus.COMPLETED
    
    db.commit()
    db.refresh(roster)
    
    return {"message": "Checked out successfully", "roster": roster}


# ========== Checkpoint Endpoints ==========

def generate_checkpoint_qr(checkpoint_number: str, checkpoint_name: str) -> str:
    """Generate QR code for checkpoint"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"CHECKPOINT:{checkpoint_number}:{checkpoint_name}")
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()


@app.post("/checkpoints", response_model=CheckpointResponse)
async def create_checkpoint(
    checkpoint_data: CheckpointCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new checkpoint"""
    # Generate checkpoint number
    count = db.query(Checkpoint).count()
    checkpoint_number = f"CP{count + 1:04d}"
    
    # Create checkpoint
    checkpoint = Checkpoint(
        checkpoint_number=checkpoint_number,
        **checkpoint_data.dict()
    )
    
    # Generate QR code
    checkpoint.qr_code = generate_checkpoint_qr(checkpoint_number, checkpoint_data.checkpoint_name)
    
    db.add(checkpoint)
    db.commit()
    db.refresh(checkpoint)
    
    return checkpoint


@app.get("/checkpoints", response_model=List[CheckpointResponse])
async def get_checkpoints(
    is_active: Optional[bool] = None,
    sector: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all checkpoints"""
    query = db.query(Checkpoint)
    
    if is_active is not None:
        query = query.filter(Checkpoint.is_active == is_active)
    
    if sector:
        query = query.filter(Checkpoint.sector == sector)
    
    checkpoints = query.order_by(Checkpoint.patrol_sequence).offset(skip).limit(limit).all()
    return checkpoints


@app.get("/checkpoints/{checkpoint_id}", response_model=CheckpointResponse)
async def get_checkpoint(
    checkpoint_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific checkpoint"""
    checkpoint = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint


@app.put("/checkpoints/{checkpoint_id}", response_model=CheckpointResponse)
async def update_checkpoint(
    checkpoint_id: str,
    checkpoint_data: CheckpointUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a checkpoint"""
    checkpoint = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    for field, value in checkpoint_data.dict(exclude_unset=True).items():
        setattr(checkpoint, field, value)
    
    checkpoint.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(checkpoint)
    
    return checkpoint


# ========== Patrol Log Endpoints ==========

@app.post("/patrol-log", response_model=PatrolLogResponse)
async def create_patrol_log(
    log_data: PatrolLogCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a patrol log entry (checkpoint scan)"""
    # Generate log number
    count = db.query(PatrolLog).count()
    log_number = f"PL{datetime.now().year}{count + 1:06d}"
    
    # Get checkpoint details
    checkpoint = db.query(Checkpoint).filter(Checkpoint.id == log_data.checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    # Create patrol log
    patrol_log = PatrolLog(
        log_number=log_number,
        **log_data.dict()
    )
    
    # Check if scan is on time (simple implementation)
    # In production, check against expected scan interval
    patrol_log.is_on_time = True
    patrol_log.delay_minutes = 0
    
    # Location verification (simple distance check if GPS available)
    if log_data.gps_latitude and log_data.gps_longitude and checkpoint.gps_latitude and checkpoint.gps_longitude:
        # In production, implement proper distance calculation
        patrol_log.location_verified = True
    
    db.add(patrol_log)
    db.commit()
    db.refresh(patrol_log)
    
    return patrol_log


@app.get("/patrol-log", response_model=List[PatrolLogResponse])
async def get_patrol_logs(
    duty_roster_id: Optional[str] = None,
    checkpoint_id: Optional[str] = None,
    guard_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patrol logs"""
    query = db.query(PatrolLog)
    
    if duty_roster_id:
        query = query.filter(PatrolLog.duty_roster_id == duty_roster_id)
    
    if checkpoint_id:
        query = query.filter(PatrolLog.checkpoint_id == checkpoint_id)
    
    if guard_id:
        query = query.filter(PatrolLog.guard_id == guard_id)
    
    logs = query.order_by(PatrolLog.scan_time.desc()).offset(skip).limit(limit).all()
    return logs


@app.post("/patrol-log/upload-photo")
async def upload_patrol_photo(
    log_id: str = Query(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload photo for patrol log"""
    log = db.query(PatrolLog).filter(PatrolLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Patrol log not found")
    
    # Save file
    file_path = await save_upload_file(file, "patrol_photos")
    log.photo_path = file_path
    
    db.commit()
    db.refresh(log)
    
    return {"message": "Photo uploaded successfully", "photo_path": file_path}


# ========== Incident Endpoints ==========

@app.post("/incidents", response_model=IncidentResponse)
async def create_incident(
    incident_data: IncidentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Report a new incident"""
    # Generate incident number
    count = db.query(Incident).count()
    incident_number = f"INC{datetime.now().year}{count + 1:06d}"
    
    # Create incident
    incident = Incident(
        incident_number=incident_number,
        **incident_data.dict()
    )
    
    db.add(incident)
    db.commit()
    db.refresh(incident)
    
    return incident


@app.get("/incidents", response_model=List[IncidentResponse])
async def get_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    incident_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all incidents"""
    query = db.query(Incident)
    
    if status:
        query = query.filter(Incident.status == status)
    
    if severity:
        query = query.filter(Incident.severity == severity)
    
    if incident_type:
        query = query.filter(Incident.incident_type == incident_type)
    
    incidents = query.order_by(Incident.incident_time.desc()).offset(skip).limit(limit).all()
    return incidents


@app.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific incident"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.put("/incidents/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    incident_data: IncidentUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an incident"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    for field, value in incident_data.dict(exclude_unset=True).items():
        setattr(incident, field, value)
    
    incident.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    
    return incident


@app.post("/incidents/{incident_id}/acknowledge")
async def acknowledge_incident(
    incident_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Acknowledge an incident"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident.status = IncidentStatus.ACKNOWLEDGED
    incident.acknowledged_by = current_user["id"]
    incident.acknowledged_at = datetime.utcnow()
    
    db.commit()
    db.refresh(incident)
    
    return {"message": "Incident acknowledged", "incident": incident}


@app.post("/incidents/{incident_id}/resolve")
async def resolve_incident(
    incident_id: str,
    resolution_notes: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve an incident"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident.status = IncidentStatus.RESOLVED
    incident.resolution_notes = resolution_notes
    incident.resolved_by = current_user["id"]
    incident.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(incident)
    
    return {"message": "Incident resolved", "incident": incident}


@app.post("/incidents/upload-photo")
async def upload_incident_photo(
    incident_id: str = Query(...),
    description: Optional[str] = None,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload photo for incident"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Save file
    file_path = await save_upload_file(file, "incident_photos")
    
    # Create attachment
    attachment = IncidentAttachment(
        incident_id=incident_id,
        file_name=file.filename,
        file_path=file_path,
        file_type="photo",
        file_size=file.size,
        description=description,
        uploaded_by=current_user["id"]
    )
    
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    return {"message": "Photo uploaded successfully", "attachment": attachment}


# ========== SOS Alert Endpoints ==========

@app.post("/sos", response_model=SOSAlertResponse)
async def create_sos_alert(
    alert_data: SOSAlertCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create SOS emergency alert"""
    # Generate alert number
    count = db.query(SOSAlert).count()
    alert_number = f"SOS{datetime.now().year}{count + 1:06d}"
    
    # Create alert
    alert = SOSAlert(
        alert_number=alert_number,
        **alert_data.dict()
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    # In production: Send real-time notifications to supervisors
    
    return alert


@app.get("/sos", response_model=List[SOSAlertResponse])
async def get_sos_alerts(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all SOS alerts"""
    query = db.query(SOSAlert)
    
    if status:
        query = query.filter(SOSAlert.status == status)
    
    alerts = query.order_by(SOSAlert.alert_time.desc()).offset(skip).limit(limit).all()
    return alerts


@app.get("/sos/{alert_id}", response_model=SOSAlertResponse)
async def get_sos_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific SOS alert"""
    alert = db.query(SOSAlert).filter(SOSAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="SOS alert not found")
    return alert


@app.post("/sos/{alert_id}/acknowledge")
async def acknowledge_sos_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Acknowledge SOS alert"""
    alert = db.query(SOSAlert).filter(SOSAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="SOS alert not found")
    
    alert.status = SOSStatus.RESPONDING
    alert.acknowledged_by = current_user["id"]
    alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    return {"message": "SOS alert acknowledged", "alert": alert}


@app.post("/sos/{alert_id}/resolve")
async def resolve_sos_alert(
    alert_id: str,
    resolution_notes: str,
    false_alarm: bool = False,
    false_alarm_reason: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve SOS alert"""
    alert = db.query(SOSAlert).filter(SOSAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="SOS alert not found")
    
    if false_alarm:
        alert.status = SOSStatus.FALSE_ALARM
        alert.false_alarm = True
        alert.false_alarm_reason = false_alarm_reason
    else:
        alert.status = SOSStatus.RESOLVED
    
    alert.resolution_notes = resolution_notes
    alert.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    return {"message": "SOS alert resolved", "alert": alert}


# ========== Dashboard Endpoints ==========

@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    today = datetime.utcnow().date()
    
    # Total guards (unique guards in rosters)
    total_guards = db.query(func.count(func.distinct(DutyRoster.guard_id))).scalar()
    
    # Active patrols (rosters with active status)
    active_patrols = db.query(DutyRoster).filter(
        DutyRoster.status == DutyStatus.ACTIVE
    ).count()
    
    # Completed patrols today
    completed_patrols = db.query(DutyRoster).filter(
        and_(
            DutyRoster.status == DutyStatus.COMPLETED,
            func.date(DutyRoster.duty_date) == today
        )
    ).count()
    
    # Total checkpoints
    total_checkpoints = db.query(Checkpoint).filter(
        Checkpoint.is_active == True
    ).count()
    
    # Incidents today
    incidents_today = db.query(Incident).filter(
        func.date(Incident.incident_time) == today
    ).count()
    
    # Open incidents
    incidents_open = db.query(Incident).filter(
        Incident.status.in_([
            IncidentStatus.REPORTED,
            IncidentStatus.ACKNOWLEDGED,
            IncidentStatus.INVESTIGATING
        ])
    ).count()
    
    # Active SOS alerts
    sos_alerts_active = db.query(SOSAlert).filter(
        SOSAlert.status.in_([SOSStatus.ACTIVE, SOSStatus.RESPONDING])
    ).count()
    
    # SOS alerts today
    sos_alerts_today = db.query(SOSAlert).filter(
        func.date(SOSAlert.alert_time) == today
    ).count()
    
    # Missed patrols (logs marked as missed)
    missed_patrols = db.query(PatrolLog).filter(
        and_(
            PatrolLog.status == PatrolStatus.MISSED,
            func.date(PatrolLog.scan_time) == today
        )
    ).count()
    
    # Critical incidents (high or critical severity, not closed)
    critical_incidents = db.query(Incident).filter(
        and_(
            Incident.severity.in_(["high", "critical"]),
            Incident.status != IncidentStatus.CLOSED
        )
    ).count()
    
    return DashboardStats(
        total_guards=total_guards,
        active_patrols=active_patrols,
        completed_patrols=completed_patrols,
        total_checkpoints=total_checkpoints,
        incidents_today=incidents_today,
        incidents_open=incidents_open,
        sos_alerts_active=sos_alerts_active,
        sos_alerts_today=sos_alerts_today,
        missed_patrols=missed_patrols,
        critical_incidents=critical_incidents
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
