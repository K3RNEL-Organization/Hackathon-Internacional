import { Priority } from "@/lib/types";
import { formatDateTime } from "@/lib/format";
import { PriorityBadge } from "@/components/PriorityBadge";

export interface PatientSummary {
  patient_id: string;
  signal_count: number;
  max_priority: Priority;
  last_signal_at: string;
}

const CASE_CARD_CLASS: Record<Priority, string> = {
  LOW: "case-card--low",
  MEDIUM: "case-card--medium",
  HIGH: "case-card--high",
  CRITICAL: "case-card--critical",
};

export function PatientSummaryCard({
  patient,
  onSelect,
}: {
  patient: PatientSummary;
  onSelect: (patientId: string) => void;
}) {
  return (
    <button
      type="button"
      className={`card case-card card-clickable ${CASE_CARD_CLASS[patient.max_priority]}`}
      onClick={() => onSelect(patient.patient_id)}
      aria-label={`Paciente ${patient.patient_id}, mayor prioridad registrada ${patient.max_priority}. Ver detalle.`}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: "var(--space-4)",
          marginBottom: "var(--space-3)",
        }}
      >
        <h3>{patient.patient_id}</h3>
        <PriorityBadge priority={patient.max_priority} />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "var(--space-3)",
          marginBottom: "var(--space-3)",
        }}
      >
        <div>
          <p className="caption">Señales</p>
          <p style={{ fontWeight: 600 }}>{patient.signal_count}</p>
        </div>
        <div>
          <p className="caption">Última señal</p>
          <p style={{ fontWeight: 600, fontSize: 13 }}>{formatDateTime(patient.last_signal_at)}</p>
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <span style={{ color: "var(--color-action)", fontSize: 13, fontWeight: 600 }}>
          Ver detalle →
        </span>
      </div>
    </button>
  );
}
