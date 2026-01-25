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
    quarter_number: str
    category: str
    sub_category: Optional[str] = None
    description: str
    priority: str = "medium"


class MaintenanceRequestUpdate(BaseModel):
    category: Optional[str] = None
    sub_category: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[RequestStatusEnum] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    resolution_notes: Optional[str] = None


class MaintenanceRequestAssign(BaseModel):
    assigned_vendor_id: Optional[str] = None
    assigned_technician_id: Optional[str] = None
    requires_approval: Optional[bool] = None
    estimated_cost: Optional[float] = None


class MaintenanceStatusChange(BaseModel):
    status: RequestStatusEnum
    notes: Optional[str] = None
    actual_cost: Optional[float] = None


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
    name: str
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: str
    service_categories: str


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    service_categories: Optional[str] = None
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
    asset_number: str
    asset_type: str
    quarter_number: str
    make: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    installation_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    amc_start_date: Optional[datetime] = None
    amc_end_date: Optional[datetime] = None
    amc_vendor: Optional[str] = None


class AssetUpdate(BaseModel):
    asset_type: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    status: Optional[str] = None
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
    name: str
    description: Optional[str] = None
    sla_hours: int = 24
    icon: Optional[str] = None
    is_active: bool = True


class ServiceCategoryUpdate(BaseModel):
    description: Optional[str] = None
    sla_hours: Optional[int] = None
    icon: Optional[str] = None
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
    request_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None


# Recurring Maintenance Schemas
class RecurringMaintenanceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    frequency: str  # monthly, quarterly, annual
    next_schedule_date: datetime
    assigned_vendor_id: Optional[str] = None
    is_active: bool = True


class RecurringMaintenanceUpdate(BaseModel):
    description: Optional[str] = None
    frequency: Optional[str] = None
    next_schedule_date: Optional[datetime] = None
    assigned_vendor_id: Optional[str] = None
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
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    specialization: Optional[str] = None
    vendor_id: Optional[str] = None


class TechnicianUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    specialization: Optional[str] = None
    vendor_id: Optional[str] = None
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
