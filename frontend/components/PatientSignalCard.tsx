import { PatientSignal, PRIORITY_LABEL } from "@/lib/types";
import { formatDateTime } from "@/lib/format";
import { PriorityBadge } from "@/components/PriorityBadge";

export function PatientSignalCard({
  signal,
  onSelect,
}: {
  signal: PatientSignal;
  onSelect: (signal: PatientSignal) => void;
}) {
  return (
    <button
      type="button"
      className="card card-clickable"
      onClick={() => onSelect(signal)}
      aria-label={`Señal detectada, prioridad ${PRIORITY_LABEL[signal.priority_level].toLowerCase()}, paciente ${signal.patient_id}. Ver detalle.`}
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
        <PriorityBadge priority={signal.priority_level} />
        {signal.risk_score !== null && (
          <span className="caption" style={{ fontWeight: 600 }}>
            Score: {signal.risk_score.toFixed(2)}
          </span>
        )}
      </div>

      <h3 style={{ marginBottom: "var(--space-1)" }}>{signal.patient_id}</h3>

      <p style={{ color: "var(--color-text-secondary)", marginBottom: "var(--space-3)" }}>
        {signal.short_description}
      </p>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span className="caption">{formatDateTime(signal.generated_at)}</span>
        <span style={{ color: "var(--color-action)", fontSize: 13, fontWeight: 600 }}>
          Ver detalle
        </span>
      </div>
    </button>
  );
}
