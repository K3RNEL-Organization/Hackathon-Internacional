export function StatCard({
  label,
  value,
  accentColor,
}: {
  label: string;
  value: number | string;
  accentColor?: string;
}) {
  return (
    <div className="card" style={{ textAlign: "center" }}>
      <p
        className="caption"
        style={{ textTransform: "uppercase", letterSpacing: 0.4, marginBottom: "var(--space-3)" }}
      >
        {label}
      </p>
      <p style={{ fontSize: 28, fontWeight: 700, color: accentColor ?? "var(--color-text-primary)" }}>
        {value}
      </p>
    </div>
  );
}
