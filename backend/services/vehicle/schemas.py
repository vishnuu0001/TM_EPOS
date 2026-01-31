from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class VehicleType(str, Enum):
    CAR = "CAR"
    BUS = "BUS"
    TRUCK = "TRUCK"
    AMBULANCE = "AMBULANCE"
    UTILITY = "UTILITY"

class VehicleStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"

class RequisitionStatus(str, Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class TripStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

# Vehicle Schemas
class VehicleBase(BaseModel):
    registration_number: str = Field(..., min_length=1, max_length=50)
    vehicle_type: VehicleType
    make: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    capacity: Optional[int] = Field(None, ge=1)
    fuel_type: Optional[str] = Field(None, min_length=1, max_length=50)

class VehicleCreate(VehicleBase):
    pass

class VehicleResponse(VehicleBase):
    id: str
    status: VehicleStatus
    current_odometer: float
    created_at: datetime

    class Config:
        from_attributes = True

# Driver Schemas
class DriverBase(BaseModel):
    license_number: str = Field(..., min_length=1, max_length=100)
    license_expiry: datetime
    license_type: Optional[str] = Field(None, min_length=1, max_length=50)

class DriverCreate(DriverBase):
    user_id: str = Field(..., min_length=1)

class DriverResponse(DriverBase):
    id: str
    user_id: str
    is_active: bool
    rating: float
    total_trips: int
    created_at: datetime

    class Config:
        from_attributes = True

# Requisition Schemas
class RequisitionBase(BaseModel):
    purpose: str = Field(..., min_length=1, max_length=200)
    destination: str = Field(..., min_length=1, max_length=200)
    departure_date: datetime
    return_date: Optional[datetime] = None
    number_of_passengers: int = Field(1, ge=1)
    cost_center: Optional[str] = Field(None, min_length=1, max_length=100)
    notes: Optional[str] = Field(None, min_length=1)

    @validator("return_date")
    def validate_return_date(cls, value, values):
        departure_date = values.get("departure_date")
        if value and departure_date and value < departure_date:
            raise ValueError("return_date must be on or after departure_date")
        return value

class RequisitionCreate(RequisitionBase):
    pass

class RequisitionResponse(RequisitionBase):
    id: str
    requisition_number: str
    requester_id: str
    vehicle_id: Optional[str] = None
    status: RequisitionStatus
    approver_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Trip Schemas
class TripBase(BaseModel):
    driver_id: str = Field(..., min_length=1)

class TripCreate(TripBase):
    requisition_id: str = Field(..., min_length=1)

class TripUpdate(BaseModel):
    start_odometer: Optional[float] = Field(None, ge=0)
    end_odometer: Optional[float] = Field(None, ge=0)
    status: Optional[TripStatus] = None

class TripResponse(TripBase):
    id: str
    requisition_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    start_odometer: Optional[float] = None
    end_odometer: Optional[float] = None
    distance_km: Optional[float] = None
    status: TripStatus
    created_at: datetime

    class Config:
        from_attributes = True

# Fuel Log Schemas
class FuelLogBase(BaseModel):
    fuel_quantity: float = Field(..., ge=0)
    fuel_cost: float = Field(..., ge=0)
    odometer_reading: float = Field(..., ge=0)
    fuel_station: Optional[str] = Field(None, min_length=1, max_length=200)
    receipt_number: Optional[str] = Field(None, min_length=1, max_length=100)

class FuelLogCreate(FuelLogBase):
    trip_id: str = Field(..., min_length=1)

class FuelLogResponse(FuelLogBase):
    id: str
    trip_id: str
    filled_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Feedback Schemas
class FeedbackBase(BaseModel):
    driver_rating: int = Field(..., ge=1, le=5)
    vehicle_rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, min_length=1)

class FeedbackCreate(FeedbackBase):
    trip_id: str = Field(..., min_length=1)

class FeedbackResponse(FeedbackBase):
    id: str
    trip_id: str
    submitted_by_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard Stats
class DashboardStats(BaseModel):
    total_vehicles: int
    available_vehicles: int
    in_use_vehicles: int
    maintenance_vehicles: int
    total_requisitions: int
    pending_approvals: int
    pending_requisitions: int
    approved_requisitions: int
    active_trips: int
    total_distance_km: float
    total_km_today: float
    fuel_cost_today: float
    avg_driver_rating: float
