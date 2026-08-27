"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { PatientDetail, PRIORITY_LABEL, TimelineEventType } from "@/lib/types";
import { formatDateTime } from "@/lib/format";
import { PriorityBadge } from "@/components/PriorityBadge";
import { PatientSignalCard } from "@/components/PatientSignalCard";
import { EmptyState } from "@/components/EmptyState";

type LoadStatus = "loading" | "error" | "not_found" | "ready";

type TabKey =
  | "resumen"
  | "evolucion"
  | "vitales"
  | "laboratorios"
  | "wearables"
  | "timeline"
  | "senales";

const TABS: { key: TabKey; label: string }[] = [
  { key: "resumen", label: "Resumen" },
  { key: "evolucion", label: "Evolución temporal" },
  { key: "vitales", label: "Signos vitales" },
  { key: "laboratorios", label: "Laboratorios" },
  { key: "wearables", label: "Wearables" },
  { key: "timeline", label: "Timeline" },
  { key: "senales", label: "Señales asociadas" },
];

const TIMELINE_LABEL: Record<TimelineEventType, string> = {
  SIGNAL_DETECTED: "Señal detectada",
  ENCOUNTER_START: "Inicio del episodio de monitoreo",
  ENCOUNTER_END: "Fin del episodio de monitoreo",
  CONDITION_RECORDED: "Antecedente registrado",
};

export function PatientDetailView({ patientId }: { patientId: string }) {
  const router = useRouter();
  const [status, setStatus] = useState<LoadStatus>("loading");
  const [patient, setPatient] = useState<PatientDetail | null>(null);
  const [tab, setTab] = useState<TabKey>("resumen");

  const load = useCallback(async () => {
    setStatus("loading");
    try {
      const response = await fetch(`/api/patients/${encodeURIComponent(patientId)}`, {
        cache: "no-store",
      });

      if (response.status === 401) {
        router.push("/login");
        return;
      }

      if (response.status === 404) {
        setStatus("not_found");
        return;
      }

      if (!response.ok) {
        setStatus("error");
        return;
      }

      const data: PatientDetail = await response.json();
      setPatient(data);
      setStatus("ready");
    } catch {
      setStatus("error");
    }
  }, [patientId, router]);

  useEffect(() => {
    load();
  }, [load]);

  if (status === "loading") {
    return <LoadingState />;
  }

  if (status === "not_found") {
    return <EmptyState message="Paciente no encontrado." />;
  }

  if (status === "error" || !patient) {
    return (
      <div className="card state-panel">
        <p style={{ marginBottom: "var(--space-4)" }}>
          No fue posible cargar la información del paciente.
        </p>
        <button type="button" className="btn btn-primary" onClick={load}>
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div>
      <PatientHeader patient={patient} />

      <div
        style={{
          display: "flex",
          gap: "var(--space-2)",
          flexWrap: "wrap",
          marginTop: "var(--space-6)",
          marginBottom: "var(--space-4)",
        }}
        role="tablist"
        aria-label="Secciones del paciente"
      >
        {TABS.map((option) => (
          <button
            key={option.key}
            type="button"
            role="tab"
            aria-selected={tab === option.key}
            className={`filter-chip ${tab === option.key ? "filter-chip-active" : ""}`}
            onClick={() => setTab(option.key)}
          >
            {option.label}
          </button>
        ))}
      </div>

      {tab === "resumen" && <ResumenTab patient={patient} />}
      {tab === "evolucion" && (
        <EmptyState message="No hay datos de evolución temporal disponibles para este paciente." />
      )}
      {tab === "vitales" && <EmptyState message="Información no disponible." />}
      {tab === "laboratorios" && <EmptyState message="Información no disponible." />}
      {tab === "wearables" && <EmptyState message="Información no disponible." />}
      {tab === "timeline" && <TimelineTab patient={patient} />}
      {tab === "senales" && <SenalesTab patient={patient} />}
    </div>
  );
}

function PatientHeader({ patient }: { patient: PatientDetail }) {
  return (
    <div className="card">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          flexWrap: "wrap",
          gap: "var(--space-4)",
        }}
      >
        <div>
          <p className="caption">Patient ID</p>
          <h1 style={{ fontSize: 22 }}>{patient.patient_id}</h1>
        </div>

        {patient.current_priority ? (
          <div style={{ textAlign: "right" }}>
            <PriorityBadge priority={patient.current_priority} />
            {patient.current_risk_score !== null && (
              <p className="caption" style={{ marginTop: "var(--space-1)" }}>
                Score: {patient.current_risk_score.toFixed(2)}
              </p>
            )}
          </div>
        ) : (
          <p className="caption">Sin señal registrada</p>
        )}
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "var(--space-4)",
          marginTop: "var(--space-5)",
        }}
      >
        <InfoField
          label="Última señal detectada"
          value={patient.last_signal_at ? formatDateTime(patient.last_signal_at) : "No disponible"}
        />
        <InfoField
          label="Última actualización"
          value={patient.last_updated ? formatDateTime(patient.last_updated) : "No disponible"}
        />
        <InfoField
          label="Encounter actual"
          value={
            patient.encounter
              ? `${patient.encounter.encounter_id} · desde ${formatDateTime(patient.encounter.start)}`
              : "No disponible"
          }
        />
      </div>
    </div>
  );
}

function InfoField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="caption">{label}</p>
      <p style={{ fontWeight: 600 }}>{value}</p>
    </div>
  );
}

function ResumenTab({ patient }: { patient: PatientDetail }) {
  return (
    <div className="card">
      <h2 style={{ marginBottom: "var(--space-4)" }}>Antecedentes</h2>
      {patient.conditions.length === 0 ? (
        <p className="caption">Información no disponible.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
          {patient.conditions.map((condition, index) => (
            <div
              key={index}
              style={{
                display: "flex",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: "var(--space-2)",
                paddingBottom: "var(--space-3)",
                borderBottom:
                  index < patient.conditions.length - 1 ? "1px solid var(--color-border)" : "none",
              }}
            >
              <span style={{ fontWeight: 600 }}>{condition.category.replaceAll("_", " ")}</span>
              <span className="caption">{condition.status}</span>
              <span className="caption">{formatDateTime(condition.recorded_at)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function TimelineTab({ patient }: { patient: PatientDetail }) {
  if (patient.timeline.length === 0) {
    return <EmptyState message="No hay eventos registrados para este paciente." />;
  }

  return (
    <div className="card">
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
        {patient.timeline.map((event, index) => (
          <div
            key={index}
            style={{
              display: "flex",
              gap: "var(--space-3)",
              alignItems: "flex-start",
              paddingBottom: "var(--space-4)",
              borderBottom:
                index < patient.timeline.length - 1 ? "1px solid var(--color-border)" : "none",
            }}
          >
            <span
              className="caption"
              style={{ minWidth: 150, fontWeight: 600, color: "var(--color-text-primary)" }}
            >
              {formatDateTime(event.timestamp)}
            </span>
            <div>
              <p style={{ fontWeight: 600 }}>{TIMELINE_LABEL[event.type]}</p>
              <p className="caption">
                {event.label}
                {event.priority_level ? ` · ${PRIORITY_LABEL[event.priority_level]}` : ""}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SenalesTab({ patient }: { patient: PatientDetail }) {
  const router = useRouter();

  if (patient.signals.length === 0) {
    return <EmptyState message="No hay señales activas para este paciente." />;
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
        gap: "var(--space-4)",
      }}
    >
      {patient.signals.map((signal) => (
        <PatientSignalCard
          key={signal.signal_id}
          signal={signal}
          onSelect={(selected) => router.push(`/senales/${selected.signal_id}`)}
        />
      ))}
    </div>
  );
}

function LoadingState() {
  return (
    <div>
      <div className="skeleton" style={{ height: 160, borderRadius: "var(--radius-md)" }} />
      <p className="caption" style={{ margin: "var(--space-4) 0" }}>
        Cargando información...
      </p>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
          gap: "var(--space-4)",
        }}
      >
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="skeleton" style={{ height: 130, borderRadius: "var(--radius-md)" }} />
        ))}
      </div>
    </div>
  );
}
