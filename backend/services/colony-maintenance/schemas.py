from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RequestStatusEnum(str, Enum):
    SUBMITTED = "submitted"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    MATERIALS_REQUIRED = "materials_required"
    COMPLETED = "completed"
    CLOSED = "closed"
    CANCELLED = "cancelled"


# Maintenance Request Schemas
class MaintenanceRequestCreate(BaseModel):
    quarter_number: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., min_length=1, max_length=100)
    sub_category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    priority: str = Field("medium", min_length=1, max_length=20)


class MaintenanceRequestUpdate(BaseModel):
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    sub_category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    priority: Optional[str] = Field(None, min_length=1, max_length=20)
    status: Optional[RequestStatusEnum] = None
    estimated_cost: Optional[float] = Field(None, ge=0)
    actual_cost: Optional[float] = Field(None, ge=0)
    resolution_notes: Optional[str] = Field(None, min_length=1)


class MaintenanceRequestAssign(BaseModel):
    assigned_vendor_id: Optional[str] = Field(None, min_length=1)
    assigned_technician_id: Optional[str] = Field(None, min_length=1)
    requires_approval: Optional[bool] = None
    estimated_cost: Optional[float] = Field(None, ge=0)


class MaintenanceStatusChange(BaseModel):
    status: RequestStatusEnum
    notes: Optional[str] = Field(None, min_length=1)
    actual_cost: Optional[float] = Field(None, ge=0)


class MaintenanceRequestResponse(BaseModel):
    id: str
    request_number: str
    resident_id: str
    quarter_number: str
    category: str
    sub_category: Optional[str]
    description: str
    priority: str
    status: RequestStatusEnum
    assigned_vendor_id: Optional[str]
    assigned_technician_id: Optional[str]
    estimated_cost: Optional[float]
    actual_cost: Optional[float]
    rating: Optional[int]
    feedback: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RequestStatusHistoryResponse(BaseModel):
    id: str
    status: RequestStatusEnum
    notes: Optional[str]
    changed_by: Optional[str]
    changed_at: datetime

    class Config:
        from_attributes = True


# Vendor Schemas
class VendorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: str = Field(..., min_length=1, max_length=20)
    service_categories: str = Field(..., min_length=1)


class VendorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    service_categories: Optional[str] = Field(None, min_length=1)
    is_active: Optional[bool] = None


class VendorResponse(BaseModel):
    id: str
    name: str
    company_name: Optional[str]
    email: Optional[str]
    phone: str
    service_categories: str
    rating: float
    total_jobs: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Asset Schemas
class AssetCreate(BaseModel):
    asset_number: str = Field(..., min_length=1, max_length=50)
    asset_type: str = Field(..., min_length=1, max_length=100)
    quarter_number: str = Field(..., min_length=1, max_length=50)
    make: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    serial_number: Optional[str] = Field(None, min_length=1, max_length=100)
    installation_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    amc_start_date: Optional[datetime] = None
    amc_end_date: Optional[datetime] = None
    amc_vendor: Optional[str] = Field(None, min_length=1, max_length=200)


class AssetUpdate(BaseModel):
    asset_type: Optional[str] = Field(None, min_length=1, max_length=100)
    make: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = Field(None, min_length=1, max_length=50)
    warranty_expiry: Optional[datetime] = None
    amc_start_date: Optional[datetime] = None
    amc_end_date: Optional[datetime] = None


class AssetResponse(BaseModel):
    id: str
    asset_number: str
    asset_type: str
    quarter_number: str
    make: Optional[str]
    model: Optional[str]
    serial_number: Optional[str]
    installation_date: Optional[datetime]
    warranty_expiry: Optional[datetime]
    amc_start_date: Optional[datetime]
    amc_end_date: Optional[datetime]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Service Category Schemas
class ServiceCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    sla_hours: int = Field(24, ge=1)
    icon: Optional[str] = Field(None, min_length=1, max_length=200)
    is_active: bool = True


class ServiceCategoryUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    sla_hours: Optional[int] = Field(None, ge=1)
    icon: Optional[str] = Field(None, min_length=1, max_length=200)
    is_active: Optional[bool] = None


class ServiceCategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    sla_hours: int
    icon: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Feedback Schema
class FeedbackCreate(BaseModel):
    request_id: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = Field(None, min_length=1)


# Recurring Maintenance Schemas
class RecurringMaintenanceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    category: str = Field(..., min_length=1, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=50)  # monthly, quarterly, annual
    next_schedule_date: datetime
    assigned_vendor_id: Optional[str] = Field(None, min_length=1)
    is_active: bool = True


class RecurringMaintenanceUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    frequency: Optional[str] = Field(None, min_length=1, max_length=50)
    next_schedule_date: Optional[datetime] = None
    assigned_vendor_id: Optional[str] = Field(None, min_length=1)
    is_active: Optional[bool] = None


class RecurringMaintenanceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: str
    frequency: str
    next_schedule_date: datetime
    assigned_vendor_id: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Technician Schemas
class TechnicianCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    specialization: Optional[str] = Field(None, min_length=1, max_length=200)
    vendor_id: Optional[str] = Field(None, min_length=1)


class TechnicianUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    specialization: Optional[str] = Field(None, min_length=1, max_length=200)
    vendor_id: Optional[str] = Field(None, min_length=1)
    is_active: Optional[bool] = None


class TechnicianResponse(BaseModel):
    id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    specialization: Optional[str]
    vendor_id: Optional[str]
    rating: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard Statistics
class DashboardStats(BaseModel):
    total_requests: int
    pending_requests: int
    in_progress_requests: int
    completed_requests: int
    avg_resolution_time: float
    avg_rating: float
    overdue_requests: int
    active_recurring: int
    open_assignments: int
