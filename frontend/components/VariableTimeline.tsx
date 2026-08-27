import { EvidenceRecord, variableLabel } from "@/lib/types";
import { formatDateTime } from "@/lib/format";

interface VariableGroup {
  variable_code: string;
  points: EvidenceRecord[];
}

function clampPercent(position: number): number {
  return Math.min(Math.max(position, 0), 100);
}

export function VariableTimeline({
  evidence,
  windowStart,
  windowEnd,
  decisionAt,
}: {
  evidence: EvidenceRecord[];
  windowStart: string | null;
  windowEnd: string | null;
  decisionAt: string;
}) {
  if (evidence.length === 0 || !windowStart || !windowEnd) {
    return <p className="caption">No hay datos suficientes para representar la evolución temporal.</p>;
  }

  const start = new Date(windowStart).getTime();
  const end = new Date(windowEnd).getTime();
  const decision = new Date(decisionAt).getTime();
  const span = end - start;
  const decisionPosition = span > 0 ? clampPercent(((decision - start) / span) * 100) : 100;

  const groups: VariableGroup[] = [];
  for (const record of evidence) {
    let group = groups.find((g) => g.variable_code === record.variable_code);
    if (!group) {
      group = { variable_code: record.variable_code, points: [] };
      groups.push(group);
    }
    group.points.push(record);
  }

  return (
    <div>
      <p className="caption" style={{ marginBottom: "var(--space-5)" }}>
        RISA no dispone del valor numérico medido de cada variable, por lo que esta línea de tiempo
        muestra únicamente los momentos en que cada variable participó como evidencia dentro de la
        ventana analizada.
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
        {groups.map((group) => (
          <div key={group.variable_code}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "baseline",
                marginBottom: "var(--space-2)",
              }}
            >
              <span style={{ fontWeight: 600 }}>
                {variableLabel(group.variable_code)}{" "}
                <span className="caption">({group.variable_code})</span>
              </span>
              <span className="caption">
                {group.points.length} {group.points.length === 1 ? "observación" : "observaciones"}
              </span>
            </div>

            <div
              style={{
                position: "relative",
                height: 8,
                borderRadius: 999,
                backgroundColor: "var(--color-brand-soft)",
              }}
            >
              {/* decision_datetime marker */}
              <span
                title={`Decisión: ${formatDateTime(decisionAt)}`}
                style={{
                  position: "absolute",
                  left: `${decisionPosition}%`,
                  top: -6,
                  bottom: -6,
                  width: 2,
                  backgroundColor: "var(--color-critical)",
                }}
              />

              {group.points.map((point, index) => {
                const position =
                  span > 0 ? clampPercent(((new Date(point.event_datetime).getTime() - start) / span) * 100) : 50;
                return (
                  <span
                    key={index}
                    title={`${variableLabel(point.variable_code)} · ${formatDateTime(point.event_datetime)} · ${point.evidence_role}`}
                    style={{
                      position: "absolute",
                      left: `${position}%`,
                      top: "50%",
                      transform: "translate(-50%, -50%)",
                      width: 10,
                      height: 10,
                      borderRadius: "50%",
                      backgroundColor:
                        point.evidence_role === "PRIMARY" ? "var(--color-action)" : "var(--color-text-muted)",
                      border: "2px solid var(--color-surface)",
                    }}
                  />
                );
              })}
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginTop: "var(--space-1)",
              }}
            >
              <span className="caption">Inicio evidencia: {formatDateTime(windowStart)}</span>
              <span className="caption">Decisión: {formatDateTime(decisionAt)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
