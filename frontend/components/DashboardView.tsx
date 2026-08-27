"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { DashboardSummary, PatientSignal } from "@/lib/types";
import { formatDateTime } from "@/lib/format";
import { StatCard } from "@/components/StatCard";
import { PatientSignalCard } from "@/components/PatientSignalCard";
import { EmptyState } from "@/components/EmptyState";
import { PriorityFilterBar, PriorityFilterValue } from "@/components/PriorityFilterBar";

type LoadStatus = "loading" | "error" | "ready";

export function DashboardView() {
  const router = useRouter();
  const [status, setStatus] = useState<LoadStatus>("loading");
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [patients, setPatients] = useState<PatientSignal[]>([]);
  const [filter, setFilter] = useState<PriorityFilterValue>("ALL");
  const [isRefreshing, setIsRefreshing] = useState(false);

  const load = useCallback(
    async (priority: PriorityFilterValue, mode: "initial" | "refresh" = "initial") => {
      if (mode === "initial") {
        setStatus("loading");
      } else {
        setIsRefreshing(true);
      }

      try {
        const [summaryRes, patientsRes] = await Promise.all([
          fetch("/api/dashboard/summary", { cache: "no-store" }),
          fetch(`/api/dashboard/patients?priority=${priority}`, { cache: "no-store" }),
        ]);

        if (summaryRes.status === 401 || patientsRes.status === 401) {
          router.push("/login");
          return;
        }

        if (!summaryRes.ok || !patientsRes.ok) {
          setStatus("error");
          return;
        }

        const summaryData: DashboardSummary = await summaryRes.json();
        const patientsData: PatientSignal[] = await patientsRes.json();

        setSummary(summaryData);
        setPatients(patientsData);
        setStatus("ready");
      } catch {
        setStatus("error");
      } finally {
        setIsRefreshing(false);
      }
    },
    [router]
  );

  useEffect(() => {
    load(filter, "initial");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  function handleSelectPatient(signal: PatientSignal) {
    router.push(`/pacientes/${signal.patient_id}`);
  }

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          flexWrap: "wrap",
          gap: "var(--space-4)",
          marginBottom: "var(--space-6)",
        }}
      >
        <div>
          <h1>Dashboard clínico</h1>
          <p className="caption" style={{ marginTop: "var(--space-1)" }}>
            {summary?.last_updated
              ? `Última actualización de señales: ${formatDateTime(summary.last_updated)}`
              : "Señales de riesgo detectadas por RISA"}
          </p>
        </div>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => load(filter, "refresh")}
          disabled={isRefreshing || status === "loading"}
        >
          {isRefreshing ? "Actualizando..." : "Actualizar"}
        </button>
      </div>

      {status === "loading" && <LoadingState />}

      {status === "error" && (
        <div className="card state-panel">
          <p style={{ marginBottom: "var(--space-4)" }}>
            No fue posible cargar la información del Dashboard.
          </p>
          <button type="button" className="btn btn-primary" onClick={() => load(filter, "initial")}>
            Reintentar
          </button>
        </div>
      )}

      {status === "ready" && summary && (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "var(--space-4)",
              marginBottom: "var(--space-6)",
            }}
          >
            <StatCard label="Pacientes con señales" value={summary.patients_monitored} />
            <StatCard label="Señales activas" value={summary.active_signals} />
            <StatCard
              label="Prioridad crítica"
              value={summary.priority_critical}
              accentColor="var(--color-critical)"
            />
            <StatCard label="Prioridad alta" value={summary.priority_high} accentColor="var(--color-high)" />
            <StatCard
              label="Prioridad media"
              value={summary.priority_medium}
              accentColor="var(--color-medium)"
            />
            <StatCard label="Prioridad baja" value={summary.priority_low} accentColor="var(--color-low)" />
          </div>

          {summary.active_signals === 0 ? (
            <EmptyState message="No hay señales activas que requieren revisión en este momento." />
          ) : (
            <>
              <PriorityFilterBar value={filter} onChange={setFilter} allLabel="Todos" />

              {patients.length === 0 ? (
                <EmptyState message="No hay pacientes disponibles actualmente." />
              ) : (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
                    gap: "var(--space-4)",
                  }}
                >
                  {patients.map((signal) => (
                    <PatientSignalCard
                      key={signal.signal_id}
                      signal={signal}
                      onSelect={handleSelectPatient}
                    />
                  ))}
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}

function LoadingState() {
  return (
    <div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "var(--space-4)",
          marginBottom: "var(--space-6)",
        }}
      >
        {Array.from({ length: 5 }).map((_, index) => (
          <div key={index} className="skeleton" style={{ height: 84, borderRadius: "var(--radius-md)" }} />
        ))}
      </div>
      <p className="caption" style={{ marginBottom: "var(--space-4)" }}>
        Cargando información...
      </p>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
          gap: "var(--space-4)",
        }}
      >
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="skeleton" style={{ height: 150, borderRadius: "var(--radius-md)" }} />
        ))}
      </div>
    </div>
  );
}
