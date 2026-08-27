import pandas as pd

PATIENT_ID = "PAT-0001"

print(f"\n=== BASELINE PERSONAL DE {PATIENT_ID} ===")

# ================================================
# CARGAR TIMELINE
# ================================================

timeline = pd.read_parquet(
    f"data/processed/timelines/"
    f"{PATIENT_ID}_timeline_enriched.parquet"
)

timeline["event_datetime"] = pd.to_datetime(
    timeline["event_datetime"]
)

# ================================================
# SOLO SIGNOS VITALES
# ================================================

variables_baseline = [
    "HR",
    "RR",
    "SpO2",
    "TEMP",
    "SBP",
    "DBP"
]

vitals = timeline[
    (timeline["source_type"] == "VITAL_SIGN") &
    (timeline["variable_code"].isin(variables_baseline))
].copy()

# Convertir value nuevamente a numérico
vitals["value_numeric"] = pd.to_numeric(
    vitals["value"],
    errors="coerce"
)

# ================================================
# DEFINIR PERIODO DE CALIBRACION
# Primeras 24 horas
# ================================================

inicio = vitals["event_datetime"].min()

fin_baseline = inicio + pd.Timedelta(hours=24)

baseline_data = vitals[
    (vitals["event_datetime"] >= inicio) &
    (vitals["event_datetime"] < fin_baseline) &
    (vitals["quality_info"] == "OK") &
    (~vitals["is_plausibility_issue"])
].copy()

print("\nInicio baseline:", inicio)
print("Fin baseline:", fin_baseline)

print(
    "\nCantidad de mediciones utilizadas:",
    len(baseline_data)
)

# ================================================
# CALCULAR BASELINE
# ================================================

baseline = baseline_data.groupby(
    "variable_code"
)["value_numeric"].agg(
    [
        "count",
        "mean",
        "median",
        "std",
        "min",
        "max"
    ]
).reset_index()

print("\nBaseline:")

print(
    baseline.to_string(index=False)
)

# ================================================
# GUARDAR
# ================================================

ruta = (
    f"data/processed/"
    f"{PATIENT_ID}_baseline.parquet"
)

baseline.to_parquet(
    ruta,
    index=False
)

print("\nBaseline guardado en:")
print(ruta)

print("\n=== BASELINE TERMINADO ===")