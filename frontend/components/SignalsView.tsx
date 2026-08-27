"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { PatientSignal } from "@/lib/types";
import { PatientSignalCard } from "@/components/PatientSignalCard";
import { EmptyState } from "@/components/EmptyState";
import { PriorityFilterBar, PriorityFilterValue } from "@/components/PriorityFilterBar";

type LoadStatus = "loading" | "error" | "ready";

export function SignalsView() {
  const router = useRouter();
  const [status, setStatus] = useState<LoadStatus>("loading");
  const [signals, setSignals] = useState<PatientSignal[]>([]);
  const [filter, setFilter] = useState<PriorityFilterValue>("ALL");

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
        setSignals(data);
        setStatus("ready");
      } catch {
        setStatus("error");
      }
    },
    [router]
  );

  useEffect(() => {
    load(filter);
  }, [filter, load]);

  function handleSelectSignal(signal: PatientSignal) {
    router.push(`/senales/${signal.signal_id}`);
  }

  return (
    <div>
      <div style={{ marginBottom: "var(--space-6)" }}>
        <h1>Señales RISA</h1>
        <p className="caption" style={{ marginTop: "var(--space-1)" }}>
          Señales detectadas que requieren revisión profesional, ordenadas por prioridad.
        </p>
      </div>

      <PriorityFilterBar value={filter} onChange={setFilter} />

      {status === "loading" && <LoadingState />}

      {status === "error" && (
        <div className="card state-panel">
          <p style={{ marginBottom: "var(--space-4)" }}>No fue posible cargar las señales.</p>
          <button type="button" className="btn btn-primary" onClick={() => load(filter)}>
            Reintentar
          </button>
        </div>
      )}

      {status === "ready" &&
        (signals.length === 0 ? (
          <EmptyState
            message={
              filter === "ALL"
                ? "No hay señales que requieren revisión actualmente."
                : "No hay señales con esta prioridad en este momento."
            }
          />
        ) : (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
              gap: "var(--space-4)",
            }}
          >
            {signals.map((signal) => (
              <PatientSignalCard key={signal.signal_id} signal={signal} onSelect={handleSelectSignal} />
            ))}
          </div>
        ))}
    </div>
  );
}

function LoadingState() {
  return (
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
  );
}
