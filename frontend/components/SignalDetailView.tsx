"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { SignalDetail, SOURCE_FILE_LABEL, variableLabel } from "@/lib/types";
import { formatDateTime, formatPercent, formatSigma } from "@/lib/format";
import { PriorityBadge } from "@/components/PriorityBadge";
import { EmptyState } from "@/components/EmptyState";
import { VariableTimeline } from "@/components/VariableTimeline";
import { Breadcrumb } from "@/components/Breadcrumb";
import { RoleBadge } from "@/components/RoleBadge";

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
      <Breadcrumb
        items={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Señales", href: "/senales" },
          { label: signal.patient_id, href: `/pacientes/${signal.patient_id}` },
          { label: signal.signal_id },
        ]}
      />

      <div
        style={{
          display: "flex",
          gap: "var(--space-3)",
          marginBottom: "var(--space-5)",
          flexWrap: "wrap",
        }}
      >
        <button type="button" className="btn btn-secondary" onClick={() => router.back()}>
          ← Volver
        </button>
        <Link href={`/pacientes/${signal.patient_id}`} className="btn btn-secondary">
          Volver al paciente
        </Link>
        <Link href="/senales" className="btn btn-secondary">
          Volver a Señales
        </Link>
      </div>

      <SignalHeader signal={signal} />

      <Section title="Qué fue detectado">
        <p style={{ color: "var(--color-text-secondary)", marginBottom: "var(--space-5)" }}>
          <strong style={{ color: "var(--color-text-primary)" }}>Patrón detectado: </strong>
          {signal.pattern_summary}
        </p>

        {signal.variable_deviations.length === 0 ? (
          <p className="caption">No hay variables cuantificadas disponibles para esta señal.</p>
        ) : (
          <div style={{ overflowX: "auto", marginBottom: "var(--space-5)" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ textAlign: "left", borderBottom: "1px solid var(--color-border)" }}>
                  <th style={thStyle}>Variable</th>
                  <th style={thStyle}>Comportamiento</th>
                  <th style={thStyle}>Desviación</th>
                </tr>
              </thead>
              <tbody>
                {signal.variable_deviations.map((deviation) => (
                  <tr key={deviation.variable_code} style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <td style={{ ...tdStyle, fontWeight: 600 }}>{variableLabel(deviation.variable_code)}</td>
                    <td
                      style={{
                        ...tdStyle,
                        color:
                          deviation.direction === "INCREASE" ? "var(--color-high)" : "var(--color-action)",
                        fontWeight: 600,
                      }}
                    >
                      {deviation.direction === "INCREASE" ? "↑ Aumento" : "↓ Descenso"}
                    </td>
                    <td style={tdStyle}>{formatSigma(deviation.z_score)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {(signal.persistence_windows !== null ||
          signal.device_quality_pct !== null ||
          signal.activity_note ||
          signal.context_note) && (
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
            {signal.persistence_windows !== null && (
              <p className="caption">
                Persistencia: {signal.persistence_windows} ventana
                {signal.persistence_windows === 1 ? "" : "s"} consecutiva
                {signal.persistence_windows === 1 ? "" : "s"}
              </p>
            )}
            {signal.device_quality_pct !== null && (
              <p className="caption">Calidad de señal: {signal.device_quality_pct.toFixed(0)}%</p>
            )}
            {signal.activity_note && <p className="caption">Contexto de actividad: {signal.activity_note}</p>}
            {signal.context_note && <p className="caption">{signal.context_note}</p>}
          </div>
        )}
      </Section>

      <Section title="Evolución temporal">
        <VariableTimeline
          evidence={signal.evidence}
          windowStart={signal.evidence_window_start}
          windowEnd={signal.evidence_window_end}
          decisionAt={signal.generated_at}
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
            label="Confianza de la evidencia"
            value={signal.confidence_score !== null ? formatPercent(signal.confidence_score) : "No disponible"}
          />
        </div>
      </Section>

      <Section title="Evidencia y trazabilidad">
        <p className="caption" style={{ marginBottom: "var(--space-2)" }}>
          Modelo: {signal.model_version}
        </p>
        <p className="caption" style={{ marginBottom: "var(--space-4)" }}>
          Todas las evidencias listadas estaban disponibles al momento de la decisión (
          {formatDateTime(signal.generated_at)}) — regla temporal de RISA: momento disponible ≤ momento
          de decisión.
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
                  <th style={thStyle}>ID de registro</th>
                  <th style={thStyle}>Momento del evento</th>
                  <th style={thStyle}>Disponible desde</th>
                  <th style={thStyle}>Rol</th>
                  <th style={thStyle}>Contribución</th>
                </tr>
              </thead>
              <tbody>
                {signal.evidence.map((record, index) => {
                  const isNonScoring =
                    record.contribution === 0 &&
                    (record.evidence_role === "CONTEXT" || record.evidence_role === "QUALITY");
                  return (
                    <tr key={index} style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <td style={tdStyle}>
                        {variableLabel(record.variable_code)}{" "}
                        <span className="caption">({record.variable_code})</span>
                      </td>
                      <td style={tdStyle}>
                        {SOURCE_FILE_LABEL[record.source_file] ?? record.source_file}{" "}
                        <span className="caption">({record.source_file})</span>
                      </td>
                      <td style={tdStyle}>
                        <span className="caption">{record.record_id}</span>
                      </td>
                      <td style={tdStyle}>{formatDateTime(record.event_datetime)}</td>
                      <td style={tdStyle}>{formatDateTime(record.available_datetime)}</td>
                      <td style={tdStyle}>
                        <RoleBadge role={record.evidence_role} />
                      </td>
                      <td style={tdStyle}>
                        {isNonScoring ? (
                          <span
                            title="Esta evidencia contextualiza o aporta calidad, pero no incrementa directamente el score."
                            style={{ cursor: "help", color: "var(--color-text-muted)" }}
                          >
                            —
                          </span>
                        ) : (
                          record.contribution.toFixed(2)
                        )}
                      </td>
                    </tr>
                  );
                })}
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
          <p className="caption">ID de paciente</p>
          <h1 style={{ fontSize: 22 }}>{signal.patient_id}</h1>
          <p className="caption" style={{ marginTop: "var(--space-1)" }}>
            {signal.signal_id}
          </p>
        </div>
        <div style={{ textAlign: "right" }}>
          <PriorityBadge priority={signal.priority_level} />
          {signal.risk_score !== null && (
            <p className="caption" style={{ marginTop: "var(--space-1)" }}>
              Score de riesgo: {signal.risk_score.toFixed(2)}
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
