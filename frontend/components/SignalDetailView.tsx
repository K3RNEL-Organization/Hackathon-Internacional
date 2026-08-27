"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { SignalDetail, SOURCE_FILE_LABEL } from "@/lib/types";
import { formatDateTime } from "@/lib/format";
import { PriorityBadge } from "@/components/PriorityBadge";
import { EmptyState } from "@/components/EmptyState";
import { VariableTimeline } from "@/components/VariableTimeline";

type LoadStatus = "loading" | "error" | "not_found" | "ready";

export function SignalDetailView({ signalId }: { signalId: string }) {
  const router = useRouter();
  const [status, setStatus] = useState<LoadStatus>("loading");
  const [signal, setSignal] = useState<SignalDetail | null>(null);

  const load = useCallback(async () => {
    setStatus("loading");
    try {
      const response = await fetch(`/api/signals/${encodeURIComponent(signalId)}`, {
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

      const data: SignalDetail = await response.json();
      setSignal(data);
      setStatus("ready");
    } catch {
      setStatus("error");
    }
  }, [signalId, router]);

  useEffect(() => {
    load();
  }, [load]);

  if (status === "loading") {
    return <LoadingState />;
  }

  if (status === "not_found") {
    return <EmptyState message="Señal no encontrada." />;
  }

  if (status === "error" || !signal) {
    return (
      <div className="card state-panel">
        <p style={{ marginBottom: "var(--space-4)" }}>
          No fue posible cargar la información de la señal.
        </p>
        <button type="button" className="btn btn-primary" onClick={load}>
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div>
      <div
        style={{
          display: "flex",
          gap: "var(--space-3)",
          marginBottom: "var(--space-5)",
          flexWrap: "wrap",
        }}
      >
        <Link href={`/pacientes/${signal.patient_id}`} className="btn btn-secondary">
          Volver al paciente
        </Link>
        <Link href="/senales" className="btn btn-secondary">
          Volver a Señales
        </Link>
      </div>

      <SignalHeader signal={signal} />

      <Section title="Qué fue detectado">
        <p style={{ color: "var(--color-text-secondary)" }}>{signal.explanation}</p>
      </Section>

      <Section title="Variables involucradas">
        {signal.variable_deviations.length === 0 ? (
          <p className="caption">No hay variables cuantificadas disponibles para esta señal.</p>
        ) : (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-3)" }}>
            {signal.variable_deviations.map((deviation) => (
              <div
                key={deviation.variable_code}
                className="card"
                style={{ padding: "var(--space-3) var(--space-4)", minWidth: 140 }}
              >
                <p style={{ fontWeight: 700 }}>{deviation.variable_code}</p>
                <p
                  className="caption"
                  style={{
                    color:
                      deviation.direction === "INCREASE" ? "var(--color-high)" : "var(--color-action)",
                    fontWeight: 600,
                  }}
                >
                  {deviation.direction === "INCREASE" ? "▲ Aumento" : "▼ Descenso"} ·{" "}
                  {deviation.z_score.toFixed(2)} z
                </p>
              </div>
            ))}
          </div>
        )}
      </Section>

      <Section title="Evolución temporal">
        <VariableTimeline
          evidence={signal.evidence}
          windowStart={signal.evidence_window_start}
          windowEnd={signal.evidence_window_end}
        />
      </Section>

      <Section title="Por qué se asignó esta prioridad">
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
            gap: "var(--space-4)",
          }}
        >
          <InfoField label="Nivel de prioridad" value={<PriorityBadge priority={signal.priority_level} />} />
          <InfoField
            label="Score de riesgo"
            value={signal.risk_score !== null ? signal.risk_score.toFixed(2) : "No disponible"}
          />
          <InfoField
            label="Confianza del modelo"
            value={signal.confidence_score !== null ? signal.confidence_score.toFixed(2) : "No disponible"}
          />
        </div>
      </Section>

      <Section title="Evidencia y trazabilidad">
        <p className="caption" style={{ marginBottom: "var(--space-4)" }}>
          Modelo: {signal.model_version}
        </p>
        {signal.evidence.length === 0 ? (
          <p className="caption">No hay evidencia disponible para esta señal.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ textAlign: "left", borderBottom: "1px solid var(--color-border)" }}>
                  <th style={thStyle}>Variable</th>
                  <th style={thStyle}>Fuente</th>
                  <th style={thStyle}>Momento del evento</th>
                  <th style={thStyle}>Disponible desde</th>
                  <th style={thStyle}>Rol</th>
                  <th style={thStyle}>Contribución</th>
                </tr>
              </thead>
              <tbody>
                {signal.evidence.map((record, index) => (
                  <tr key={index} style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <td style={tdStyle}>{record.variable_code}</td>
                    <td style={tdStyle}>{SOURCE_FILE_LABEL[record.source_file] ?? record.source_file}</td>
                    <td style={tdStyle}>{formatDateTime(record.event_datetime)}</td>
                    <td style={tdStyle}>{formatDateTime(record.available_datetime)}</td>
                    <td style={tdStyle}>{record.evidence_role}</td>
                    <td style={tdStyle}>{record.contribution.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Section>
    </div>
  );
}

function SignalHeader({ signal }: { signal: SignalDetail }) {
  return (
    <div className="card" style={{ marginBottom: "var(--space-5)" }}>
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
          <h1 style={{ fontSize: 22 }}>{signal.patient_id}</h1>
          <p className="caption" style={{ marginTop: "var(--space-1)" }}>
            {signal.signal_id}
          </p>
        </div>
        <div style={{ textAlign: "right" }}>
          <PriorityBadge priority={signal.priority_level} />
          {signal.risk_score !== null && (
            <p className="caption" style={{ marginTop: "var(--space-1)" }}>
              Score: {signal.risk_score.toFixed(2)}
            </p>
          )}
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "var(--space-4)",
          marginTop: "var(--space-5)",
        }}
      >
        <InfoField label="Fecha y hora de generación" value={formatDateTime(signal.generated_at)} />
        <InfoField label="Modelo" value={signal.model_version} />
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card" style={{ marginBottom: "var(--space-5)" }}>
      <h2 style={{ marginBottom: "var(--space-4)" }}>{title}</h2>
      {children}
    </div>
  );
}

function InfoField({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <p className="caption">{label}</p>
      <div style={{ fontWeight: 600, marginTop: "var(--space-1)" }}>{value}</div>
    </div>
  );
}

const thStyle: React.CSSProperties = {
  padding: "var(--space-2) var(--space-3)",
  color: "var(--color-text-secondary)",
  fontWeight: 600,
  whiteSpace: "nowrap",
};

const tdStyle: React.CSSProperties = {
  padding: "var(--space-2) var(--space-3)",
  whiteSpace: "nowrap",
};

function LoadingState() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
      <div className="skeleton" style={{ height: 140, borderRadius: "var(--radius-md)" }} />
      <div className="skeleton" style={{ height: 100, borderRadius: "var(--radius-md)" }} />
      <div className="skeleton" style={{ height: 180, borderRadius: "var(--radius-md)" }} />
    </div>
  );
}
