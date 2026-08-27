"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertFunnelSummary } from "@/lib/types";
import { Breadcrumb } from "@/components/Breadcrumb";
import { StatCard } from "@/components/StatCard";

type LoadStatus = "loading" | "error" | "ready";

function formatNumber(value: number): string {
  return value.toLocaleString("es-AR");
}

export function AlertControlView() {
  const router = useRouter();
  const [status, setStatus] = useState<LoadStatus>("loading");
  const [summary, setSummary] = useState<AlertFunnelSummary | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setStatus("loading");
      try {
        const response = await fetch("/api/alert-control/funnel-summary", { cache: "no-store" });

        if (response.status === 401) {
          router.push("/login");
          return;
        }

        if (!response.ok) {
          if (!cancelled) setStatus("error");
          return;
        }

        const data: AlertFunnelSummary = await response.json();
        if (!cancelled) {
          setSummary(data);
          setStatus("ready");
        }
      } catch {
        if (!cancelled) setStatus("error");
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [router]);

  const steps = summary
    ? [
        { label: "Ventanas evaluadas", value: summary.windows_evaluated },
        { label: "Desviación detectada (≥1 variable)", value: summary.windows_with_deviation },
        { label: "Desviación multivariable (≥2 variables)", value: summary.windows_with_multivariable_deviation },
        { label: "Persistencia temporal confirmada", value: summary.persistence_confirmed_cases },
        { label: "Episodios consolidados", value: summary.consolidated_episodes },
        { label: "Señales finales", value: summary.final_signals },
      ]
    : [];

  const maxStepValue = steps.length > 0 ? steps[0].value : 0;

  return (
    <div>
      <Breadcrumb items={[{ label: "Dashboard", href: "/dashboard" }, { label: "Control de alertas" }]} />

      <div style={{ marginBottom: "var(--space-4)" }}>
        <h1>Control de alertas</h1>
        <p className="caption" style={{ marginTop: "var(--space-2)", fontSize: 13 }}>
          Cómo se filtran las ventanas de datos hasta convertirse en una señal final.
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
          TriageMed no convierte cada anomalía en una alerta. Exige desviación multivariable, persistencia
          temporal y contexto antes de generar una señal.
        </p>
      </div>

      {status === "loading" && (
        <div className="skeleton" style={{ height: 420, borderRadius: "var(--radius-md)" }} />
      )}

      {status === "error" && (
        <div className="card state-panel">
          <p>No fue posible cargar el resumen de control de alertas.</p>
        </div>
      )}

      {status === "ready" && summary && (
        <>
          <div className="card" style={{ marginBottom: "var(--space-6)" }}>
            <h3 style={{ marginBottom: "var(--space-5)" }}>Embudo de detección</h3>
            <div style={{ display: "grid", gap: "var(--space-2)" }}>
              {steps.map((step, index) => (
                <div key={step.label}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "baseline",
                      marginBottom: "var(--space-2)",
                    }}
                  >
                    <span style={{ fontSize: 13, fontWeight: 600 }}>{step.label}</span>
                    <strong style={{ fontFamily: "var(--font-space-grotesk), system-ui, sans-serif", fontSize: 18 }}>
                      {formatNumber(step.value)}
                    </strong>
                  </div>
                  <div
                    style={{
                      background: "var(--color-background)",
                      borderRadius: "var(--radius-sm)",
                      overflow: "hidden",
                      height: 10,
                    }}
                  >
                    <div
                      style={{
                        width: maxStepValue > 0 ? `${(step.value / maxStepValue) * 100}%` : "0%",
                        background: "var(--color-action)",
                        height: "100%",
                        borderRadius: "var(--radius-sm)",
                      }}
                    />
                  </div>
                  {index < steps.length - 1 && (
                    <div style={{ textAlign: "center", color: "var(--color-text-muted)", fontSize: 12, margin: "var(--space-2) 0" }}>
                      ↓
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="card-grid">
            <StatCard label="Señales finales" value={summary.final_signals} />
            <StatCard label="Retransmisiones excluidas" value={summary.retransmissions_excluded} />
            <StatCard
              label="Reducción desde candidatos multivariables"
              value={`${summary.candidate_reduction_pct}%`}
            />
          </div>
        </>
      )}
    </div>
  );
}
