import enum
from datetime import datetime

from pydantic import BaseModel, EmailStr

from .models import UserRole


class SignalPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    name: str
    email: EmailStr


class UserOut(BaseModel):
    email: EmailStr
    name: str
    role: UserRole

    model_config = {"from_attributes": True}


class DashboardSummary(BaseModel):
    patients_monitored: int
    active_signals: int
    priority_critical: int
    priority_high: int
    priority_medium: int
    priority_low: int
    last_updated: datetime | None


class PatientSignalOut(BaseModel):
    patient_id: str
    signal_id: str
    priority_level: SignalPriority
    risk_score: float | None
    short_description: str
    generated_at: datetime


class ConditionOut(BaseModel):
    category: str
    status: str
    onset_date: datetime | None
    recorded_at: datetime


class EncounterOut(BaseModel):
    encounter_id: str
    start: datetime
    end: datetime | None


class TimelineEventType(str, enum.Enum):
    SIGNAL_DETECTED = "SIGNAL_DETECTED"
    ENCOUNTER_START = "ENCOUNTER_START"
    ENCOUNTER_END = "ENCOUNTER_END"
    CONDITION_RECORDED = "CONDITION_RECORDED"


class TimelineEventOut(BaseModel):
    type: TimelineEventType
    label: str
    timestamp: datetime
    priority_level: SignalPriority | None = None


class PatientDetailOut(BaseModel):
    patient_id: str
    current_priority: SignalPriority | None
    current_risk_score: float | None
    last_signal_id: str | None
    last_signal_at: datetime | None
    last_updated: datetime | None
    encounter: EncounterOut | None
    conditions: list[ConditionOut]
    signals: list[PatientSignalOut]
    timeline: list[TimelineEventOut]


class VariableDeviationOut(BaseModel):
    variable_code: str
    direction: str
    z_score: float


class EvidenceRecordOut(BaseModel):
    source_file: str
    variable_code: str
    record_id: str
    event_datetime: datetime
    available_datetime: datetime
    evidence_role: str
    contribution: float


class SignalDetailOut(BaseModel):
    model_config = {"protected_namespaces": ()}

    signal_id: str
    patient_id: str
    priority_level: SignalPriority
    risk_score: float | None
    confidence_score: float | None
    generated_at: datetime
    model_version: str
    explanation: str
    evidence_window_start: datetime | None
    evidence_window_end: datetime | None
    variable_deviations: list[VariableDeviationOut]
    evidence: list[EvidenceRecordOut]
