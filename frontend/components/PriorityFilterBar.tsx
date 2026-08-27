export type PriorityFilterValue = "ALL" | "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

function buildFilters(allLabel: string): { value: PriorityFilterValue; label: string }[] {
  return [
    { value: "ALL", label: allLabel },
    { value: "CRITICAL", label: "Crítica" },
    { value: "HIGH", label: "Alta" },
    { value: "MEDIUM", label: "Media" },
    { value: "LOW", label: "Baja" },
  ];
}

export function PriorityFilterBar({
  value,
  onChange,
  allLabel = "Todas",
}: {
  value: PriorityFilterValue;
  onChange: (value: PriorityFilterValue) => void;
  allLabel?: string;
}) {
  const filters = buildFilters(allLabel);

  return (
    <div
      style={{
        display: "flex",
        gap: "var(--space-2)",
        marginBottom: "var(--space-4)",
        flexWrap: "wrap",
      }}
      role="group"
      aria-label="Filtrar por prioridad"
    >
      {filters.map((option) => (
        <button
          key={option.value}
          type="button"
          className={`filter-chip ${value === option.value ? "filter-chip-active" : ""}`}
          onClick={() => onChange(option.value)}
          aria-pressed={value === option.value}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
