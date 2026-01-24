from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class ShiftTypeEnum(str, Enum):
    MORNING = "morning"
    EVENING = "evening"
    NIGHT = "night"


class DutyStatusEnum(str, Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ABSENT = "absent"


class PatrolStatusEnum(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MISSED = "missed"


class IncidentSeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatusEnum(str, Enum):
    REPORTED = "reported"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SOSStatusEnum(str, Enum):
    ACTIVE = "active"
    RESPONDING = "responding"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"


# Duty Roster Schemas
class DutyRosterCreate(BaseModel):
    guard_id: str
    guard_name: str
    guard_phone: Optional[str] = None
    guard_employee_id: Optional[str] = None
    duty_date: datetime
    shift_type: ShiftTypeEnum
    shift_start: datetime
    shift_end: datetime
    assigned_gate: Optional[str] = None
    assigned_sector: Optional[str] = None
    patrol_route: Optional[str] = None
    supervisor_id: Optional[str] = None
    supervisor_name: Optional[str] = None
    special_instructions: Optional[str] = None


class DutyRosterUpdate(BaseModel):
    duty_date: Optional[datetime] = None
    shift_type: Optional[ShiftTypeEnum] = None
    shift_start: Optional[datetime] = None
    shift_end: Optional[datetime] = None
    assigned_gate: Optional[str] = None
    assigned_sector: Optional[str] = None
    patrol_route: Optional[str] = None
    status: Optional[DutyStatusEnum] = None
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    remarks: Optional[str] = None


class DutyRosterResponse(BaseModel):
    id: UUID
    roster_number: str
    guard_id: UUID
    guard_name: str
    guard_phone: Optional[str]
    guard_employee_id: Optional[str]
    duty_date: datetime
    shift_type: ShiftTypeEnum
    shift_start: datetime
    shift_end: datetime
    assigned_gate: Optional[str]
    assigned_sector: Optional[str]
    patrol_route: Optional[str]
    status: DutyStatusEnum
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    supervisor_id: Optional[UUID]
    supervisor_name: Optional[str]
    special_instructions: Optional[str]
    remarks: Optional[str]
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Checkpoint Schemas
class CheckpointCreate(BaseModel):
    checkpoint_name: str
    location_description: Optional[str] = None
    sector: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    rfid_tag_id: Optional[str] = None
    is_critical: bool = False
    expected_scan_interval: Optional[int] = None
    patrol_sequence: Optional[int] = None


class CheckpointUpdate(BaseModel):
    checkpoint_name: Optional[str] = None
    location_description: Optional[str] = None
    sector: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    rfid_tag_id: Optional[str] = None
    is_active: Optional[bool] = None
    is_critical: Optional[bool] = None
    expected_scan_interval: Optional[int] = None
    patrol_sequence: Optional[int] = None


class CheckpointResponse(BaseModel):
    id: UUID
    checkpoint_number: str
    checkpoint_name: str
    location_description: Optional[str]
    sector: Optional[str]
    building: Optional[str]
    floor: Optional[str]
    gps_latitude: Optional[float]
    gps_longitude: Optional[float]
    rfid_tag_id: Optional[str]
    qr_code: Optional[str]
    is_active: bool
    is_critical: bool
    expected_scan_interval: Optional[int]
    patrol_sequence: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Patrol Log Schemas
class PatrolLogCreate(BaseModel):
    duty_roster_id: str
    checkpoint_id: str
    scan_method: str = "manual"
    guard_id: str
    guard_name: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    observations: Optional[str] = None
    anomalies_found: bool = False
    anomaly_description: Optional[str] = None
    photo_path: Optional[str] = None


class PatrolLogResponse(BaseModel):
    id: UUID
    log_number: str
    duty_roster_id: UUID
    checkpoint_id: UUID
    scan_time: datetime
    scan_method: str
    guard_id: UUID
    guard_name: Optional[str]
    status: PatrolStatusEnum
    is_on_time: bool
    delay_minutes: int
    gps_latitude: Optional[float]
    gps_longitude: Optional[float]
    location_verified: bool
    observations: Optional[str]
    anomalies_found: bool
    anomaly_description: Optional[str]
    photo_path: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Incident Schemas
class IncidentCreate(BaseModel):
    title: str
    description: str
    incident_type: str
    severity: IncidentSeverityEnum = IncidentSeverityEnum.MEDIUM
    location: str
    sector: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    incident_time: datetime
    reported_by_guard_id: str
    reported_by_guard_name: Optional[str] = None
    duty_roster_id: Optional[str] = None
    witnesses: Optional[str] = None


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[IncidentSeverityEnum] = None
    status: Optional[IncidentStatusEnum] = None
    response_team: Optional[str] = None
    resolution_notes: Optional[str] = None
    actions_taken: Optional[str] = None
    police_informed: Optional[bool] = None
    fire_dept_informed: Optional[bool] = None
    medical_assistance: Optional[bool] = None
    evidence_collected: Optional[str] = None


class IncidentResponse(BaseModel):
    id: UUID
    incident_number: str
    title: str
    description: str
    incident_type: str
    severity: IncidentSeverityEnum
    location: str
    sector: Optional[str]
    building: Optional[str]
    floor: Optional[str]
    gps_latitude: Optional[float]
    gps_longitude: Optional[float]
    incident_time: datetime
    reported_time: datetime
    reported_by_guard_id: UUID
    reported_by_guard_name: Optional[str]
    duty_roster_id: Optional[UUID]
    status: IncidentStatusEnum
    acknowledged_by: Optional[UUID]
    acknowledged_at: Optional[datetime]
    response_team: Optional[str]
    response_time: Optional[datetime]
    resolution_notes: Optional[str]
    resolved_by: Optional[UUID]
    resolved_at: Optional[datetime]
    actions_taken: Optional[str]
    police_informed: bool
    fire_dept_informed: bool
    medical_assistance: bool
    witnesses: Optional[str]
    evidence_collected: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# SOS Alert Schemas
class SOSAlertCreate(BaseModel):
    guard_id: str
    guard_name: str
    guard_phone: Optional[str] = None
    alert_type: str = "emergency"
    location: Optional[str] = None
    sector: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None


class SOSAlertUpdate(BaseModel):
    status: Optional[SOSStatusEnum] = None
    response_team: Optional[str] = None
    response_time: Optional[datetime] = None
    responders_arrived_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    false_alarm: Optional[bool] = None
    false_alarm_reason: Optional[str] = None
    incident_id: Optional[str] = None


class SOSAlertResponse(BaseModel):
    id: UUID
    alert_number: str
    alert_time: datetime
    alert_type: str
    guard_id: UUID
    guard_name: str
    guard_phone: Optional[str]
    location: Optional[str]
    sector: Optional[str]
    gps_latitude: Optional[float]
    gps_longitude: Optional[float]
    status: SOSStatusEnum
    acknowledged_by: Optional[UUID]
    acknowledged_at: Optional[datetime]
    response_team: Optional[str]
    response_time: Optional[datetime]
    responders_arrived_at: Optional[datetime]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    false_alarm: bool
    false_alarm_reason: Optional[str]
    incident_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Dashboard Stats
class DashboardStats(BaseModel):
    total_guards: int
    active_patrols: int
    completed_patrols: int
    total_checkpoints: int
    incidents_today: int
    incidents_open: int
    sos_alerts_active: int
    sos_alerts_today: int
    missed_patrols: int
    critical_incidents: int
    
    class Config:
        from_attributes = True
