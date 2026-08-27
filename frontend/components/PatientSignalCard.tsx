import { PatientSignal, PRIORITY_LABEL, variableLabel } from "@/lib/types";
import { formatDateTime, formatSigma } from "@/lib/format";
import { PriorityBadge } from "@/components/PriorityBadge";

const CASE_CARD_CLASS: Record<PatientSignal["priority_level"], string> = {
  LOW: "case-card--low",
  MEDIUM: "case-card--medium",
  HIGH: "case-card--high",
  CRITICAL: "case-card--critical",
};

const MAX_VARIABLES_SHOWN = 3;

export function PatientSignalCard({
  signal,
  onSelect,
}: {
  signal: PatientSignal;
  onSelect: (signal: PatientSignal) => void;
}) {
  const shownDeviations = signal.variable_deviations.slice(0, MAX_VARIABLES_SHOWN);
  const remainingCount = signal.variable_deviations.length - shownDeviations.length;

  return (
    <button
      type="button"
      className={`card case-card card-clickable ${CASE_CARD_CLASS[signal.priority_level]}`}
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
            Score {signal.risk_score.toFixed(2)}
          </span>
        )}
      </div>

      <h3 style={{ marginBottom: "var(--space-2)" }}>{signal.patient_id}</h3>

      <p
        className="caption"
        style={{ color: "var(--color-text-secondary)", marginBottom: "var(--space-3)" }}
      >
        {signal.pattern_summary}
      </p>

      {shownDeviations.length > 0 && (
        <div style={{ marginBottom: "var(--space-3)" }}>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: `repeat(${shownDeviations.length}, 1fr)`,
              gap: "var(--space-2)",
            }}
          >
            {shownDeviations.map((deviation) => (
              <div key={deviation.variable_code} style={{ textAlign: "center" }}>
                <p className="caption" style={{ fontWeight: 700, color: "var(--color-text-primary)" }}>
                  {variableLabel(deviation.variable_code)}
                </p>
                <p
                  style={{
                    fontSize: 12,
                    fontWeight: 600,
                    color:
                      deviation.direction === "INCREASE" ? "var(--color-high)" : "var(--color-action)",
                  }}
                >
                  {deviation.direction === "INCREASE" ? "↑" : "↓"} {formatSigma(deviation.z_score)}
                </p>
              </div>
            ))}
          </div>
          {remainingCount > 0 && (
            <p className="caption" style={{ marginTop: "var(--space-2)" }}>
              +{remainingCount} variable{remainingCount === 1 ? "" : "s"}
            </p>
          )}
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span className="caption">Decisión: {formatDateTime(signal.generated_at)}</span>
        <span style={{ color: "var(--color-action)", fontSize: 13, fontWeight: 600 }}>
          Ver detalle →
        </span>
      </div>
    </button>
  );
}
