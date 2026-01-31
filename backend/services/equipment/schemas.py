from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class EquipmentType(str, Enum):
    CRANE = "CRANE"
    FORKLIFT = "FORKLIFT"
    EXCAVATOR = "EXCAVATOR"
    LOADER = "LOADER"
    TRUCK = "TRUCK"
    GENERATOR = "GENERATOR"
    OTHER = "OTHER"

class EquipmentStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"

class BookingStatus(str, Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

# Equipment Schemas
class EquipmentBase(BaseModel):
    equipment_number: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    equipment_type: EquipmentType
    manufacturer: Optional[str] = Field(None, min_length=1, max_length=200)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    capacity: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    hourly_rate: Optional[float] = Field(None, ge=0)
    requires_certification: bool = True
    description: Optional[str] = Field(None, min_length=1)

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[EquipmentStatus] = None
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    hourly_rate: Optional[float] = Field(None, ge=0)
    description: Optional[str] = Field(None, min_length=1)

class EquipmentResponse(EquipmentBase):
    id: str
    status: EquipmentStatus
    created_at: datetime

    class Config:
        from_attributes = True

# Operator Certification Schemas
class CertificationBase(BaseModel):
    equipment_type: EquipmentType
    certification_number: str = Field(..., min_length=1, max_length=100)
    issued_date: datetime
    expiry_date: datetime
    issuing_authority: Optional[str] = Field(None, min_length=1, max_length=200)

class CertificationCreate(CertificationBase):
    operator_id: str = Field(..., min_length=1)

class CertificationResponse(CertificationBase):
    id: str
    operator_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Booking Schemas
class BookingBase(BaseModel):
    equipment_id: str = Field(..., min_length=1)
    operator_id: str = Field(..., min_length=1)
    start_time: datetime
    end_time: datetime
    purpose: str = Field(..., min_length=1, max_length=200)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    cost_center: Optional[str] = Field(None, min_length=1, max_length=100)

    @validator("end_time")
    def validate_end_time(cls, value, values):
        start_time = values.get("start_time")
        if start_time and value <= start_time:
            raise ValueError("end_time must be after start_time")
        return value

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[BookingStatus] = None
    notes: Optional[str] = Field(None, min_length=1)

class BookingResponse(BookingBase):
    id: str
    booking_number: str
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    status: BookingStatus
    requested_by_id: str
    approved_by_id: Optional[str] = None
    safety_permit_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Usage Log Schemas
class UsageLogBase(BaseModel):
    actual_hours: Optional[float] = Field(None, ge=0)
    fuel_consumed: Optional[float] = Field(None, ge=0)
    fuel_type: Optional[str] = Field(None, min_length=1, max_length=50)
    start_reading: Optional[float] = Field(None, ge=0)
    end_reading: Optional[float] = Field(None, ge=0)
    issues_reported: Optional[str] = Field(None, min_length=1)
    operator_remarks: Optional[str] = Field(None, min_length=1)

class UsageLogCreate(UsageLogBase):
    booking_id: str = Field(..., min_length=1)

class UsageLogResponse(UsageLogBase):
    id: str
    booking_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Maintenance Schemas
class MaintenanceBase(BaseModel):
    maintenance_type: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    scheduled_date: datetime
    next_service_hours: Optional[float] = Field(None, ge=0)
    next_service_date: Optional[datetime] = None

class MaintenanceCreate(MaintenanceBase):
    equipment_id: str = Field(..., min_length=1)

class MaintenanceUpdate(BaseModel):
    completed_date: Optional[datetime] = None
    performed_by: Optional[str] = Field(None, min_length=1, max_length=200)
    cost: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, min_length=1)

class MaintenanceResponse(MaintenanceBase):
    id: str
    equipment_id: str
    completed_date: Optional[datetime] = None
    performed_by: Optional[str] = None
    cost: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Safety Permit Schemas
class SafetyPermitBase(BaseModel):
    checklist: str = Field(..., min_length=1)
    all_checks_passed: bool
    valid_until: datetime
    remarks: Optional[str] = Field(None, min_length=1)

class SafetyPermitCreate(SafetyPermitBase):
    pass

class SafetyPermitResponse(SafetyPermitBase):
    id: str
    permit_number: str
    issued_by_id: str
    issued_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard Stats
class DashboardStats(BaseModel):
    total_equipment: int
    available_equipment: int
    in_use_equipment: int
    maintenance_equipment: int
    total_bookings: int
    active_bookings: int
    pending_approvals: int
    utilization_rate: float
    pending_maintenance: int
    expired_certifications: int
