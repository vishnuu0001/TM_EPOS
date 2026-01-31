from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
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

from models import Base, Vehicle, Driver, VehicleRequisition, Trip, FuelLog, TripFeedback, RequisitionStatus, TripStatus, VehicleStatus, VehicleType
from schemas import (
    VehicleCreate, VehicleResponse,
    DriverCreate, DriverResponse,
    RequisitionCreate, RequisitionResponse,
    TripCreate, TripUpdate, TripResponse,
    FuelLogCreate, FuelLogResponse,
    FeedbackCreate, FeedbackResponse,
    DashboardStats
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vehicle Requisition Service", version="1.0.0")
setup_middleware(app)


def _get_user_id(current_user: User) -> str:
    if isinstance(current_user, dict):
        return current_user.get("id")
    return getattr(current_user, "id", None)


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


def _seed_vehicle_data(db: Session) -> None:
    """Seed vehicles and drivers up to target count."""
    target = int(os.getenv("SEED_VEHICLE_COUNT", "1000"))
    existing = db.query(Vehicle).count()
    if existing < target:
        base_index = existing + 1
        type_cycle = [VehicleType.CAR, VehicleType.BUS, VehicleType.TRUCK, VehicleType.UTILITY, VehicleType.AMBULANCE]
        for i in range(base_index, target + 1):
            v_type = type_cycle[i % len(type_cycle)]
            db.add(
                Vehicle(
                    registration_number=f"DL99AA{i:04d}",
                    vehicle_type=v_type,
                    make="AutoGen",
                    model=f"Model-{i % 100}",
                    year=2019 + (i % 6),
                    capacity=4 if v_type == VehicleType.CAR else 30,
                    fuel_type="Diesel" if i % 2 == 0 else "Petrol",
                    status=VehicleStatus.AVAILABLE,
                    current_odometer=10000 + i * 3,
                )
            )
        db.commit()

    if db.query(Driver).count() == 0:
        drivers = [
            {
                "user_id": "00000000-0000-0000-0000-000000000001",
                "license_number": "DL123456",
                "license_expiry": datetime.utcnow() + timedelta(days=365),
                "license_type": "Light Motor Vehicle",
                "is_active": True,
                "rating": 4.2,
            },
            {
                "user_id": "00000000-0000-0000-0000-000000000002",
                "license_number": "DL789012",
                "license_expiry": datetime.utcnow() + timedelta(days=365),
                "license_type": "Heavy Motor Vehicle",
                "is_active": True,
                "rating": 4.0,
            },
        ]
        for item in drivers:
            db.add(Driver(**item))
        db.commit()


@app.on_event("startup")
async def startup_event():
    if _should_seed() and _should_seed_first_boot("vehicle"):
        db = next(get_db())
        try:
            _seed_vehicle_data(db)
            _mark_seeded("vehicle")
        finally:
            db.close()

@app.get("/")
async def root():
    return {"service": "Vehicle Requisition", "status": "running", "version": "1.0.0"}


@app.post("/admin/seed")
async def seed_vehicle_data(request: Request, current_user: User = Depends(get_current_user)):
    _require_seed_token(request)
    db = next(get_db())
    try:
        _seed_vehicle_data(db)
        return {"seeded": True}
    finally:
        db.close()

# Vehicles
@app.post("/vehicles", response_model=VehicleResponse)
async def create_vehicle(vehicle_data: VehicleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    vehicle = Vehicle(**vehicle_data.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle

@app.get("/vehicles", response_model=List[VehicleResponse])
async def list_vehicles(status: Optional[VehicleStatus] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Vehicle)
    if status:
        query = query.filter(Vehicle.status == status)
    return query.offset(skip).limit(limit).all()

# Drivers
@app.post("/drivers", response_model=DriverResponse)
async def create_driver(driver_data: DriverCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    driver = Driver(**driver_data.model_dump())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver

@app.get("/drivers", response_model=List[DriverResponse])
async def list_drivers(active_only: bool = True, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Driver)
    if active_only:
        query = query.filter(Driver.is_active == True)
    return query.all()

# Requisitions
@app.post("/requisitions", response_model=RequisitionResponse)
async def create_requisition(requisition_data: RequisitionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    year = datetime.now().year
    count = db.query(VehicleRequisition).filter(VehicleRequisition.requisition_number.like(f"VR{year}%")).count()
    requisition_number = f"VR{year}{count + 1:06d}"

    requester_id = _get_user_id(current_user)
    if not requester_id:
        raise HTTPException(status_code=401, detail="Invalid user")

    requisition = VehicleRequisition(
        **requisition_data.model_dump(),
        requisition_number=requisition_number,
        requester_id=requester_id,
    )
    db.add(requisition)
    db.commit()
    db.refresh(requisition)
    return requisition

@app.get("/requisitions", response_model=List[RequisitionResponse])
async def list_requisitions(status: Optional[RequisitionStatus] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(VehicleRequisition)
    if status:
        query = query.filter(VehicleRequisition.status == status)
    return query.order_by(VehicleRequisition.departure_date.desc()).offset(skip).limit(limit).all()

@app.post("/requisitions/{requisition_id}/approve")
async def approve_requisition(requisition_id: str, vehicle_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    requisition = db.query(VehicleRequisition).filter(VehicleRequisition.id == requisition_id).first()
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    approver_id = _get_user_id(current_user)
    if not approver_id:
        raise HTTPException(status_code=401, detail="Invalid user")

    requisition.status = RequisitionStatus.APPROVED
    requisition.vehicle_id = vehicle_id
    requisition.approver_id = approver_id
    requisition.approved_at = datetime.now()
    db.commit()
    return {"message": "Requisition approved", "requisition_id": requisition_id}

# Trips
@app.post("/trips", response_model=TripResponse)
async def create_trip(trip_data: TripCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    trip = Trip(**trip_data.model_dump())
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip

@app.put("/trips/{trip_id}/start")
async def start_trip(trip_id: str, start_odometer: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    trip.start_time = datetime.now()
    trip.start_odometer = start_odometer
    trip.status = TripStatus.IN_PROGRESS
    
    requisition = db.query(VehicleRequisition).filter(VehicleRequisition.id == trip.requisition_id).first()
    vehicle = db.query(Vehicle).filter(Vehicle.id == requisition.vehicle_id).first()
    vehicle.status = VehicleStatus.IN_USE
    
    db.commit()
    return {"message": "Trip started", "trip_id": trip_id}

@app.put("/trips/{trip_id}/end")
async def end_trip(trip_id: str, end_odometer: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    trip.end_time = datetime.now()
    trip.end_odometer = end_odometer
    trip.distance_km = end_odometer - trip.start_odometer
    trip.status = TripStatus.COMPLETED
    
    requisition = db.query(VehicleRequisition).filter(VehicleRequisition.id == trip.requisition_id).first()
    requisition.status = RequisitionStatus.COMPLETED
    vehicle = db.query(Vehicle).filter(Vehicle.id == requisition.vehicle_id).first()
    vehicle.status = VehicleStatus.AVAILABLE
    vehicle.current_odometer = end_odometer
    
    driver = db.query(Driver).filter(Driver.id == trip.driver_id).first()
    driver.total_trips += 1
    
    db.commit()
    return {"message": "Trip completed", "trip_id": trip_id, "distance_km": trip.distance_km}

# Fuel Logs
@app.post("/fuel-logs", response_model=FuelLogResponse)
async def create_fuel_log(log_data: FuelLogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fuel_log = FuelLog(**log_data.model_dump())
    db.add(fuel_log)
    db.commit()
    db.refresh(fuel_log)
    return fuel_log

# Feedback
@app.post("/feedback", response_model=FeedbackResponse)
async def create_feedback(feedback_data: FeedbackCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    submitted_by_id = _get_user_id(current_user)
    if not submitted_by_id:
        raise HTTPException(status_code=401, detail="Invalid user")

    feedback = TripFeedback(**feedback_data.model_dump(), submitted_by_id=submitted_by_id)
    db.add(feedback)
    
    # Update driver rating
    trip = db.query(Trip).filter(Trip.id == feedback_data.trip_id).first()
    driver = db.query(Driver).filter(Driver.id == trip.driver_id).first()
    
    all_feedback = db.query(TripFeedback).join(Trip).filter(Trip.driver_id == driver.id).all()
    total_ratings = sum([f.driver_rating for f in all_feedback]) + feedback_data.driver_rating
    driver.rating = total_ratings / (len(all_feedback) + 1)
    
    db.commit()
    db.refresh(feedback)
    return feedback

# Dashboard Stats
@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_vehicles = db.query(Vehicle).count()
    available_vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.AVAILABLE).count()
    in_use_vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.IN_USE).count()
    maintenance_vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.MAINTENANCE).count()
    total_requisitions = db.query(VehicleRequisition).count()
    pending_approvals = db.query(VehicleRequisition).filter(VehicleRequisition.status == RequisitionStatus.REQUESTED).count()
    pending_requisitions = db.query(VehicleRequisition).filter(VehicleRequisition.status == RequisitionStatus.REQUESTED).count()
    approved_requisitions = db.query(VehicleRequisition).filter(VehicleRequisition.status == RequisitionStatus.APPROVED).count()
    active_trips = db.query(Trip).filter(Trip.status == TripStatus.IN_PROGRESS).count()
    
    total_distance = db.query(Trip).filter(Trip.distance_km.isnot(None))
    total_distance_km = sum([t.distance_km for t in total_distance.all()])

    today = datetime.utcnow().date()
    total_km_today = db.query(func.sum(Trip.distance_km)).filter(
        Trip.distance_km.isnot(None),
        func.date(Trip.start_time) == today
    ).scalar() or 0

    fuel_cost_today = db.query(func.sum(FuelLog.fuel_cost)).filter(
        func.date(FuelLog.filled_at) == today
    ).scalar() or 0
    
    drivers = db.query(Driver).filter(Driver.rating > 0).all()
    avg_driver_rating = sum([d.rating for d in drivers]) / len(drivers) if drivers else 0
    
    return {
        "total_vehicles": total_vehicles,
        "available_vehicles": available_vehicles,
        "in_use_vehicles": in_use_vehicles,
        "maintenance_vehicles": maintenance_vehicles,
        "total_requisitions": total_requisitions,
        "pending_approvals": pending_approvals,
        "pending_requisitions": pending_requisitions,
        "approved_requisitions": approved_requisitions,
        "active_trips": active_trips,
        "total_distance_km": round(total_distance_km, 2),
        "total_km_today": round(total_km_today, 2),
        "fuel_cost_today": round(fuel_cost_today, 2),
        "avg_driver_rating": round(avg_driver_rating, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
