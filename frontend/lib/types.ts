export interface CurrentUser {
  email: string;
  name: string;
  role: "PROFESIONAL_SALUD" | "ADMINISTRADOR";
}

export type Priority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export const PRIORITY_LABEL: Record<Priority, string> = {
  LOW: "Baja",
  MEDIUM: "Media",
  HIGH: "Alta",
  CRITICAL: "Crítica",
};

export type DeviationDirection = "INCREASE" | "DECREASE";

export interface VariableDeviation {
  variable_code: string;
  direction: DeviationDirection;
  z_score: number;
}

/** Display-only translations. Internal codes (HR, RR, SpO2, TEMP, ...) are never changed. */
export const VARIABLE_LABEL: Record<string, string> = {
  HR: "FC",
  RR: "FR",
  SpO2: "SpO₂",
  TEMP: "Temperatura",
  SBP: "PAS",
  DBP: "PAD",
  ACTIVITY_LEVEL: "Nivel de actividad",
  SIGNAL_QUALITY_INDEX: "Calidad de señal",
  SLEEP_STATE: "Estado de sueño",
  RECOVERY_PHASE: "Fase de recuperación",
  CONNECTIVITY: "Conectividad",
  LAB_A: "Laboratorio A",
  LAB_B: "Laboratorio B",
  LAB_C: "Laboratorio C",
  LAB_D: "Laboratorio D",
};

export function variableLabel(code: string): string {
  return VARIABLE_LABEL[code] ?? code;
}

export interface DashboardSummary {
  patients_monitored: number;
  active_signals: number;
  priority_critical: number;
  priority_high: number;
  priority_medium: number;
  priority_low: number;
  last_updated: string | null;
}

export interface PatientSignal {
  patient_id: string;
  signal_id: string;
  priority_level: Priority;
  risk_score: number | null;
  short_description: string;
  pattern_summary: string;
  variable_deviations: VariableDeviation[];
  generated_at: string;
}

export interface Condition {
  category: string;
  status: string;
  onset_date: string | null;
  recorded_at: string;
}

/** Display-only translations. Internal codes (RENAL_HISTORY, ...) are never changed. */
export const CONDITION_CATEGORY_LABEL: Record<string, string> = {
  RENAL_HISTORY: "Antecedente renal",
  CARDIOVASCULAR_HISTORY: "Antecedente cardiovascular",
  RESPIRATORY_HISTORY: "Antecedente respiratorio",
  METABOLIC_HISTORY: "Antecedente metabólico",
  NO_MAJOR_RECORDED_HISTORY: "Sin antecedentes relevantes registrados",
};

export const CONDITION_STATUS_LABEL: Record<string, string> = {
  ACTIVE: "Activo",
  INACTIVE: "Inactivo",
  RESOLVED: "Resuelto",
  RECORDED: "Registrado",
};

export function conditionCategoryLabel(code: string): string {
  return CONDITION_CATEGORY_LABEL[code] ?? code.replaceAll("_", " ");
}

export function conditionStatusLabel(code: string): string {
  return CONDITION_STATUS_LABEL[code] ?? code;
}

export interface Encounter {
  encounter_id: string;
  start: string;
  end: string | null;
}

export type TimelineEventType =
  | "SIGNAL_DETECTED"
  | "ENCOUNTER_START"
  | "ENCOUNTER_END"
  | "CONDITION_RECORDED";

export interface TimelineEvent {
  type: TimelineEventType;
  label: string;
  timestamp: string;
  priority_level: Priority | null;
}

export interface PatientDetail {
  patient_id: string;
  current_priority: Priority | null;
  current_risk_score: number | null;
  last_signal_id: string | null;
  last_signal_at: string | null;
  last_updated: string | null;
  encounter: Encounter | null;
  conditions: Condition[];
  signals: PatientSignal[];
  timeline: TimelineEvent[];
}

export interface EvidenceRecord {
  source_file: string;
  variable_code: string;
  record_id: string;
  event_datetime: string;
  available_datetime: string;
  evidence_role: string;
  contribution: number;
}

export const SOURCE_FILE_LABEL: Record<string, string> = {
  "vital_signs.csv": "Signos vitales",
  "wearable_observations.csv": "Wearable",
  "device_observations.csv": "Dispositivo",
  "patient_context.csv": "Contexto del paciente",
  "laboratory_results.csv": "Laboratorio",
  "connectivity_events.csv": "Conectividad",
};

export interface SignalDetail {
  signal_id: string;
  patient_id: string;
  priority_level: Priority;
  risk_score: number | null;
  confidence_score: number | null;
  generated_at: string;
  model_version: string;
  explanation: string;
  evidence_window_start: string | null;
  evidence_window_end: string | null;
  variable_deviations: VariableDeviation[];
  pattern_summary: string;
  persistence_windows: number | null;
  device_quality_pct: number | null;
  activity_note: string | null;
  context_note: string | null;
  evidence: EvidenceRecord[];
}
