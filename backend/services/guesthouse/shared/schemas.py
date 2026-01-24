from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    employee_id: str
    full_name: str
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    plant_location: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    plant_location: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: str  # UUID as string for SQLite compatibility
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Authentication schemas
class LoginRequest(BaseModel):
    username: str  # Can be email or employee_id
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


# Notification schemas
class NotificationBase(BaseModel):
    title: str
    message: str
    type: Optional[str] = None


class NotificationCreate(NotificationBase):
    user_id: UUID


class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Common response schemas
class MessageResponse(BaseModel):
    message: str
    success: bool = True


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int


# Approval workflow schemas
class ApprovalRequest(BaseModel):
    approved: bool
    comments: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: UUID
    status: str
    approver_id: UUID
    approved_at: datetime
    comments: Optional[str] = None


# File upload schemas
class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    file_size: int
    content_type: str
    uploaded_at: datetime


# Audit log schemas
class AuditLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    action: str
    module: str
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
