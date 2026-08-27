import { EvidenceRecord } from "@/lib/types";
import { formatDateTime } from "@/lib/format";

interface VariableGroup {
  variable_code: string;
  points: EvidenceRecord[];
}

export function VariableTimeline({
  evidence,
  windowStart,
  windowEnd,
}: {
  evidence: EvidenceRecord[];
  windowStart: string | null;
  windowEnd: string | null;
}) {
  if (evidence.length === 0 || !windowStart || !windowEnd) {
    return <p className="caption">No hay datos suficientes para representar la evolución temporal.</p>;
  }

  const start = new Date(windowStart).getTime();
  const end = new Date(windowEnd).getTime();
  const span = end - start;

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
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-5)" }}>
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
            <span style={{ fontWeight: 600 }}>{group.variable_code}</span>
            <span className="caption">
              {group.points.length} {group.points.length === 1 ? "observación" : "observaciones"}
            </span>
          </div>
          <div
            style={{
              position: "relative",
              height: 8,
              borderRadius: 999,
              backgroundColor: "var(--color-border)",
            }}
          >
            {group.points.map((point, index) => {
              const position = span > 0 ? ((new Date(point.event_datetime).getTime() - start) / span) * 100 : 50;
              return (
                <span
                  key={index}
                  title={`${point.variable_code} · ${formatDateTime(point.event_datetime)} · ${point.evidence_role}`}
                  style={{
                    position: "absolute",
                    left: `${Math.min(Math.max(position, 0), 100)}%`,
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
            <span className="caption">{formatDateTime(windowStart)}</span>
            <span className="caption">{formatDateTime(windowEnd)}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
