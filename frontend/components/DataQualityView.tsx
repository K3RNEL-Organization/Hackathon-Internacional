"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  DATA_QUALITY_ISSUE_TYPE_LABEL,
  DataQualityIssue,
  DataQualityIssueType,
  DataQualitySummary,
  PlausibilityBreakdownItem,
  variableLabel,
  conditionCategoryLabel,
} from "@/lib/types";
import { Breadcrumb } from "@/components/Breadcrumb";
import { StatCard } from "@/components/StatCard";
import { EmptyState } from "@/components/EmptyState";

type LoadStatus = "loading" | "error" | "ready";

type IssueTypeFilter = "ALL" | DataQualityIssueType;

const ISSUE_TYPE_FILTERS: { value: IssueTypeFilter; label: string }[] = [
  { value: "ALL", label: "Todas" },
  { value: "PLAUSIBILITY", label: DATA_QUALITY_ISSUE_TYPE_LABEL.PLAUSIBILITY },
  { value: "RETRANSMISSION", label: DATA_QUALITY_ISSUE_TYPE_LABEL.RETRANSMISSION },
  { value: "UNIT_NORMALIZED", label: DATA_QUALITY_ISSUE_TYPE_LABEL.UNIT_NORMALIZED },
  { value: "TEMPORAL", label: DATA_QUALITY_ISSUE_TYPE_LABEL.TEMPORAL },
  { value: "ENCOUNTER_BOUNDARY", label: DATA_QUALITY_ISSUE_TYPE_LABEL.ENCOUNTER_BOUNDARY },
  { value: "LAB_REFERENCE", label: DATA_QUALITY_ISSUE_TYPE_LABEL.LAB_REFERENCE },
];

const TREATMENT_BADGE_CLASS: Record<string, string> = {
  "Marcado, no eliminado": "role-badge--quality",
  "Excluido del doble conteo fisiológico": "role-badge--primary",
  "Convertido a unidad canónica": "role-badge--supporting",
  "Conservado y marcado": "role-badge--context",
  "Revisable, no es señal de riesgo automática": "role-badge--context",
};

const PAGE_SIZE = 15;

const VITAL_VARIABLE_CODES = ["HR", "RR", "SpO2", "TEMP", "SBP", "DBP"];

function issueVariableLabel(issue: DataQualityIssue): string {
  if (issue.issue_type === "TEMPORAL") return conditionCategoryLabel(issue.variable_code);
  return variableLabel(issue.variable_code);
}

function formatDateTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("es-AR", { dateStyle: "short", timeStyle: "short" });
}

export function DataQualityView() {
  const router = useRouter();

  const [summaryStatus, setSummaryStatus] = useState<LoadStatus>("loading");
  const [summary, setSummary] = useState<DataQualitySummary | null>(null);
  const [breakdown, setBreakdown] = useState<PlausibilityBreakdownItem[]>([]);

  const [typeFilter, setTypeFilter] = useState<IssueTypeFilter>("ALL");
  const [patientQuery, setPatientQuery] = useState("");
  const [variableQuery, setVariableQuery] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);

  const [issuesStatus, setIssuesStatus] = useState<LoadStatus>("loading");
  const [issues, setIssues] = useState<DataQualityIssue[]>([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadSummary() {
      setSummaryStatus("loading");
      try {
        const [summaryResponse, breakdownResponse] = await Promise.all([
          fetch("/api/data-quality/summary", { cache: "no-store" }),
          fetch("/api/data-quality/plausibility-breakdown", { cache: "no-store" }),
        ]);

        if (summaryResponse.status === 401 || breakdownResponse.status === 401) {
          router.push("/login");
          return;
        }

        if (!summaryResponse.ok || !breakdownResponse.ok) {
          if (!cancelled) setSummaryStatus("error");
          return;
        }

        const summaryData: DataQualitySummary = await summaryResponse.json();
        const breakdownData: PlausibilityBreakdownItem[] = await breakdownResponse.json();

        if (!cancelled) {
          setSummary(summaryData);
          setBreakdown(breakdownData);
          setSummaryStatus("ready");
        }
      } catch {
        if (!cancelled) setSummaryStatus("error");
      }
    }

    loadSummary();
    return () => {
      cancelled = true;
    };
  }, [router]);

  const loadIssues = useCallback(
    async (filters: {
      type: IssueTypeFilter;
      patientQuery: string;
      variableQuery: string;
      searchQuery: string;
      page: number;
    }) => {
      setIssuesStatus("loading");
      try {
        const params = new URLSearchParams();
        if (filters.type !== "ALL") params.set("type", filters.type);
        if (filters.patientQuery.trim()) params.set("patient_id", filters.patientQuery.trim());
        if (filters.variableQuery.trim()) params.set("variable", filters.variableQuery.trim());
        if (filters.searchQuery.trim()) params.set("search", filters.searchQuery.trim());
        params.set("page", String(filters.page));
        params.set("page_size", String(PAGE_SIZE));

        const response = await fetch(`/api/data-quality/issues?${params.toString()}`, { cache: "no-store" });

        if (response.status === 401) {
          router.push("/login");
          return;
        }

        if (!response.ok) {
          setIssuesStatus("error");
          return;
        }

        const data: { items: DataQualityIssue[]; total: number } = await response.json();
        setIssues(data.items);
        setTotal(data.total);
        setIssuesStatus("ready");
      } catch {
        setIssuesStatus("error");
      }
    },
    [router]
  );

  useEffect(() => {
    const timeout = setTimeout(() => {
      loadIssues({ type: typeFilter, patientQuery, variableQuery, searchQuery, page });
    }, 300);
    return () => clearTimeout(timeout);
  }, [typeFilter, patientQuery, variableQuery, searchQuery, page, loadIssues]);

  useEffect(() => {
    setPage(1);
  }, [typeFilter, patientQuery, variableQuery, searchQuery]);

  const maxBreakdownCount = useMemo(
    () => breakdown.reduce((max, item) => Math.max(max, item.count), 0),
    [breakdown]
  );

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const hasActiveFilters = Boolean(patientQuery || variableQuery || searchQuery || typeFilter !== "ALL");

  function clearFilters() {
    setTypeFilter("ALL");
    setPatientQuery("");
    setVariableQuery("");
    setSearchQuery("");
  }

  return (
    <div>
      <Breadcrumb items={[{ label: "Dashboard", href: "/dashboard" }, { label: "Calidad de datos" }]} />

      <div style={{ marginBottom: "var(--space-4)" }}>
        <h1>Calidad de datos</h1>
        <p className="caption" style={{ marginTop: "var(--space-2)", fontSize: 13 }}>
          TriageMed valida la calidad, consistencia y temporalidad de la información antes de utilizarla en el
          análisis de riesgo.
        </p>
      </div>

      <div
        className="card"
        style={{
          marginBottom: "var(--space-6)",
          background: "var(--color-brand-soft)",
          border: "1px solid var(--color-border)",
        }}
      >
        <p style={{ margin: 0, fontSize: 13, color: "var(--color-action-hover)" }}>
          Una anomalía de calidad no representa por sí sola una condición clínica ni genera automáticamente una
          señal. Los registros sospechosos no se eliminan: se marcan, se normalizan cuando corresponde y se
          conserva el valor original para mantener trazabilidad.
        </p>
      </div>

      {summaryStatus === "loading" && (
        <div className="card-grid" style={{ marginBottom: "var(--space-6)" }}>
          {Array.from({ length: 5 }).map((_, index) => (
            <div key={index} className="skeleton" style={{ height: 110, borderRadius: "var(--radius-md)" }} />
          ))}
        </div>
      )}

      {summaryStatus === "error" && (
        <div className="card state-panel" style={{ marginBottom: "var(--space-6)" }}>
          <p>No fue posible cargar el resumen de calidad de datos.</p>
        </div>
      )}

      {summaryStatus === "ready" && summary && (
        <>
          <div className="card-grid" style={{ marginBottom: "var(--space-6)" }}>
            <StatCard label="Valores fuera de plausibilidad" value={summary.plausibility_issues} />
            <StatCard label="Retransmisiones detectadas" value={summary.retransmissions} />
            <StatCard label="Unidades normalizadas" value={summary.normalized_units} />
            <StatCard
              label="Incidencias temporales"
              value={summary.temporal_issues + summary.encounter_boundary_issues}
            />
            <StatCard label="Resultados fuera de referencia" value={summary.lab_out_of_reference} />
          </div>
          <p className="caption" style={{ marginTop: "calc(-1 * var(--space-4))", marginBottom: "var(--space-6)" }}>
            Estar fuera del rango de referencia de laboratorio no genera automáticamente una señal de riesgo.
          </p>

          <div className="card" style={{ marginBottom: "var(--space-6)" }}>
            <h3 style={{ marginBottom: "var(--space-4)" }}>Distribución de valores fuera de plausibilidad</h3>
            {breakdown.length === 0 ? (
              <p className="caption">Sin valores fuera de plausibilidad para mostrar.</p>
            ) : (
              <div style={{ display: "grid", gap: "var(--space-3)" }}>
                {breakdown.map((item) => (
                  <div key={item.variable_code} style={{ display: "grid", gridTemplateColumns: "70px 1fr 50px", gap: "var(--space-3)", alignItems: "center" }}>
                    <span className="caption" style={{ fontWeight: 600 }}>
                      {variableLabel(item.variable_code)}
                    </span>
                    <div style={{ background: "var(--color-background)", borderRadius: "var(--radius-sm)", overflow: "hidden", height: 14 }}>
                      <div
                        style={{
                          width: maxBreakdownCount > 0 ? `${(item.count / maxBreakdownCount) * 100}%` : "0%",
                          background: "var(--color-action)",
                          height: "100%",
                          borderRadius: "var(--radius-sm)",
                        }}
                      />
                    </div>
                    <strong style={{ textAlign: "right", fontSize: 13 }}>{item.count}</strong>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      <div
        style={{
          display: "flex",
          gap: "var(--space-4)",
          flexWrap: "wrap",
          marginBottom: "var(--space-4)",
          alignItems: "flex-end",
        }}
      >
        <div style={{ minWidth: 200 }}>
          <label htmlFor="dq-patient-search" className="caption" style={{ display: "block", marginBottom: "var(--space-2)" }}>
            Paciente
          </label>
          <input
            id="dq-patient-search"
            type="search"
            placeholder="Ej. PAT-0034"
            value={patientQuery}
            onChange={(e) => setPatientQuery(e.target.value)}
            style={inputStyle}
          />
        </div>
        <div style={{ minWidth: 160 }}>
          <label htmlFor="dq-variable" className="caption" style={{ display: "block", marginBottom: "var(--space-2)" }}>
            Variable
          </label>
          <select
            id="dq-variable"
            value={variableQuery}
            onChange={(e) => setVariableQuery(e.target.value)}
            style={inputStyle}
          >
            <option value="">Todas</option>
            {VITAL_VARIABLE_CODES.map((code) => (
              <option key={code} value={code}>
                {variableLabel(code)}
              </option>
            ))}
          </select>
        </div>
        <div style={{ minWidth: 220 }}>
          <label htmlFor="dq-search" className="caption" style={{ display: "block", marginBottom: "var(--space-2)" }}>
            Buscar
          </label>
          <input
            id="dq-search"
            type="search"
            placeholder="Variable, problema, paciente..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={inputStyle}
          />
        </div>
        {hasActiveFilters && (
          <button type="button" className="btn btn-secondary" onClick={clearFilters}>
            Limpiar filtros
          </button>
        )}
      </div>

      <div
        style={{ display: "flex", gap: "var(--space-2)", marginBottom: "var(--space-4)", flexWrap: "wrap" }}
        role="group"
        aria-label="Filtrar por tipo de incidencia"
      >
        {ISSUE_TYPE_FILTERS.map((option) => (
          <button
            key={option.value}
            type="button"
            className={`filter-chip ${typeFilter === option.value ? "filter-chip-active" : ""}`}
            onClick={() => setTypeFilter(option.value)}
            aria-pressed={typeFilter === option.value}
          >
            {option.label}
          </button>
        ))}
      </div>

      {issuesStatus === "loading" && (
        <div className="skeleton" style={{ height: 320, borderRadius: "var(--radius-md)" }} />
      )}

      {issuesStatus === "error" && (
        <div className="card state-panel">
          <p style={{ marginBottom: "var(--space-4)" }}>No fue posible cargar las incidencias.</p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => loadIssues({ type: typeFilter, patientQuery, variableQuery, searchQuery, page })}
          >
            Reintentar
          </button>
        </div>
      )}

      {issuesStatus === "ready" &&
        (issues.length === 0 ? (
          <EmptyState message="No hay incidencias que coincidan con los filtros aplicados." />
        ) : (
          <>
            <div className="card" style={{ overflowX: "auto", padding: 0 }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                    {[
                      "Paciente",
                      "Tipo",
                      "Variable",
                      "Valor original",
                      "Valor procesado",
                      "Problema detectado",
                      "Tratamiento",
                      "Fecha/Hora",
                    ].map((header) => (
                      <th
                        key={header}
                        style={{
                          textAlign: "left",
                          padding: "var(--space-3) var(--space-4)",
                          color: "var(--color-text-secondary)",
                          fontWeight: 600,
                          whiteSpace: "nowrap",
                        }}
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {issues.map((issue, index) => (
                    <tr key={`${issue.patient_id}-${issue.event_datetime}-${index}`} style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <td style={{ padding: "var(--space-3) var(--space-4)", whiteSpace: "nowrap" }}>{issue.patient_id}</td>
                      <td style={{ padding: "var(--space-3) var(--space-4)", whiteSpace: "nowrap" }}>
                        {DATA_QUALITY_ISSUE_TYPE_LABEL[issue.issue_type]}
                      </td>
                      <td style={{ padding: "var(--space-3) var(--space-4)", whiteSpace: "nowrap" }}>{issueVariableLabel(issue)}</td>
                      <td style={{ padding: "var(--space-3) var(--space-4)", whiteSpace: "nowrap" }}>{issue.value_original}</td>
                      <td style={{ padding: "var(--space-3) var(--space-4)", whiteSpace: "nowrap" }}>{issue.value_canonical}</td>
                      <td style={{ padding: "var(--space-3) var(--space-4)", minWidth: 220 }}>{issue.detected_issue}</td>
                      <td style={{ padding: "var(--space-3) var(--space-4)", whiteSpace: "nowrap" }}>
                        <span className={`role-badge ${TREATMENT_BADGE_CLASS[issue.treatment] ?? "role-badge--context"}`}>
                          {issue.treatment}
                        </span>
                      </td>
                      <td style={{ padding: "var(--space-3) var(--space-4)", whiteSpace: "nowrap" }}>
                        {formatDateTime(issue.event_datetime)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginTop: "var(--space-4)",
                flexWrap: "wrap",
                gap: "var(--space-3)",
              }}
            >
              <span className="caption">
                {total} incidencia{total === 1 ? "" : "s"} · página {page} de {totalPages}
              </span>
              <div style={{ display: "flex", gap: "var(--space-2)" }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  disabled={page <= 1}
                  onClick={() => setPage((prev) => Math.max(1, prev - 1))}
                >
                  Anterior
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  disabled={page >= totalPages}
                  onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
                >
                  Siguiente
                </button>
              </div>
            </div>
          </>
        ))}
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  padding: "var(--space-3)",
  borderRadius: "var(--radius-sm)",
  border: "1px solid var(--color-border)",
  fontSize: 14,
  color: "var(--color-text-primary)",
  outline: "none",
};
