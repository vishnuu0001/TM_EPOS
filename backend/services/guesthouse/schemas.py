from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class RoomType(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"
    SUITE = "suite"
    DORMITORY = "dormitory"

class RoomStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"

# Room Schemas
class RoomBase(BaseModel):
    room_number: str
    room_type: RoomType
    floor: int
    capacity: int
    amenities: Optional[str] = None
    rate_per_night: float
    description: Optional[str] = None

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    room_type: Optional[RoomType] = None
    capacity: Optional[int] = None
    amenities: Optional[str] = None
    rate_per_night: Optional[float] = None
    status: Optional[RoomStatus] = None
    description: Optional[str] = None

class RoomResponse(RoomBase):
    id: str
    status: RoomStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Booking Schemas
class BookingBase(BaseModel):
    guest_name: str
    guest_phone: str
    guest_email: Optional[EmailStr] = None
    guest_company: Optional[str] = None
    guest_id_proof: Optional[str] = None
    check_in_date: datetime
    check_out_date: datetime
    number_of_guests: int = 1
    cost_center: str
    purpose: Optional[str] = None
    special_requests: Optional[str] = None

class BookingCreate(BookingBase):
    room_id: str

class BookingUpdate(BaseModel):
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    number_of_guests: Optional[int] = None
    status: Optional[BookingStatus] = None
    special_requests: Optional[str] = None
    notes: Optional[str] = None

class BookingResponse(BookingBase):
    id: str
    booking_number: str
    room_id: str
    actual_check_in: Optional[datetime] = None
    actual_check_out: Optional[datetime] = None
    status: BookingStatus
    booked_by_id: str
    approved_by_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Check-in/Check-out Schemas
class CheckInRequest(BaseModel):
    booking_id: str
    actual_check_in: Optional[datetime] = None

class CheckOutRequest(BaseModel):
    booking_id: str
    actual_check_out: Optional[datetime] = None
    room_condition_notes: Optional[str] = None

# Billing Schemas
class BillingBase(BaseModel):
    room_charges: float = 0.0
    meal_charges: float = 0.0
    extra_service_charges: float = 0.0
    tax_amount: float = 0.0
    discount: float = 0.0

class BillingCreate(BillingBase):
    booking_id: str

class BillingUpdate(BaseModel):
    meal_charges: Optional[float] = None
    extra_service_charges: Optional[float] = None
    discount: Optional[float] = None
    paid: Optional[bool] = None
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None

class BillingResponse(BillingBase):
    id: str
    booking_id: str
    invoice_number: str
    total_amount: float
    paid: bool
    payment_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Housekeeping Schemas
class HousekeepingBase(BaseModel):
    task_type: str
    task_description: Optional[str] = None

class HousekeepingCreate(HousekeepingBase):
    room_id: str

class HousekeepingUpdate(BaseModel):
    assigned_to_id: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None

class HousekeepingResponse(HousekeepingBase):
    id: str
    room_id: str
    assigned_to_id: Optional[str] = None
    status: str
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    remarks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard Stats
class DashboardStats(BaseModel):
    total_rooms: int
    available_rooms: int
    occupied_rooms: int
    maintenance_rooms: int
    total_bookings: int
    active_bookings: int
    checked_in_today: int
    checking_out_today: int
    occupancy_rate: float
    pending_housekeeping: int

# Availability Response
class AvailabilityResponse(BaseModel):
    available_rooms: List[RoomResponse]
    check_in_date: datetime
    check_out_date: datetime
