export function StatCard({
  label,
  value,
  accentColor,
  icon,
}: {
  label: string;
  value: number | string;
  accentColor?: string;
  icon?: string;
}) {
  return (
    <div className="card kpi-card" style={{ textAlign: "center", position: "relative" }}>
      {icon && (
        <span
          className="kpi-icon"
          style={{ position: "absolute", top: "var(--space-5)", right: "var(--space-5)", ...(accentColor ? { color: accentColor } : undefined) }}
          aria-hidden="true"
        >
          {icon}
        </span>
      )}
      <p className="caption" style={{ textTransform: "uppercase", letterSpacing: 0.4 }}>
        {label}
      </p>
      <p className="kpi-card__value" style={{ color: accentColor ?? "var(--color-text-primary)" }}>
        {value}
      </p>
    </div>
  );
}
