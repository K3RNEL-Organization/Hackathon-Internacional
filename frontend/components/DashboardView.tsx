"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { DashboardSummary, PatientSignal } from "@/lib/types";
import { formatDateTime } from "@/lib/format";
import { StatCard } from "@/components/StatCard";
import { PatientSignalCard } from "@/components/PatientSignalCard";
import { EmptyState } from "@/components/EmptyState";
import { PriorityDistributionBar } from "@/components/PriorityDistributionBar";

type LoadStatus = "loading" | "error" | "ready";

const PRIORITY_SIGNALS_LIMIT = 6;

export function DashboardView() {
  const router = useRouter();
  const [status, setStatus] = useState<LoadStatus>("loading");
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [prioritySignals, setPrioritySignals] = useState<PatientSignal[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const load = useCallback(
    async (mode: "initial" | "refresh" = "initial") => {
      if (mode === "initial") {
        setStatus("loading");
      } else {
        setIsRefreshing(true);
      }

      try {
        const [summaryRes, signalsRes] = await Promise.all([
          fetch("/api/dashboard/summary", { cache: "no-store" }),
          fetch("/api/signals?priority=ALL", { cache: "no-store" }),
        ]);

        if (summaryRes.status === 401 || signalsRes.status === 401) {
          router.push("/login");
          return;
        }

        if (!summaryRes.ok || !signalsRes.ok) {
          setStatus("error");
          return;
        }

        const summaryData: DashboardSummary = await summaryRes.json();
        const allSignals: PatientSignal[] = await signalsRes.json();

        // Vista de triage: solo lo que requiere atención primero (CRITICAL/HIGH), por risk_score.
        const priority = allSignals
          .filter((s) => s.priority_level === "CRITICAL" || s.priority_level === "HIGH")
          .sort((a, b) => (b.risk_score ?? 0) - (a.risk_score ?? 0))
          .slice(0, PRIORITY_SIGNALS_LIMIT);

        setSummary(summaryData);
        setPrioritySignals(priority);
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
    load("initial");
  }, [load]);

  function handleSelectSignal(signal: PatientSignal) {
    router.push(`/senales/${signal.signal_id}`);
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
          onClick={() => load("refresh")}
          disabled={isRefreshing || status === "loading"}
        >
          {isRefreshing ? "Actualizando..." : "↻ Actualizar"}
        </button>
      </div>

      {status === "loading" && <LoadingState />}

      {status === "error" && (
        <div className="card state-panel">
          <p style={{ marginBottom: "var(--space-4)" }}>
            No fue posible cargar la información del Dashboard.
          </p>
          <button type="button" className="btn btn-primary" onClick={() => load("initial")}>
            Reintentar
          </button>
        </div>
      )}

      {status === "ready" && summary && (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "var(--space-4)",
              marginBottom: "var(--space-4)",
            }}
          >
            <StatCard label="Pacientes con señales" value={summary.patients_monitored} icon="◉" />
            <StatCard label="Total de señales" value={summary.active_signals} icon="⌁" />
          </div>

          <div className="card" style={{ marginBottom: "var(--space-6)" }}>
            <h2 style={{ marginBottom: "var(--space-5)" }}>Distribución de prioridades</h2>
            <PriorityDistributionBar
              counts={{
                critical: summary.priority_critical,
                high: summary.priority_high,
                medium: summary.priority_medium,
                low: summary.priority_low,
              }}
            />
          </div>

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: "var(--space-3)",
              marginBottom: "var(--space-4)",
            }}
          >
            <h2>Señales prioritarias</h2>
            <Link href="/senales" className="btn btn-secondary">
              Ver todas las señales →
            </Link>
          </div>

          {prioritySignals.length === 0 ? (
            <EmptyState message="No hay señales críticas o altas que requieran revisión en este momento." />
          ) : (
            <div className="card-grid">
              {prioritySignals.map((signal) => (
                <PatientSignalCard key={signal.signal_id} signal={signal} onSelect={handleSelectSignal} />
              ))}
            </div>
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
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "var(--space-4)",
          marginBottom: "var(--space-4)",
        }}
      >
        {Array.from({ length: 2 }).map((_, index) => (
          <div key={index} className="skeleton" style={{ height: 84, borderRadius: "var(--radius-md)" }} />
        ))}
      </div>
      <div className="skeleton" style={{ height: 96, borderRadius: "var(--radius-md)", marginBottom: "var(--space-6)" }} />
      <p className="caption" style={{ marginBottom: "var(--space-4)" }}>
        Cargando información...
      </p>
      <div className="card-grid">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="skeleton" style={{ height: 150, borderRadius: "var(--radius-md)" }} />
        ))}
      </div>
    </div>
  );
}
