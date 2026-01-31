from pydantic import BaseModel, EmailStr, Field, validator
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
    room_number: str = Field(..., min_length=1, max_length=50)
    room_type: RoomType
    floor: int = Field(..., ge=0)
    capacity: int = Field(..., ge=1)
    amenities: Optional[str] = Field(None, min_length=1)
    rate_per_night: float = Field(..., ge=0)
    description: Optional[str] = Field(None, min_length=1)

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    room_type: Optional[RoomType] = None
    capacity: Optional[int] = Field(None, ge=1)
    amenities: Optional[str] = Field(None, min_length=1)
    rate_per_night: Optional[float] = Field(None, ge=0)
    status: Optional[RoomStatus] = None
    description: Optional[str] = Field(None, min_length=1)

class RoomResponse(RoomBase):
    id: str
    status: RoomStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Booking Schemas
class BookingBase(BaseModel):
    guest_name: str = Field(..., min_length=1, max_length=200)
    guest_phone: str = Field(..., min_length=1, max_length=20)
    guest_email: Optional[EmailStr] = None
    guest_company: Optional[str] = Field(None, min_length=1, max_length=200)
    guest_id_proof: Optional[str] = Field(None, min_length=1, max_length=200)
    check_in_date: datetime
    check_out_date: datetime
    number_of_guests: int = Field(1, ge=1)
    cost_center: str = Field(..., min_length=1, max_length=100)
    purpose: Optional[str] = Field(None, min_length=1)
    special_requests: Optional[str] = Field(None, min_length=1)

    @validator("check_out_date")
    def validate_check_out_date(cls, value, values):
        check_in = values.get("check_in_date")
        if check_in and value <= check_in:
            raise ValueError("check_out_date must be after check_in_date")
        return value

class BookingCreate(BookingBase):
    room_id: str

class BookingUpdate(BaseModel):
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    number_of_guests: Optional[int] = Field(None, ge=1)
    status: Optional[BookingStatus] = None
    special_requests: Optional[str] = Field(None, min_length=1)
    notes: Optional[str] = Field(None, min_length=1)

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
    booking_id: str = Field(..., min_length=1)
    actual_check_in: Optional[datetime] = None

class CheckOutRequest(BaseModel):
    booking_id: str = Field(..., min_length=1)
    actual_check_out: Optional[datetime] = None
    room_condition_notes: Optional[str] = Field(None, min_length=1)

# Billing Schemas
class BillingBase(BaseModel):
    room_charges: float = Field(0.0, ge=0)
    meal_charges: float = Field(0.0, ge=0)
    extra_service_charges: float = Field(0.0, ge=0)
    tax_amount: float = Field(0.0, ge=0)
    discount: float = Field(0.0, ge=0)

class BillingCreate(BillingBase):
    booking_id: str = Field(..., min_length=1)

class BillingUpdate(BaseModel):
    meal_charges: Optional[float] = Field(None, ge=0)
    extra_service_charges: Optional[float] = Field(None, ge=0)
    discount: Optional[float] = Field(None, ge=0)
    paid: Optional[bool] = None
    payment_method: Optional[str] = Field(None, min_length=1, max_length=50)
    transaction_id: Optional[str] = Field(None, min_length=1, max_length=100)

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
    task_type: str = Field(..., min_length=1, max_length=100)
    task_description: Optional[str] = Field(None, min_length=1)

class HousekeepingCreate(HousekeepingBase):
    room_id: str = Field(..., min_length=1)

class HousekeepingUpdate(BaseModel):
    assigned_to_id: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, min_length=1, max_length=50)
    remarks: Optional[str] = Field(None, min_length=1)

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
    pending_bookings: int
    checked_in_guests: int
    checked_in_today: int
    checking_out_today: int
    occupancy_rate: float
    pending_housekeeping: int
    revenue_today: float
    revenue_month: float

# Availability Response
class AvailabilityResponse(BaseModel):
    available_rooms: List[RoomResponse]
    check_in_date: datetime
    check_out_date: datetime
