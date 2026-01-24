from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class RoomType(str, enum.Enum):
    SINGLE = "single"
    DOUBLE = "double"
    SUITE = "suite"
    DORMITORY = "dormitory"

class RoomStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"

class Room(Base):
    __tablename__ = "guesthouse_rooms"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    room_number = Column(String(10), unique=True, nullable=False, index=True)
    room_type = Column(SQLEnum(RoomType), nullable=False)
    floor = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    amenities = Column(Text)  # JSON string: AC, TV, WiFi, etc.
    rate_per_night = Column(Float, nullable=False)
    status = Column(SQLEnum(RoomStatus), default=RoomStatus.AVAILABLE, nullable=False)
    description = Column(Text)
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = relationship("Booking", back_populates="room")
    housekeeping_tasks = relationship("Housekeeping", back_populates="room")


class Booking(Base):
    __tablename__ = "guesthouse_bookings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_number = Column(String(50), unique=True, nullable=False, index=True)
    
    room_id = Column(String(36), ForeignKey("guesthouse_rooms.id"), nullable=False)
    guest_name = Column(String(200), nullable=False)
    guest_phone = Column(String(20), nullable=False)
    guest_email = Column(String(100))
    guest_company = Column(String(200))
    guest_id_proof = Column(String(100))  # ID proof number
    
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    actual_check_in = Column(DateTime)
    actual_check_out = Column(DateTime)
    
    number_of_guests = Column(Integer, default=1)
    cost_center = Column(String(100), nullable=False)
    purpose = Column(Text)
    
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.CONFIRMED)
    
    booked_by_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(String(36), ForeignKey("users.id"))
    
    special_requests = Column(Text)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    room = relationship("Room", back_populates="bookings")
    billing = relationship("Billing", back_populates="booking", uselist=False)


class Billing(Base):
    __tablename__ = "guesthouse_billing"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("guesthouse_bookings.id"), nullable=False, unique=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    
    room_charges = Column(Float, default=0.0)
    meal_charges = Column(Float, default=0.0)
    extra_service_charges = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    paid = Column(Boolean, default=False)
    payment_date = Column(DateTime)
    payment_method = Column(String(50))
    transaction_id = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    booking = relationship("Booking", back_populates="billing")


class Housekeeping(Base):
    __tablename__ = "guesthouse_housekeeping"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    room_id = Column(String(36), ForeignKey("guesthouse_rooms.id"), nullable=False)
    
    task_type = Column(String(100), nullable=False)  # Cleaning, Maintenance, Inspection
    task_description = Column(Text)
    
    assigned_to_id = Column(String(36), ForeignKey("users.id"))
    assigned_at = Column(DateTime)
    
    status = Column(String(20), default="pending")  # pending, in_progress, completed
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    remarks = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    room = relationship("Room", back_populates="housekeeping_tasks")
