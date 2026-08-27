"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { PatientSignal } from "@/lib/types";
import { PatientSignalCard } from "@/components/PatientSignalCard";
import { EmptyState } from "@/components/EmptyState";
import { PriorityFilterBar, PriorityFilterValue } from "@/components/PriorityFilterBar";
import { Breadcrumb } from "@/components/Breadcrumb";

type LoadStatus = "loading" | "error" | "ready";

export function SignalsView() {
  const router = useRouter();
  const [status, setStatus] = useState<LoadStatus>("loading");
  const [signals, setSignals] = useState<PatientSignal[]>([]);
  const [priorityFilter, setPriorityFilter] = useState<PriorityFilterValue>("ALL");
  const [patientQuery, setPatientQuery] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const load = useCallback(
    async (priority: PriorityFilterValue) => {
      setStatus("loading");
      try {
        const response = await fetch(`/api/signals?priority=${priority}`, { cache: "no-store" });

        if (response.status === 401) {
          router.push("/login");
          return;
        }

        if (!response.ok) {
          setStatus("error");
          return;
        }

        const data: PatientSignal[] = await response.json();
        // Explorador completo: orden por risk_score descendente por defecto.
        data.sort((a, b) => (b.risk_score ?? 0) - (a.risk_score ?? 0));
        setSignals(data);
        setStatus("ready");
      } catch {
        setStatus("error");
      }
    },
    [router]
  );

  useEffect(() => {
    load(priorityFilter);
  }, [priorityFilter, load]);

  const filteredSignals = useMemo(() => {
    const patientQueryUpper = patientQuery.trim().toUpperCase();
    return signals.filter((signal) => {
      if (patientQueryUpper && !signal.patient_id.toUpperCase().includes(patientQueryUpper)) {
        return false;
      }
      const signalDate = signal.generated_at.slice(0, 10);
      if (dateFrom && signalDate < dateFrom) return false;
      if (dateTo && signalDate > dateTo) return false;
      return true;
    });
  }, [signals, patientQuery, dateFrom, dateTo]);

  const hasActiveFilters = Boolean(patientQuery || dateFrom || dateTo);

  function handleSelectSignal(signal: PatientSignal) {
    router.push(`/senales/${signal.signal_id}`);
  }

  function clearFilters() {
    setPatientQuery("");
    setDateFrom("");
    setDateTo("");
  }

  return (
    <div>
      <Breadcrumb items={[{ label: "Dashboard", href: "/dashboard" }, { label: "Señales" }]} />

      <div style={{ marginBottom: "var(--space-6)" }}>
        <h1>Señales RISA</h1>
        <p className="caption" style={{ marginTop: "var(--space-1)" }}>
          Explorador completo de señales detectadas, ordenadas por score de riesgo.
        </p>
      </div>

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
          <label htmlFor="signal-patient-search" className="caption" style={{ display: "block", marginBottom: "var(--space-2)" }}>
            Paciente
          </label>
          <input
            id="signal-patient-search"
            type="search"
            placeholder="Ej. PAT-0034"
            value={patientQuery}
            onChange={(e) => setPatientQuery(e.target.value)}
            style={inputStyle}
          />
        </div>
        <div>
          <label htmlFor="signal-date-from" className="caption" style={{ display: "block", marginBottom: "var(--space-2)" }}>
            Desde
          </label>
          <input
            id="signal-date-from"
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            style={inputStyle}
          />
        </div>
        <div>
          <label htmlFor="signal-date-to" className="caption" style={{ display: "block", marginBottom: "var(--space-2)" }}>
            Hasta
          </label>
          <input
            id="signal-date-to"
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            style={inputStyle}
          />
        </div>
        {hasActiveFilters && (
          <button type="button" className="btn btn-secondary" onClick={clearFilters}>
            Limpiar filtros
          </button>
        )}
      </div>

      <PriorityFilterBar value={priorityFilter} onChange={setPriorityFilter} />

      {status === "loading" && <LoadingState />}

      {status === "error" && (
        <div className="card state-panel">
          <p style={{ marginBottom: "var(--space-4)" }}>No fue posible cargar las señales.</p>
          <button type="button" className="btn btn-primary" onClick={() => load(priorityFilter)}>
            Reintentar
          </button>
        </div>
      )}

      {status === "ready" &&
        (signals.length === 0 ? (
          <EmptyState
            message={
              priorityFilter === "ALL"
                ? "No hay señales que requieren revisión actualmente."
                : "No hay señales con esta prioridad en este momento."
            }
          />
        ) : filteredSignals.length === 0 ? (
          <EmptyState message="Ninguna señal coincide con los filtros aplicados." />
        ) : (
          <div className="card-grid">
            {filteredSignals.map((signal) => (
              <PatientSignalCard key={signal.signal_id} signal={signal} onSelect={handleSelectSignal} />
            ))}
          </div>
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

function LoadingState() {
  return (
    <div className="card-grid">
      {Array.from({ length: 6 }).map((_, index) => (
        <div key={index} className="skeleton" style={{ height: 150, borderRadius: "var(--radius-md)" }} />
      ))}
    </div>
  );
}
