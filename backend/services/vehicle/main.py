from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path
import os

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


def _should_seed() -> bool:
    return os.getenv("SEED_DATA_ON_STARTUP", "true").strip().lower() in {"1", "true", "yes"}


def _seed_vehicle_data(db: Session) -> None:
    """Seed vehicles and drivers when empty."""
    if db.query(Vehicle).count() == 0:
        vehicles = [
            {
                "registration_number": "DL01AB1234",
                "vehicle_type": VehicleType.CAR,
                "make": "Maruti",
                "model": "Swift",
                "year": 2020,
                "capacity": 4,
                "fuel_type": "Petrol",
                "status": VehicleStatus.AVAILABLE,
                "current_odometer": 15000,
            },
            {
                "registration_number": "DL01CD5678",
                "vehicle_type": VehicleType.CAR,
                "make": "Mahindra",
                "model": "Scorpio",
                "year": 2021,
                "capacity": 7,
                "fuel_type": "Diesel",
                "status": VehicleStatus.AVAILABLE,
                "current_odometer": 25000,
            },
            {
                "registration_number": "DL01EF9012",
                "vehicle_type": VehicleType.BUS,
                "make": "Tata",
                "model": "LP 410",
                "year": 2019,
                "capacity": 30,
                "fuel_type": "Diesel",
                "status": VehicleStatus.IN_USE,
                "current_odometer": 50000,
            },
        ]
        for item in vehicles:
            db.add(Vehicle(**item))
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
    if _should_seed():
        db = next(get_db())
        try:
            _seed_vehicle_data(db)
        finally:
            db.close()

@app.get("/")
async def root():
    return {"service": "Vehicle Requisition", "status": "running", "version": "1.0.0"}

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
    
    requisition = VehicleRequisition(**requisition_data.model_dump(), requisition_number=requisition_number, requester_id=current_user.id)
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
    
    requisition.status = RequisitionStatus.APPROVED
    requisition.vehicle_id = vehicle_id
    requisition.approver_id = current_user.id
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
    feedback = TripFeedback(**feedback_data.model_dump(), submitted_by_id=current_user.id)
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
    total_requisitions = db.query(VehicleRequisition).count()
    pending_approvals = db.query(VehicleRequisition).filter(VehicleRequisition.status == RequisitionStatus.REQUESTED).count()
    active_trips = db.query(Trip).filter(Trip.status == TripStatus.IN_PROGRESS).count()
    
    total_distance = db.query(Trip).filter(Trip.distance_km.isnot(None))
    total_distance_km = sum([t.distance_km for t in total_distance.all()])
    
    drivers = db.query(Driver).filter(Driver.rating > 0).all()
    avg_driver_rating = sum([d.rating for d in drivers]) / len(drivers) if drivers else 0
    
    return {
        "total_vehicles": total_vehicles,
        "available_vehicles": available_vehicles,
        "in_use_vehicles": in_use_vehicles,
        "total_requisitions": total_requisitions,
        "pending_approvals": pending_approvals,
        "active_trips": active_trips,
        "total_distance_km": round(total_distance_km, 2),
        "avg_driver_rating": round(avg_driver_rating, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
