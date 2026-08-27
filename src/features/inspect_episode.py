import pandas as pd

PATIENT_ID = "PAT-0001"

EPISODE_START = pd.Timestamp("2026-07-12 10:00:00")
EPISODE_END = pd.Timestamp("2026-07-12 23:00:00")

print(f"\n=== INSPECCION EPISODIO {PATIENT_ID} ===")
print("Desde:", EPISODE_START)
print("Hasta:", EPISODE_END)


# ==================================================
# CARGAR TIMELINE ENRIQUECIDA
# ==================================================

timeline = pd.read_parquet(
    f"data/processed/timelines/"
    f"{PATIENT_ID}_timeline_enriched.parquet"
)

timeline["event_datetime"] = pd.to_datetime(
    timeline["event_datetime"]
)

timeline["available_datetime"] = pd.to_datetime(
    timeline["available_datetime"]
)


# ==================================================
# FILTRAR EPISODIO
# ==================================================

episode = timeline[
    (timeline["event_datetime"] >= EPISODE_START) &
    (timeline["event_datetime"] <= EPISODE_END)
].copy()

print("\nCantidad de eventos:", len(episode))


# ==================================================
# 1. SIGNOS VITALES
# ==================================================

vitals = episode[
    episode["source_type"] == "VITAL_SIGN"
].copy()

vitals["value_numeric"] = pd.to_numeric(
    vitals["value"],
    errors="coerce"
)

resumen_vitales = vitals.groupby(
    "variable_code"
)["value_numeric"].agg(
    ["count", "mean", "min", "max"]
)

print("\n=== RESUMEN VITALES ===")
print(resumen_vitales)


# ==================================================
# 2. CALIDAD
# ==================================================

print("\n=== QUALITY FLAGS ===")

print(
    vitals["quality_info"].value_counts(
        dropna=False
    )
)

print(
    "\nProblemas de plausibilidad:",
    vitals["is_plausibility_issue"].sum()
)


# ==================================================
# 3. CONTEXTO
# ==================================================

print("\n=== SUEÑO ===")

print(
    episode["sleep_state"].value_counts(
        dropna=False
    )
)

print("\n=== ACTIVIDAD ===")

print(
    episode["activity_level"].value_counts(
        dropna=False
    )
)

print("\n=== RECUPERACION ===")

print(
    episode["recovery_phase"].value_counts(
        dropna=False
    )
)


# ==================================================
# 4. CONECTIVIDAD
# ==================================================

print("\n=== CONECTIVIDAD ===")

print(
    episode["connectivity_status"].value_counts(
        dropna=False
    )
)


# ==================================================
# 5. WEARABLE
# ==================================================

wearable = episode[
    episode["source_type"] == "WEARABLE"
].copy()

print("\n=== ACTIVIDAD SEGUN WEARABLE ===")

actividad_wearable = wearable[
    wearable["variable_code"] == "ACTIVITY_LEVEL"
]

print(
    actividad_wearable["value"].value_counts(
        dropna=False
    )
)


# ==================================================
# 6. CALIDAD DEL DISPOSITIVO
# ==================================================

device_quality = episode[
    episode["source_type"] == "DEVICE_QUALITY"
].copy()

print("\n=== DEVICE QUALITY ===")

if len(device_quality) > 0:

    device_quality["quality_numeric"] = pd.to_numeric(
        device_quality["value"],
        errors="coerce"
    )

    print(
        device_quality["quality_numeric"].describe()
    )

else:
    print("Sin observaciones de calidad en el periodo.")


# ==================================================
# 7. LABORATORIOS DISPONIBLES
# ==================================================

labs = episode[
    episode["source_type"] == "LABORATORY"
]

print("\n=== LABORATORIOS ===")

if len(labs) > 0:

    print(
        labs[
            [
                "variable_code",
                "value",
                "unit",
                "event_datetime",
                "available_datetime"
            ]
        ].to_string(index=False)
    )

else:
    print("Sin laboratorios durante este episodio.")


# ==================================================
# 8. EVOLUCION HORARIA
# ==================================================

print("\n=== EVOLUCION DE VITALES ===")

tabla = vitals.pivot_table(
    index="event_datetime",
    columns="variable_code",
    values="value_numeric",
    aggfunc="mean"
)

print(
    tabla.tail(50).to_string()
)

print("\n=== FIN INSPECCION ===")