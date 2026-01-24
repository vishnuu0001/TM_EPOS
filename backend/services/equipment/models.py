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

class EquipmentType(str, enum.Enum):
    CRANE = "CRANE"
    FORKLIFT = "FORKLIFT"
    EXCAVATOR = "EXCAVATOR"
    LOADER = "LOADER"
    TRUCK = "TRUCK"
    GENERATOR = "GENERATOR"
    OTHER = "OTHER"

class EquipmentStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"

class BookingStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    equipment_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    equipment_type = Column(Enum(EquipmentType), nullable=False)
    manufacturer = Column(String(200))
    model = Column(String(100))
    capacity = Column(String(100))
    location = Column(String(200))
    status = Column(Enum(EquipmentStatus), default=EquipmentStatus.AVAILABLE)
    hourly_rate = Column(Float)
    requires_certification = Column(Boolean, default=True)
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = relationship("EquipmentBooking", back_populates="equipment")
    maintenance_logs = relationship("MaintenanceSchedule", back_populates="equipment")


class OperatorCertification(Base):
    __tablename__ = "operator_certifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    operator_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    equipment_type = Column(Enum(EquipmentType), nullable=False)
    certification_number = Column(String(100), unique=True, nullable=False)
    issued_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    issuing_authority = Column(String(200))
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EquipmentBooking(Base):
    __tablename__ = "equipment_bookings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_number = Column(String(50), unique=True, nullable=False, index=True)
    equipment_id = Column(String(36), ForeignKey("equipment.id"), nullable=False)
    operator_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    actual_start_time = Column(DateTime)
    actual_end_time = Column(DateTime)
    
    purpose = Column(Text, nullable=False)
    location = Column(String(200))
    cost_center = Column(String(100))
    
    status = Column(Enum(BookingStatus), default=BookingStatus.REQUESTED)
    
    requested_by_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(String(36), ForeignKey("users.id"))
    
    safety_permit_id = Column(String(36), ForeignKey("safety_permits.id"))
    
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="bookings")
    usage_log = relationship("UsageLog", back_populates="booking", uselist=False)
    safety_permit = relationship("SafetyPermit", back_populates="booking")


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("equipment_bookings.id"), nullable=False, unique=True)
    
    actual_hours = Column(Float)
    fuel_consumed = Column(Float)
    fuel_type = Column(String(50))
    start_reading = Column(Float)  # Hour meter or odometer
    end_reading = Column(Float)
    
    issues_reported = Column(Text)
    operator_remarks = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("EquipmentBooking", back_populates="usage_log")


class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    equipment_id = Column(String(36), ForeignKey("equipment.id"), nullable=False)
    
    maintenance_type = Column(String(100), nullable=False)  # Preventive, Corrective, Inspection
    description = Column(Text)
    
    scheduled_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime)
    
    next_service_hours = Column(Float)  # Hours of operation
    next_service_date = Column(DateTime)
    
    performed_by = Column(String(200))
    cost = Column(Float)
    
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="maintenance_logs")


class SafetyPermit(Base):
    __tablename__ = "safety_permits"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    permit_number = Column(String(50), unique=True, nullable=False)
    
    checklist = Column(Text, nullable=False)  # JSON string of safety checks
    all_checks_passed = Column(Boolean, default=False)
    
    issued_by_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=False)
    
    remarks = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("EquipmentBooking", back_populates="safety_permit")
