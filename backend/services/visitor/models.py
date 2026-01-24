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


class VisitorType(str, enum.Enum):
    CONTRACTOR = "contractor"
    VENDOR = "vendor"
    CONSULTANT = "consultant"
    GUEST = "guest"
    OFFICIAL = "official"


class RequestStatus(str, enum.Enum):
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


class TrainingStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class GatePassStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class EntryExitType(str, enum.Enum):
    ENTRY = "entry"
    EXIT = "exit"


class VisitorRequest(Base):
    __tablename__ = "visitor_requests"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    request_number = Column(String(50), unique=True, nullable=False, index=True)
    visitor_name = Column(String(200), nullable=False)
    visitor_company = Column(String(200))
    visitor_phone = Column(String(20), nullable=False)
    visitor_email = Column(String(255))
    visitor_type = Column(
        SQLEnum(
            VisitorType,
            values_callable=enum_values,
            validate_strings=True,
            name="visitortype"
        ),
        nullable=False
    )
    
    # Sponsor Information
    sponsor_employee_id = Column(String(36), nullable=False)  # FK to users table
    sponsor_name = Column(String(200), nullable=False)
    sponsor_department = Column(String(100))
    
    # Visit Details
    purpose_of_visit = Column(Text, nullable=False)
    visit_date = Column(DateTime, nullable=False)
    expected_duration = Column(Integer)  # in hours
    areas_to_visit = Column(Text)
    
    # Status & Approval
    status = Column(
        SQLEnum(
            RequestStatus,
            values_callable=enum_values,
            validate_strings=True,
            name="requeststatus"
        ),
        default=RequestStatus.SUBMITTED
    )
    safety_required = Column(Boolean, default=True)
    medical_required = Column(Boolean, default=True)
    
    # Approval Workflow
    approved_by_sponsor = Column(Boolean, default=False)
    approved_by_safety = Column(Boolean, default=False)
    approved_by_security = Column(Boolean, default=False)
    
    # Final Approval
    final_approved_by = Column(String(36))
    final_approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    safety_training = relationship("SafetyTraining", back_populates="request", uselist=False)
    medical_clearance = relationship("MedicalClearance", back_populates="request", uselist=False)
    gate_pass = relationship("GatePass", back_populates="request", uselist=False)
    entry_exit_logs = relationship("EntryExit", back_populates="request")


class SafetyTraining(Base):
    __tablename__ = "safety_training"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    request_id = Column(String(36), ForeignKey("visitor_requests.id", ondelete="CASCADE"), unique=True)
    
    # Training Video
    video_url = Column(String(500))
    video_duration = Column(Integer)  # in seconds
    video_watched = Column(Boolean, default=False)
    watch_duration = Column(Integer)  # seconds watched
    video_completed_at = Column(DateTime)
    
    # Quiz
    quiz_attempted = Column(Boolean, default=False)
    quiz_score = Column(Integer)
    quiz_total = Column(Integer, default=10)
    quiz_passed = Column(Boolean, default=False)
    quiz_attempts = Column(Integer, default=0)
    quiz_completed_at = Column(DateTime)
    
    # Certificate
    certificate_issued = Column(Boolean, default=False)
    certificate_number = Column(String(50))
    certificate_issued_at = Column(DateTime)
    
    # Status
    status = Column(
        SQLEnum(
            TrainingStatus,
            values_callable=enum_values,
            validate_strings=True,
            name="trainingstatus"
        ),
        default=TrainingStatus.NOT_STARTED
    )
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    request = relationship("VisitorRequest", back_populates="safety_training")
    certificate = relationship("TrainingCertificate", back_populates="training", uselist=False)


class TrainingCertificate(Base):
    __tablename__ = "training_certificates"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    training_id = Column(String(36), ForeignKey("safety_training.id", ondelete="CASCADE"), unique=True)
    certificate_number = Column(String(50), unique=True, nullable=False)
    visitor_name = Column(String(200), nullable=False)
    issue_date = Column(DateTime, nullable=False)
    valid_until = Column(DateTime)
    qr_code = Column(Text)  # Base64 QR code
    pdf_path = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    training = relationship("SafetyTraining", back_populates="certificate")


class MedicalClearance(Base):
    __tablename__ = "medical_clearances"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    request_id = Column(String(36), ForeignKey("visitor_requests.id", ondelete="CASCADE"), unique=True)
    
    # Document Upload
    document_name = Column(String(255))
    document_path = Column(String(500))
    document_type = Column(String(50))  # pdf, jpg, png
    document_size = Column(Integer)  # bytes
    uploaded_at = Column(DateTime)
    
    # Verification
    verified = Column(Boolean, default=False)
    verified_by = Column(String(36))  # FK to users table
    verified_at = Column(DateTime)
    verification_notes = Column(Text)
    
    # Validity
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    request = relationship("VisitorRequest", back_populates="medical_clearance")


class GatePass(Base):
    __tablename__ = "gate_passes"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    request_id = Column(String(36), ForeignKey("visitor_requests.id", ondelete="CASCADE"), unique=True)
    pass_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Pass Details
    visitor_name = Column(String(200), nullable=False)
    visitor_company = Column(String(200))
    visitor_phone = Column(String(20))
    visitor_type = Column(
        SQLEnum(
            VisitorType,
            values_callable=enum_values,
            validate_strings=True,
            name="visitortype"
        )
    )
    
    # Validity
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    status = Column(
        SQLEnum(
            GatePassStatus,
            values_callable=enum_values,
            validate_strings=True,
            name="gatepassstatus"
        ),
        default=GatePassStatus.ACTIVE
    )
    
    # QR Code
    qr_code = Column(Text)  # Base64 QR code
    qr_data = Column(Text)  # JSON string with pass details
    
    # Pass Document
    pass_pdf_path = Column(String(500))
    
    # Access Control
    authorized_areas = Column(Text)  # JSON array
    special_instructions = Column(Text)
    
    # Sponsor
    sponsor_name = Column(String(200))
    sponsor_contact = Column(String(20))
    
    # Issuance
    issued_by = Column(String(36))  # FK to users table
    issued_at = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    request = relationship("VisitorRequest", back_populates="gate_pass")
    entry_exit_logs = relationship("EntryExit", back_populates="gate_pass")


class EntryExit(Base):
    __tablename__ = "entry_exit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    request_id = Column(String(36), ForeignKey("visitor_requests.id", ondelete="CASCADE"))
    gate_pass_id = Column(String(36), ForeignKey("gate_passes.id", ondelete="CASCADE"))
    
    # Entry/Exit Details
    log_type = Column(
        SQLEnum(
            EntryExitType,
            values_callable=enum_values,
            validate_strings=True,
            name="entryexittype"
        ),
        nullable=False
    )
    gate_number = Column(String(50))
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Security Guard
    guard_id = Column(String(36))  # FK to users table
    guard_name = Column(String(200))
    
    # Verification
    qr_scanned = Column(Boolean, default=False)
    manual_entry = Column(Boolean, default=False)
    verification_notes = Column(Text)
    
    # Vehicle (if applicable)
    vehicle_number = Column(String(50))
    vehicle_type = Column(String(50))
    
    # Photo Capture
    photo_path = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    request = relationship("VisitorRequest", back_populates="entry_exit_logs")
    gate_pass = relationship("GatePass", back_populates="entry_exit_logs")
