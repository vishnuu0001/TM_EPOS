from sqlalchemy import Column, String, Text, DateTime, Boolean, Enum as SQLEnum, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
import sys
sys.path.append('../..')
from shared.database import Base


def generate_uuid():
    """Generate UUID as string for SQLite compatibility"""
    return str(uuid.uuid4())


class ShiftType(str, enum.Enum):
    MORNING = "morning"  # 6 AM - 2 PM
    EVENING = "evening"  # 2 PM - 10 PM
    NIGHT = "night"      # 10 PM - 6 AM


class DutyStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ABSENT = "absent"


class PatrolStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MISSED = "missed"


class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, enum.Enum):
    REPORTED = "reported"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SOSStatus(str, enum.Enum):
    ACTIVE = "active"
    RESPONDING = "responding"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"


class DutyRoster(Base):
    __tablename__ = "duty_rosters"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    roster_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Guard Information
    guard_id = Column(String(36), nullable=False)  # FK to users table
    guard_name = Column(String(200), nullable=False)
    guard_phone = Column(String(20))
    guard_employee_id = Column(String(50))
    
    # Duty Details
    duty_date = Column(DateTime, nullable=False)
    shift_type = Column(SQLEnum(ShiftType), nullable=False)
    shift_start = Column(DateTime, nullable=False)
    shift_end = Column(DateTime, nullable=False)
    
    # Location
    assigned_gate = Column(String(100))
    assigned_sector = Column(String(100))
    patrol_route = Column(Text)  # JSON array of checkpoint IDs
    
    # Status
    status = Column(SQLEnum(DutyStatus), default=DutyStatus.SCHEDULED)
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    
    # Supervision
    supervisor_id = Column(String(36))  # FK to users table
    supervisor_name = Column(String(200))
    
    # Notes
    special_instructions = Column(Text)
    remarks = Column(Text)
    
    # Metadata
    created_by = Column(String(36))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patrol_logs = relationship("PatrolLog", back_populates="duty_roster")
    incidents = relationship("Incident", back_populates="duty_roster")


class Checkpoint(Base):
    __tablename__ = "checkpoints"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    checkpoint_number = Column(String(50), unique=True, nullable=False, index=True)
    checkpoint_name = Column(String(200), nullable=False)
    
    # Location
    location_description = Column(Text)
    sector = Column(String(100))
    building = Column(String(100))
    floor = Column(String(50))
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)
    
    # RFID Details (stub for future implementation)
    rfid_tag_id = Column(String(100), unique=True)
    qr_code = Column(Text)  # QR code for scanning
    
    # Status
    is_active = Column(Boolean, default=True)
    is_critical = Column(Boolean, default=False)  # Critical checkpoints must be scanned
    
    # Patrol Configuration
    expected_scan_interval = Column(Integer)  # minutes
    patrol_sequence = Column(Integer)  # Order in patrol route
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patrol_logs = relationship("PatrolLog", back_populates="checkpoint")


class PatrolLog(Base):
    __tablename__ = "patrol_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    log_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # References
    duty_roster_id = Column(String(36), ForeignKey("duty_rosters.id", ondelete="CASCADE"))
    checkpoint_id = Column(String(36), ForeignKey("checkpoints.id", ondelete="CASCADE"))
    
    # Patrol Details
    scan_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    scan_method = Column(String(50), default="manual")  # manual, rfid, qr
    
    # Guard Information
    guard_id = Column(String(36), nullable=False)
    guard_name = Column(String(200))
    
    # Status
    status = Column(SQLEnum(PatrolStatus), default=PatrolStatus.COMPLETED)
    is_on_time = Column(Boolean, default=True)
    delay_minutes = Column(Integer, default=0)
    
    # Location Verification
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)
    location_verified = Column(Boolean, default=False)
    
    # Observations
    observations = Column(Text)
    anomalies_found = Column(Boolean, default=False)
    anomaly_description = Column(Text)
    
    # Photo Evidence
    photo_path = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    duty_roster = relationship("DutyRoster", back_populates="patrol_logs")
    checkpoint = relationship("Checkpoint", back_populates="patrol_logs")


class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Incident Details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    incident_type = Column(String(100), nullable=False)  # theft, fire, medical, vandalism, etc.
    severity = Column(SQLEnum(IncidentSeverity), default=IncidentSeverity.MEDIUM)
    
    # Location
    location = Column(String(200), nullable=False)
    sector = Column(String(100))
    building = Column(String(100))
    floor = Column(String(50))
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)
    
    # Timing
    incident_time = Column(DateTime, nullable=False)
    reported_time = Column(DateTime, default=datetime.utcnow)
    
    # Reporter
    reported_by_guard_id = Column(String(36), nullable=False)
    reported_by_guard_name = Column(String(200))
    duty_roster_id = Column(String(36), ForeignKey("duty_rosters.id", ondelete="SET NULL"))
    
    # Status & Resolution
    status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.REPORTED)
    acknowledged_by = Column(String(36))  # FK to users table
    acknowledged_at = Column(DateTime)
    
    # Response
    response_team = Column(Text)  # JSON array of responder IDs
    response_time = Column(DateTime)
    resolution_notes = Column(Text)
    resolved_by = Column(String(36))  # FK to users table
    resolved_at = Column(DateTime)
    
    # Actions Taken
    actions_taken = Column(Text)
    police_informed = Column(Boolean, default=False)
    fire_dept_informed = Column(Boolean, default=False)
    medical_assistance = Column(Boolean, default=False)
    
    # Evidence
    witnesses = Column(Text)
    evidence_collected = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    duty_roster = relationship("DutyRoster", back_populates="incidents")
    attachments = relationship("IncidentAttachment", back_populates="incident")


class IncidentAttachment(Base):
    __tablename__ = "incident_attachments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"))
    
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))  # photo, video, document
    file_size = Column(Integer)
    description = Column(Text)
    
    uploaded_by = Column(String(36))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    incident = relationship("Incident", back_populates="attachments")


class SOSAlert(Base):
    __tablename__ = "sos_alerts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    alert_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Alert Details
    alert_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    alert_type = Column(String(100), default="emergency")  # emergency, panic, medical
    
    # Guard Information
    guard_id = Column(String(36), nullable=False)
    guard_name = Column(String(200), nullable=False)
    guard_phone = Column(String(20))
    
    # Location
    location = Column(String(200))
    sector = Column(String(100))
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)
    
    # Status
    status = Column(SQLEnum(SOSStatus), default=SOSStatus.ACTIVE)
    
    # Response
    acknowledged_by = Column(String(36))  # FK to users table
    acknowledged_at = Column(DateTime)
    response_team = Column(Text)  # JSON array
    response_time = Column(DateTime)
    responders_arrived_at = Column(DateTime)
    
    # Resolution
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    false_alarm = Column(Boolean, default=False)
    false_alarm_reason = Column(Text)
    
    # Related Incident
    incident_id = Column(String(36))  # FK to incidents table
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
