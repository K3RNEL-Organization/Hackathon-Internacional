"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { PatientSignal, Priority } from "@/lib/types";
import { PatientSummaryCard, PatientSummary } from "@/components/PatientSummaryCard";
import { EmptyState } from "@/components/EmptyState";
import { Breadcrumb } from "@/components/Breadcrumb";

type LoadStatus = "loading" | "error" | "ready";

const PRIORITY_RANK: Record<Priority, number> = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };

function buildPatientSummaries(signals: PatientSignal[]): PatientSummary[] {
  const byPatient = new Map<string, PatientSignal[]>();
  for (const signal of signals) {
    const list = byPatient.get(signal.patient_id) ?? [];
    list.push(signal);
    byPatient.set(signal.patient_id, list);
  }

  const summaries: PatientSummary[] = [];
  for (const [patient_id, patientSignals] of byPatient) {
    const max_priority = patientSignals.reduce<Priority>(
      (worst, s) => (PRIORITY_RANK[s.priority_level] < PRIORITY_RANK[worst] ? s.priority_level : worst),
      patientSignals[0].priority_level
    );
    const last_signal_at = patientSignals.reduce(
      (latest, s) => (s.generated_at > latest ? s.generated_at : latest),
      patientSignals[0].generated_at
    );
    summaries.push({ patient_id, signal_count: patientSignals.length, max_priority, last_signal_at });
  }

  return summaries.sort((a, b) => {
    const rankDiff = PRIORITY_RANK[a.max_priority] - PRIORITY_RANK[b.max_priority];
    return rankDiff !== 0 ? rankDiff : b.last_signal_at.localeCompare(a.last_signal_at);
  });
}

export function PacientesView() {
  const router = useRouter();
  const [status, setStatus] = useState<LoadStatus>("loading");
  const [patients, setPatients] = useState<PatientSummary[]>([]);
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    setStatus("loading");
    try {
      const response = await fetch("/api/signals?priority=ALL", { cache: "no-store" });

      if (response.status === 401) {
        router.push("/login");
        return;
      }

      if (!response.ok) {
        setStatus("error");
        return;
      }

      const data: PatientSignal[] = await response.json();
      setPatients(buildPatientSummaries(data));
      setStatus("ready");
    } catch {
      setStatus("error");
    }
  }, [router]);

  useEffect(() => {
    load();
  }, [load]);

  const filteredPatients = useMemo(() => {
    const query = search.trim().toUpperCase();
    if (!query) return patients;
    return patients.filter((p) => p.patient_id.toUpperCase().includes(query));
  }, [patients, search]);

  function handleSelectPatient(patientId: string) {
    router.push(`/pacientes/${patientId}`);
  }

  return (
    <div>
      <Breadcrumb items={[{ label: "Dashboard", href: "/dashboard" }, { label: "Pacientes" }]} />

      <div style={{ marginBottom: "var(--space-6)" }}>
        <h1>Pacientes</h1>
        <p className="caption" style={{ marginTop: "var(--space-1)" }}>
          Pacientes con señales detectadas por RISA. Cada tarjeta abre la historia completa del paciente.
        </p>
      </div>

      <div style={{ marginBottom: "var(--space-5)", maxWidth: 320 }}>
        <label htmlFor="patient-search" className="caption" style={{ display: "block", marginBottom: "var(--space-2)" }}>
          Buscar por ID de paciente
        </label>
        <input
          id="patient-search"
          type="search"
          placeholder="Ej. PAT-0034"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            width: "100%",
            padding: "var(--space-3)",
            borderRadius: "var(--radius-sm)",
            border: "1px solid var(--color-border)",
            fontSize: 14,
            color: "var(--color-text-primary)",
            outline: "none",
          }}
        />
      </div>

      {status === "loading" && <LoadingState />}

      {status === "error" && (
        <div className="card state-panel">
          <p style={{ marginBottom: "var(--space-4)" }}>No fue posible cargar los pacientes.</p>
          <button type="button" className="btn btn-primary" onClick={load}>
            Reintentar
          </button>
        </div>
      )}

      {status === "ready" &&
        (patients.length === 0 ? (
          <EmptyState message="No hay pacientes disponibles actualmente." />
        ) : filteredPatients.length === 0 ? (
          <EmptyState message="Ningún paciente coincide con esa búsqueda." />
        ) : (
          <div className="card-grid">
            {filteredPatients.map((patient) => (
              <PatientSummaryCard
                key={patient.patient_id}
                patient={patient}
                onSelect={handleSelectPatient}
              />
            ))}
          </div>
        ))}
    </div>
  );
}

function LoadingState() {
  return (
    <div className="card-grid">
      {Array.from({ length: 6 }).map((_, index) => (
        <div key={index} className="skeleton" style={{ height: 130, borderRadius: "var(--radius-md)" }} />
      ))}
    </div>
  );
}
