from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path
import os
import tempfile

sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.database import get_db, engine
from shared.middleware import setup_middleware
from shared.auth import get_current_user
from shared.models import User

from models import Base, Equipment, OperatorCertification, EquipmentBooking, UsageLog, MaintenanceSchedule, SafetyPermit, EquipmentStatus, BookingStatus, EquipmentType
from schemas import (
    EquipmentCreate, EquipmentUpdate, EquipmentResponse,
    CertificationCreate, CertificationResponse,
    BookingCreate, BookingUpdate, BookingResponse,
    UsageLogCreate, UsageLogResponse,
    MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse,
    SafetyPermitCreate, SafetyPermitResponse,
    DashboardStats
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Equipment Management Service", version="1.0.0")
setup_middleware(app)


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


def _seed_equipment_data(db: Session) -> None:
    """Seed equipment catalog up to target count."""
    target = int(os.getenv("SEED_EQUIPMENT_COUNT", "1000"))
    existing = db.query(Equipment).count()
    if existing >= target:
        return

    base_index = existing + 1
    type_cycle = [
        EquipmentType.CRANE,
        EquipmentType.FORKLIFT,
        EquipmentType.EXCAVATOR,
        EquipmentType.LOADER,
        EquipmentType.TRUCK,
        EquipmentType.GENERATOR,
    ]
    for i in range(base_index, target + 1):
        e_type = type_cycle[i % len(type_cycle)]
        db.add(
            Equipment(
                equipment_number=f"EQ-{1000 + i}",
                name=f"{e_type.value.title()} {i}",
                equipment_type=e_type,
                manufacturer="AutoGen",
                model=f"Model-{i % 100}",
                capacity=f"{(i % 50) + 1}T",
                location="Plant Yard",
                status=EquipmentStatus.AVAILABLE,
                hourly_rate=500 + (i % 10) * 50,
                requires_certification=True,
                description="Auto-seeded equipment",
            )
        )
    db.commit()


@app.on_event("startup")
async def startup_event():
    if _should_seed() and _should_seed_first_boot("equipment"):
        db = next(get_db())
        try:
            _seed_equipment_data(db)
            _mark_seeded("equipment")
        finally:
            db.close()

@app.get("/")
async def root():
    return {"service": "Equipment Management", "status": "running", "version": "1.0.0"}

# Equipment Management
@app.post("/equipment", response_model=EquipmentResponse)
async def create_equipment(
    equipment_data: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    equipment = Equipment(**equipment_data.model_dump())
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment

@app.get("/equipment", response_model=List[EquipmentResponse])
async def list_equipment(
    status: Optional[EquipmentStatus] = None,
    equipment_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Equipment)
    if status:
        query = query.filter(Equipment.status == status)
    if equipment_type:
        query = query.filter(Equipment.equipment_type == equipment_type)
    return query.offset(skip).limit(limit).all()

@app.get("/equipment/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@app.put("/equipment/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: str,
    equipment_data: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    for key, value in equipment_data.model_dump(exclude_unset=True).items():
        setattr(equipment, key, value)
    
    db.commit()
    db.refresh(equipment)
    return equipment

# Operator Certifications
@app.post("/certifications", response_model=CertificationResponse)
async def create_certification(
    cert_data: CertificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    certification = OperatorCertification(**cert_data.model_dump())
    db.add(certification)
    db.commit()
    db.refresh(certification)
    return certification

@app.get("/certifications", response_model=List[CertificationResponse])
async def list_certifications(
    operator_id: Optional[str] = None,
    equipment_type: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(OperatorCertification)
    if operator_id:
        query = query.filter(OperatorCertification.operator_id == operator_id)
    if equipment_type:
        query = query.filter(OperatorCertification.equipment_type == equipment_type)
    if active_only:
        query = query.filter(
            OperatorCertification.is_active == True,
            OperatorCertification.expiry_date > datetime.now()
        )
    return query.all()

# Verify operator certification
@app.get("/certifications/verify/{operator_id}/{equipment_type}")
async def verify_certification(
    operator_id: str,
    equipment_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    certification = db.query(OperatorCertification).filter(
        OperatorCertification.operator_id == operator_id,
        OperatorCertification.equipment_type == equipment_type,
        OperatorCertification.is_active == True,
        OperatorCertification.expiry_date > datetime.now()
    ).first()
    
    return {
        "is_certified": certification is not None,
        "certification": certification if certification else None
    }

# Bookings
@app.post("/bookings", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check equipment availability
    equipment = db.query(Equipment).filter(Equipment.id == booking_data.equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # Check operator certification if required
    if equipment.requires_certification:
        certification = db.query(OperatorCertification).filter(
            OperatorCertification.operator_id == booking_data.operator_id,
            OperatorCertification.equipment_type == equipment.equipment_type,
            OperatorCertification.is_active == True,
            OperatorCertification.expiry_date > datetime.now()
        ).first()
        
        if not certification:
            raise HTTPException(status_code=400, detail="Operator not certified for this equipment type")
    
    # Check for overlapping bookings
    overlapping = db.query(EquipmentBooking).filter(
        EquipmentBooking.equipment_id == booking_data.equipment_id,
        EquipmentBooking.status.in_([BookingStatus.APPROVED, BookingStatus.ACTIVE]),
        EquipmentBooking.start_time < booking_data.end_time,
        EquipmentBooking.end_time > booking_data.start_time
    ).first()
    
    if overlapping:
        raise HTTPException(status_code=400, detail="Equipment not available for selected time slot")
    
    # Generate booking number
    year = datetime.now().year
    count = db.query(EquipmentBooking).filter(
        EquipmentBooking.booking_number.like(f"EQ{year}%")
    ).count()
    booking_number = f"EQ{year}{count + 1:06d}"
    
    booking = EquipmentBooking(
        **booking_data.model_dump(),
        booking_number=booking_number,
        requested_by_id=current_user.id
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@app.get("/bookings", response_model=List[BookingResponse])
async def list_bookings(
    status: Optional[BookingStatus] = None,
    equipment_id: Optional[str] = None,
    operator_id: Optional[str] = None,
    from_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(EquipmentBooking)
    if status:
        query = query.filter(EquipmentBooking.status == status)
    if equipment_id:
        query = query.filter(EquipmentBooking.equipment_id == equipment_id)
    if operator_id:
        query = query.filter(EquipmentBooking.operator_id == operator_id)
    if from_date:
        query = query.filter(EquipmentBooking.start_time >= from_date)
    
    return query.order_by(EquipmentBooking.start_time.desc()).offset(skip).limit(limit).all()

@app.put("/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(EquipmentBooking).filter(EquipmentBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    for key, value in booking_data.model_dump(exclude_unset=True).items():
        setattr(booking, key, value)
    
    # Update equipment status
    if booking_data.status == BookingStatus.ACTIVE:
        equipment = db.query(Equipment).filter(Equipment.id == booking.equipment_id).first()
        equipment.status = EquipmentStatus.IN_USE
        booking.actual_start_time = datetime.now()
    elif booking_data.status == BookingStatus.COMPLETED:
        equipment = db.query(Equipment).filter(Equipment.id == booking.equipment_id).first()
        equipment.status = EquipmentStatus.AVAILABLE
        booking.actual_end_time = datetime.now()
    
    db.commit()
    db.refresh(booking)
    return booking

@app.post("/bookings/{booking_id}/approve")
async def approve_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(EquipmentBooking).filter(EquipmentBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = BookingStatus.APPROVED
    booking.approved_by_id = current_user.id
    db.commit()
    
    return {"message": "Booking approved", "booking_id": booking_id}

# Usage Logs
@app.post("/usage-logs", response_model=UsageLogResponse)
async def create_usage_log(
    log_data: UsageLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    usage_log = UsageLog(**log_data.model_dump())
    db.add(usage_log)
    db.commit()
    db.refresh(usage_log)
    return usage_log

@app.get("/usage-logs/{booking_id}", response_model=UsageLogResponse)
async def get_usage_log(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    usage_log = db.query(UsageLog).filter(UsageLog.booking_id == booking_id).first()
    if not usage_log:
        raise HTTPException(status_code=404, detail="Usage log not found")
    return usage_log

# Maintenance
@app.post("/maintenance", response_model=MaintenanceResponse)
async def create_maintenance(
    maintenance_data: MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    maintenance = MaintenanceSchedule(**maintenance_data.model_dump())
    db.add(maintenance)
    
    # Update equipment status
    equipment = db.query(Equipment).filter(Equipment.id == maintenance_data.equipment_id).first()
    equipment.status = EquipmentStatus.MAINTENANCE
    
    db.commit()
    db.refresh(maintenance)
    return maintenance

@app.get("/maintenance", response_model=List[MaintenanceResponse])
async def list_maintenance(
    equipment_id: Optional[str] = None,
    pending_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(MaintenanceSchedule)
    if equipment_id:
        query = query.filter(MaintenanceSchedule.equipment_id == equipment_id)
    if pending_only:
        query = query.filter(MaintenanceSchedule.completed_date == None)
    
    return query.order_by(MaintenanceSchedule.scheduled_date.desc()).offset(skip).limit(limit).all()

@app.put("/maintenance/{maintenance_id}", response_model=MaintenanceResponse)
async def update_maintenance(
    maintenance_id: str,
    maintenance_data: MaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    maintenance = db.query(MaintenanceSchedule).filter(MaintenanceSchedule.id == maintenance_id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    
    for key, value in maintenance_data.model_dump(exclude_unset=True).items():
        setattr(maintenance, key, value)
    
    # If completed, update equipment status
    if maintenance_data.completed_date:
        equipment = db.query(Equipment).filter(Equipment.id == maintenance.equipment_id).first()
        equipment.status = EquipmentStatus.AVAILABLE
    
    db.commit()
    db.refresh(maintenance)
    return maintenance

# Safety Permits
@app.post("/safety-permits", response_model=SafetyPermitResponse)
async def create_safety_permit(
    permit_data: SafetyPermitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Generate permit number
    year = datetime.now().year
    count = db.query(SafetyPermit).filter(
        SafetyPermit.permit_number.like(f"SP{year}%")
    ).count()
    permit_number = f"SP{year}{count + 1:06d}"
    
    permit = SafetyPermit(
        **permit_data.model_dump(),
        permit_number=permit_number,
        issued_by_id=current_user.id
    )
    db.add(permit)
    db.commit()
    db.refresh(permit)
    return permit

@app.get("/safety-permits/{permit_id}", response_model=SafetyPermitResponse)
async def get_safety_permit(
    permit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    permit = db.query(SafetyPermit).filter(SafetyPermit.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail="Safety permit not found")
    return permit

# Dashboard Stats
@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_equipment = db.query(Equipment).count()
    available_equipment = db.query(Equipment).filter(Equipment.status == EquipmentStatus.AVAILABLE).count()
    in_use_equipment = db.query(Equipment).filter(Equipment.status == EquipmentStatus.IN_USE).count()
    maintenance_equipment = db.query(Equipment).filter(Equipment.status == EquipmentStatus.MAINTENANCE).count()
    
    total_bookings = db.query(EquipmentBooking).count()
    active_bookings = db.query(EquipmentBooking).filter(
        EquipmentBooking.status.in_([BookingStatus.APPROVED, BookingStatus.ACTIVE])
    ).count()
    pending_approvals = db.query(EquipmentBooking).filter(
        EquipmentBooking.status == BookingStatus.REQUESTED
    ).count()
    
    utilization_rate = (in_use_equipment / total_equipment * 100) if total_equipment > 0 else 0
    
    pending_maintenance = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.completed_date == None
    ).count()
    
    expired_certifications = db.query(OperatorCertification).filter(
        OperatorCertification.expiry_date < datetime.now(),
        OperatorCertification.is_active == True
    ).count()
    
    return {
        "total_equipment": total_equipment,
        "available_equipment": available_equipment,
        "in_use_equipment": in_use_equipment,
        "maintenance_equipment": maintenance_equipment,
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "pending_approvals": pending_approvals,
        "utilization_rate": round(utilization_rate, 2),
        "pending_maintenance": pending_maintenance,
        "expired_certifications": expired_certifications
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
