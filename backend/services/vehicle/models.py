import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
import enum

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class VehicleType(str, enum.Enum):
    CAR = "CAR"
    BUS = "BUS"
    TRUCK = "TRUCK"
    AMBULANCE = "AMBULANCE"
    UTILITY = "UTILITY"

class VehicleStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"

class RequisitionStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class TripStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    registration_number = Column(String(50), unique=True, nullable=False, index=True)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    make = Column(String(100))
    model = Column(String(100))
    year = Column(Integer)
    capacity = Column(Integer)
    fuel_type = Column(String(50))
    status = Column(Enum(VehicleStatus), default=VehicleStatus.AVAILABLE)
    current_odometer = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requisitions = relationship("VehicleRequisition", back_populates="vehicle")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)
    license_number = Column(String(50), unique=True, nullable=False)
    license_expiry = Column(DateTime, nullable=False)
    license_type = Column(String(50))
    is_active = Column(Boolean, default=True)
    rating = Column(Float, default=0.0)
    total_trips = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trips = relationship("Trip", back_populates="driver")


class VehicleRequisition(Base):
    __tablename__ = "vehicle_requisitions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    requisition_number = Column(String(50), unique=True, nullable=False, index=True)
    
    requester_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(String(36), ForeignKey("vehicles.id"))
    
    purpose = Column(Text, nullable=False)
    destination = Column(String(200), nullable=False)
    departure_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime)
    number_of_passengers = Column(Integer, default=1)
    
    cost_center = Column(String(100))
    
    status = Column(Enum(RequisitionStatus), default=RequisitionStatus.REQUESTED)
    
    approver_id = Column(String(36), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="requisitions")
    trip = relationship("Trip", back_populates="requisition", uselist=False)


class Trip(Base):
    __tablename__ = "trips"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    requisition_id = Column(String(36), ForeignKey("vehicle_requisitions.id"), nullable=False, unique=True)
    driver_id = Column(String(36), ForeignKey("drivers.id"), nullable=False)
    
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    start_odometer = Column(Float)
    end_odometer = Column(Float)
    distance_km = Column(Float)
    
    gps_tracking_id = Column(String(100))  # Placeholder for GPS integration
    
    status = Column(Enum(TripStatus), default=TripStatus.SCHEDULED)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requisition = relationship("VehicleRequisition", back_populates="trip")
    driver = relationship("Driver", back_populates="trips")
    fuel_logs = relationship("FuelLog", back_populates="trip")
    feedback = relationship("TripFeedback", back_populates="trip", uselist=False)


class FuelLog(Base):
    __tablename__ = "fuel_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False)
    
    fuel_quantity = Column(Float, nullable=False)
    fuel_cost = Column(Float, nullable=False)
    odometer_reading = Column(Float, nullable=False)
    fuel_station = Column(String(200))
    receipt_number = Column(String(100))
    
    filled_at = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="fuel_logs")


class TripFeedback(Base):
    __tablename__ = "trip_feedback"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False, unique=True)
    
    driver_rating = Column(Integer)  # 1-5
    vehicle_rating = Column(Integer)  # 1-5
    comments = Column(Text)
    
    submitted_by_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="feedback")
