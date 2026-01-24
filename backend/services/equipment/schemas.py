from pydantic import BaseModel, Field
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
    equipment_number: str
    name: str
    equipment_type: EquipmentType
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    capacity: Optional[str] = None
    location: Optional[str] = None
    hourly_rate: Optional[float] = None
    requires_certification: bool = True
    description: Optional[str] = None

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[EquipmentStatus] = None
    location: Optional[str] = None
    hourly_rate: Optional[float] = None
    description: Optional[str] = None

class EquipmentResponse(EquipmentBase):
    id: str
    status: EquipmentStatus
    created_at: datetime

    class Config:
        from_attributes = True

# Operator Certification Schemas
class CertificationBase(BaseModel):
    equipment_type: EquipmentType
    certification_number: str
    issued_date: datetime
    expiry_date: datetime
    issuing_authority: Optional[str] = None

class CertificationCreate(CertificationBase):
    operator_id: str

class CertificationResponse(CertificationBase):
    id: str
    operator_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Booking Schemas
class BookingBase(BaseModel):
    equipment_id: str
    operator_id: str
    start_time: datetime
    end_time: datetime
    purpose: str
    location: Optional[str] = None
    cost_center: Optional[str] = None

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[BookingStatus] = None
    notes: Optional[str] = None

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
    actual_hours: Optional[float] = None
    fuel_consumed: Optional[float] = None
    fuel_type: Optional[str] = None
    start_reading: Optional[float] = None
    end_reading: Optional[float] = None
    issues_reported: Optional[str] = None
    operator_remarks: Optional[str] = None

class UsageLogCreate(UsageLogBase):
    booking_id: str

class UsageLogResponse(UsageLogBase):
    id: str
    booking_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Maintenance Schemas
class MaintenanceBase(BaseModel):
    maintenance_type: str
    description: Optional[str] = None
    scheduled_date: datetime
    next_service_hours: Optional[float] = None
    next_service_date: Optional[datetime] = None

class MaintenanceCreate(MaintenanceBase):
    equipment_id: str

class MaintenanceUpdate(BaseModel):
    completed_date: Optional[datetime] = None
    performed_by: Optional[str] = None
    cost: Optional[float] = None
    notes: Optional[str] = None

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
    checklist: str
    all_checks_passed: bool
    valid_until: datetime
    remarks: Optional[str] = None

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
