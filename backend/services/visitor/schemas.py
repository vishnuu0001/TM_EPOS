from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class VisitorTypeEnum(str, Enum):
    CONTRACTOR = "contractor"
    VENDOR = "vendor"
    CONSULTANT = "consultant"
    GUEST = "guest"
    OFFICIAL = "official"


class RequestStatusEnum(str, Enum):
    SUBMITTED = "submitted"
    TRAINING_PENDING = "training_pending"
    TRAINING_COMPLETED = "training_completed"
    MEDICAL_PENDING = "medical_pending"
    MEDICAL_UPLOADED = "medical_uploaded"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    GATE_PASS_ISSUED = "gate_pass_issued"
    EXPIRED = "expired"


class TrainingStatusEnum(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class GatePassStatusEnum(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class EntryExitTypeEnum(str, Enum):
    ENTRY = "entry"
    EXIT = "exit"


# Visitor Request Schemas
class VisitorRequestCreate(BaseModel):
    visitor_name: str = Field(..., min_length=1, max_length=200)
    visitor_company: Optional[str] = Field(None, min_length=1, max_length=200)
    visitor_phone: str = Field(..., min_length=1, max_length=20)
    visitor_email: Optional[str] = Field(None, min_length=1, max_length=255)
    visitor_type: VisitorTypeEnum
    sponsor_employee_id: str = Field(..., min_length=1, max_length=50)
    sponsor_name: str = Field(..., min_length=1, max_length=200)
    sponsor_department: Optional[str] = Field(None, min_length=1, max_length=100)
    purpose_of_visit: str = Field(..., min_length=1)
    visit_date: datetime
    expected_duration: Optional[int] = Field(None, ge=1)
    areas_to_visit: Optional[str] = Field(None, min_length=1)
    safety_required: bool = True
    medical_required: bool = True


class VisitorRequestUpdate(BaseModel):
    visitor_name: Optional[str] = Field(None, min_length=1, max_length=200)
    visitor_company: Optional[str] = Field(None, min_length=1, max_length=200)
    visitor_phone: Optional[str] = Field(None, min_length=1, max_length=20)
    visitor_email: Optional[str] = Field(None, min_length=1, max_length=255)
    purpose_of_visit: Optional[str] = Field(None, min_length=1)
    visit_date: Optional[datetime] = None
    expected_duration: Optional[int] = Field(None, ge=1)
    areas_to_visit: Optional[str] = Field(None, min_length=1)
    status: Optional[RequestStatusEnum] = None
    rejection_reason: Optional[str] = Field(None, min_length=1)


class VisitorRequestResponse(BaseModel):
    id: str
    request_number: str
    visitor_name: str
    visitor_company: Optional[str]
    visitor_phone: str
    visitor_email: Optional[str]
    visitor_type: VisitorTypeEnum
    sponsor_employee_id: str
    sponsor_name: str
    sponsor_department: Optional[str]
    purpose_of_visit: str
    visit_date: datetime
    expected_duration: Optional[int]
    areas_to_visit: Optional[str]
    status: RequestStatusEnum
    safety_required: bool
    medical_required: bool
    approved_by_sponsor: bool
    approved_by_safety: bool
    approved_by_security: bool
    final_approved_by: Optional[str]
    final_approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Safety Training Schemas
class SafetyTrainingCreate(BaseModel):
    request_id: str = Field(..., min_length=1)
    video_url: Optional[str] = Field(None, min_length=1, max_length=500)
    video_duration: Optional[int] = Field(None, ge=1)


class SafetyTrainingUpdate(BaseModel):
    video_watched: Optional[bool] = None
    watch_duration: Optional[int] = Field(None, ge=0)
    quiz_attempted: Optional[bool] = None
    quiz_score: Optional[int] = Field(None, ge=0)
    quiz_passed: Optional[bool] = None
    status: Optional[TrainingStatusEnum] = None


class SafetyTrainingResponse(BaseModel):
    id: str
    request_id: str
    video_url: Optional[str]
    video_duration: Optional[int]
    video_watched: bool
    watch_duration: Optional[int]
    video_completed_at: Optional[datetime]
    quiz_attempted: bool
    quiz_score: Optional[int]
    quiz_total: int
    quiz_passed: bool
    quiz_attempts: int
    quiz_completed_at: Optional[datetime]
    certificate_issued: bool
    certificate_number: Optional[str]
    certificate_issued_at: Optional[datetime]
    status: TrainingStatusEnum
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Training Certificate Schemas
class TrainingCertificateCreate(BaseModel):
    training_id: str = Field(..., min_length=1)
    visitor_name: str = Field(..., min_length=1, max_length=200)
    valid_until: Optional[datetime] = None


class TrainingCertificateResponse(BaseModel):
    id: str
    training_id: str
    certificate_number: str
    visitor_name: str
    issue_date: datetime
    valid_until: Optional[datetime]
    qr_code: Optional[str]
    pdf_path: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Medical Clearance Schemas
class MedicalClearanceCreate(BaseModel):
    request_id: str = Field(..., min_length=1)
    document_name: str = Field(..., min_length=1, max_length=200)
    document_path: str = Field(..., min_length=1)
    document_type: str = Field(..., min_length=1, max_length=50)
    document_size: int = Field(..., ge=0)


class MedicalClearanceUpdate(BaseModel):
    verified: Optional[bool] = None
    verification_notes: Optional[str] = Field(None, min_length=1)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class MedicalClearanceResponse(BaseModel):
    id: str
    request_id: str
    document_name: Optional[str]
    document_path: Optional[str]
    document_type: Optional[str]
    document_size: Optional[int]
    uploaded_at: Optional[datetime]
    verified: bool
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    verification_notes: Optional[str]
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Gate Pass Schemas
class GatePassCreate(BaseModel):
    request_id: str = Field(..., min_length=1)
    visitor_name: str = Field(..., min_length=1, max_length=200)
    visitor_company: Optional[str] = Field(None, min_length=1, max_length=200)
    visitor_phone: str = Field(..., min_length=1, max_length=20)
    visitor_type: VisitorTypeEnum
    valid_from: datetime
    valid_until: datetime
    authorized_areas: Optional[str] = Field(None, min_length=1)
    special_instructions: Optional[str] = Field(None, min_length=1)
    sponsor_name: str = Field(..., min_length=1, max_length=200)
    sponsor_contact: Optional[str] = Field(None, min_length=1, max_length=20)

    @validator("valid_until")
    def validate_valid_until(cls, value, values):
        valid_from = values.get("valid_from")
        if valid_from and value <= valid_from:
            raise ValueError("valid_until must be after valid_from")
        return value


class GatePassUpdate(BaseModel):
    status: Optional[GatePassStatusEnum] = None
    valid_until: Optional[datetime] = None
    authorized_areas: Optional[str] = Field(None, min_length=1)
    special_instructions: Optional[str] = Field(None, min_length=1)


class GatePassResponse(BaseModel):
    id: str
    request_id: str
    pass_number: str
    visitor_name: str
    visitor_company: Optional[str]
    visitor_phone: str
    visitor_type: VisitorTypeEnum
    valid_from: datetime
    valid_until: datetime
    status: GatePassStatusEnum
    qr_code: Optional[str]
    qr_data: Optional[str]
    pass_pdf_path: Optional[str]
    authorized_areas: Optional[str]
    special_instructions: Optional[str]
    sponsor_name: str
    sponsor_contact: Optional[str]
    issued_by: Optional[str]
    issued_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Entry/Exit Log Schemas
class EntryExitCreate(BaseModel):
    request_id: str = Field(..., min_length=1)
    gate_pass_id: str = Field(..., min_length=1)
    log_type: EntryExitTypeEnum
    gate_number: Optional[str] = Field(None, min_length=1, max_length=50)
    guard_id: Optional[str] = Field(None, min_length=1)
    guard_name: Optional[str] = Field(None, min_length=1, max_length=200)
    qr_scanned: bool = False
    manual_entry: bool = False
    verification_notes: Optional[str] = Field(None, min_length=1)
    vehicle_number: Optional[str] = Field(None, min_length=1, max_length=50)
    vehicle_type: Optional[str] = Field(None, min_length=1, max_length=50)
    photo_path: Optional[str] = Field(None, min_length=1)


class EntryExitResponse(BaseModel):
    id: str
    request_id: str
    gate_pass_id: str
    log_type: EntryExitTypeEnum
    gate_number: Optional[str]
    timestamp: datetime
    guard_id: Optional[str]
    guard_name: Optional[str]
    qr_scanned: bool
    manual_entry: bool
    verification_notes: Optional[str]
    vehicle_number: Optional[str]
    vehicle_type: Optional[str]
    photo_path: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dashboard Stats
class DashboardStats(BaseModel):
    total_requests: int
    pending_requests: int
    approved_requests: int
    pending_approvals: int
    active_visitors: int
    completed_visits: int
    training_pending: int
    medical_pending: int
    gate_passes_issued: int
    visitors_today: int
    visitors_onsite: int
    today_entries: int
    today_exits: int
    
    class Config:
        from_attributes = True
