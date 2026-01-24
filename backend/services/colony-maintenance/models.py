from sqlalchemy import Column, String, Text, DateTime, Boolean, Enum as SQLEnum, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
import sys
sys.path.append('../..')
from shared.database import Base


def enum_values(enum_cls):
    """Return a list of enum values for consistent storage."""
    return [member.value for member in enum_cls]


def generate_uuid():
    """Generate UUID as string for SQLite compatibility"""
    return str(uuid.uuid4())


class RequestStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    MATERIALS_REQUIRED = "materials_required"
    COMPLETED = "completed"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    request_number = Column(String(50), unique=True, nullable=False, index=True)
    resident_id = Column(String(36), nullable=False)  # FK to users table
    quarter_number = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)  # AC, Plumbing, Electrical, etc.
    sub_category = Column(String(100))
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    status = Column(
        SQLEnum(
            RequestStatus,
            values_callable=enum_values,
            validate_strings=True,
            name="cm_request_status"
        ),
        default=RequestStatus.SUBMITTED
    )
    
    # Assignment
    assigned_vendor_id = Column(String(36))  # FK to vendors table
    assigned_technician_id = Column(String(36))  # FK to technicians table
    assigned_at = Column(DateTime)
    
    # Tracking
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String(36))
    approved_at = Column(DateTime)
    
    # Completion
    completed_at = Column(DateTime)
    closed_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Feedback
    rating = Column(Integer)  # 1-5
    feedback = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attachments = relationship("RequestAttachment", back_populates="request")
    status_history = relationship("RequestStatusHistory", back_populates="request")


class RequestAttachment(Base):
    __tablename__ = "request_attachments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    request_id = Column(String(36), ForeignKey("maintenance_requests.id", ondelete="CASCADE"))
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    uploaded_by = Column(String(36))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    request = relationship("MaintenanceRequest", back_populates="attachments")


class RequestStatusHistory(Base):
    __tablename__ = "request_status_history"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    request_id = Column(String(36), ForeignKey("maintenance_requests.id", ondelete="CASCADE"))
    status = Column(
        SQLEnum(
            RequestStatus,
            values_callable=enum_values,
            validate_strings=True,
            name="cm_request_status"
        ),
        nullable=False
    )
    notes = Column(Text)
    changed_by = Column(String(36))
    changed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    request = relationship("MaintenanceRequest", back_populates="status_history")


class ServiceCategory(Base):
    __tablename__ = "service_categories"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    sla_hours = Column(Integer, default=24)  # SLA in hours
    icon = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    company_name = Column(String(200))
    email = Column(String(255))
    phone = Column(String(20), nullable=False)
    service_categories = Column(String(500))  # Comma-separated category IDs
    rating = Column(Float, default=0.0)
    total_jobs = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    asset_number = Column(String(50), unique=True, nullable=False)
    asset_type = Column(String(100), nullable=False)  # AC, Geyser, Furniture, etc.
    quarter_number = Column(String(50), nullable=False)
    make = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))
    installation_date = Column(DateTime)
    warranty_expiry = Column(DateTime)
    amc_start_date = Column(DateTime)
    amc_end_date = Column(DateTime)
    amc_vendor = Column(String(200))
    status = Column(String(50), default="active")  # active, under_repair, retired
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RecurringMaintenance(Base):
    __tablename__ = "recurring_maintenance"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)
    frequency = Column(String(50), nullable=False)  # monthly, quarterly, annual
    next_schedule_date = Column(DateTime, nullable=False)
    assigned_vendor_id = Column(String(36))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Technician(Base):
    __tablename__ = "technicians"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    phone = Column(String(20))
    email = Column(String(255))
    specialization = Column(String(100))
    vendor_id = Column(String(36))
    rating = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

