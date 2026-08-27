import { PRIORITY_LABEL } from "@/lib/types";

interface Counts {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

const COLOR_VAR: Record<keyof Counts, string> = {
  critical: "var(--color-critical)",
  high: "var(--color-high)",
  medium: "var(--color-medium)",
  low: "var(--color-low)",
};

const PRIORITY_KEY: Record<keyof Counts, "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"> = {
  critical: "CRITICAL",
  high: "HIGH",
  medium: "MEDIUM",
  low: "LOW",
};

export function PriorityDistributionBar({ counts }: { counts: Counts }) {
  const total = counts.critical + counts.high + counts.medium + counts.low;

  return (
    <div>
      <div className="priority-distribution-bar" role="img" aria-label="Distribución de señales por prioridad">
        {(Object.keys(counts) as (keyof Counts)[]).map((key) => {
          const width = total > 0 ? (counts[key] / total) * 100 : 0;
          if (width === 0) return null;
          return (
            <span key={key} style={{ width: `${width}%`, backgroundColor: COLOR_VAR[key] }} />
          );
        })}
      </div>

      <div className="priority-legend" style={{ marginTop: "var(--space-5)" }}>
        {(Object.keys(counts) as (keyof Counts)[]).map((key) => {
          const percentage = total > 0 ? ((counts[key] / total) * 100).toFixed(1) : "0";
          return (
            <div key={key} className="priority-legend__item">
              <span
                className="priority-indicator"
                style={{ backgroundColor: COLOR_VAR[key] }}
                aria-hidden="true"
              />
              <span className="caption">{PRIORITY_LABEL[PRIORITY_KEY[key]]}</span>
              <strong>{counts[key]}</strong>
              <small>{percentage}%</small>
            </div>
          );
        })}
      </div>
    </div>
  );
}
