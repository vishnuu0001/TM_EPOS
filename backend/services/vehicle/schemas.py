from pydantic import BaseModel
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
    registration_number: str
    vehicle_type: VehicleType
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    capacity: Optional[int] = None
    fuel_type: Optional[str] = None

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
    license_number: str
    license_expiry: datetime
    license_type: Optional[str] = None

class DriverCreate(DriverBase):
    user_id: str

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
    purpose: str
    destination: str
    departure_date: datetime
    return_date: Optional[datetime] = None
    number_of_passengers: int = 1
    cost_center: Optional[str] = None
    notes: Optional[str] = None

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
    driver_id: str

class TripCreate(TripBase):
    requisition_id: str

class TripUpdate(BaseModel):
    start_odometer: Optional[float] = None
    end_odometer: Optional[float] = None
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
    fuel_quantity: float
    fuel_cost: float
    odometer_reading: float
    fuel_station: Optional[str] = None
    receipt_number: Optional[str] = None

class FuelLogCreate(FuelLogBase):
    trip_id: str

class FuelLogResponse(FuelLogBase):
    id: str
    trip_id: str
    filled_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Feedback Schemas
class FeedbackBase(BaseModel):
    driver_rating: int
    vehicle_rating: int
    comments: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    trip_id: str

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
    total_requisitions: int
    pending_approvals: int
    active_trips: int
    total_distance_km: float
    avg_driver_rating: float
