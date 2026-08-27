import pandas as pd
import numpy as np
import os

PATIENT_ID = "PAT-0001"

WINDOW_HOURS = 4
STEP_HOURS = 1

print(f"\n=== FEATURES DE {PATIENT_ID} ===")


# ==================================================
# CARGAR DATOS
# ==================================================

timeline = pd.read_parquet(
    f"data/processed/timelines/"
    f"{PATIENT_ID}_timeline_enriched.parquet"
)

baseline = pd.read_parquet(
    f"data/processed/"
    f"{PATIENT_ID}_baseline.parquet"
)

timeline["event_datetime"] = pd.to_datetime(
    timeline["event_datetime"]
)

timeline["available_datetime"] = pd.to_datetime(
    timeline["available_datetime"]
)


# ==================================================
# PREPARAR BASELINE
# ==================================================

baseline_dict = baseline.set_index(
    "variable_code"
).to_dict("index")


variables = [
    "HR",
    "RR",
    "SpO2",
    "TEMP",
    "SBP",
    "DBP"
]


# ==================================================
# SOLO SIGNOS VITALES
# ==================================================

vitals = timeline[
    (timeline["source_type"] == "VITAL_SIGN") &
    (timeline["variable_code"].isin(variables)) &
    (timeline["quality_info"] == "OK") &
    (~timeline["is_plausibility_issue"])
].copy()

vitals["value_numeric"] = pd.to_numeric(
    vitals["value"],
    errors="coerce"
)


# ==================================================
# PERIODO DE ANALISIS
# ==================================================

inicio_timeline = vitals["event_datetime"].min()

inicio_analisis = (
    inicio_timeline +
    pd.Timedelta(hours=24)
)

fin_analisis = vitals["event_datetime"].max()

print("\nInicio análisis:", inicio_analisis)
print("Fin análisis:", fin_analisis)


# ==================================================
# CREAR VENTANAS
# ==================================================

filas_features = []

decision_time = inicio_analisis

while decision_time <= fin_analisis:

    window_start = (
        decision_time -
        pd.Timedelta(hours=WINDOW_HOURS)
    )

    # MUY IMPORTANTE:
    # solamente información disponible hasta T
    ventana = vitals[
        (vitals["event_datetime"] > window_start) &
        (vitals["event_datetime"] <= decision_time) &
        (vitals["available_datetime"] <= decision_time)
    ]

    fila = {
        "patient_id": PATIENT_ID,
        "decision_datetime": decision_time,
        "window_start": window_start,
        "window_end": decision_time
    }

    for variable in variables:

        datos = ventana[
            ventana["variable_code"] == variable
        ].sort_values("event_datetime")

        # Si no hay datos
        if datos.empty:

            fila[f"{variable}_count"] = 0
            fila[f"{variable}_mean"] = np.nan
            fila[f"{variable}_last"] = np.nan
            fila[f"{variable}_min"] = np.nan
            fila[f"{variable}_max"] = np.nan
            fila[f"{variable}_delta_baseline"] = np.nan
            fila[f"{variable}_zscore"] = np.nan

            continue

        valores = datos["value_numeric"]

        media = valores.mean()
        ultimo = valores.iloc[-1]

        baseline_median = baseline_dict[
            variable
        ]["median"]

        baseline_std = baseline_dict[
            variable
        ]["std"]

        delta = (
            media -
            baseline_median
        )

        if (
            pd.notna(baseline_std)
            and baseline_std > 0
        ):
            zscore = (
                delta /
                baseline_std
            )
        else:
            zscore = np.nan

        fila[f"{variable}_count"] = len(datos)
        fila[f"{variable}_mean"] = media
        fila[f"{variable}_last"] = ultimo
        fila[f"{variable}_min"] = valores.min()
        fila[f"{variable}_max"] = valores.max()

        fila[
            f"{variable}_delta_baseline"
        ] = delta

        fila[
            f"{variable}_zscore"
        ] = zscore

    filas_features.append(fila)

    decision_time += pd.Timedelta(
        hours=STEP_HOURS
    )


# ==================================================
# DATAFRAME FINAL
# ==================================================

features = pd.DataFrame(
    filas_features
)

print(
    "\nCantidad de ventanas:",
    len(features)
)

print(
    "\nColumnas generadas:",
    len(features.columns)
)


# ==================================================
# MOSTRAR EJEMPLO
# ==================================================

columnas_mostrar = [
    "decision_datetime",

    "HR_mean",
    "HR_delta_baseline",
    "HR_zscore",

    "RR_mean",
    "RR_delta_baseline",
    "RR_zscore",

    "SpO2_mean",
    "SpO2_delta_baseline",
    "SpO2_zscore"
]

print("\nPrimeras ventanas:")

print(
    features[
        columnas_mostrar
    ].head(15).to_string(index=False)
)


# ==================================================
# GUARDAR
# ==================================================

os.makedirs(
    "data/processed/features",
    exist_ok=True
)

ruta = (
    f"data/processed/features/"
    f"{PATIENT_ID}_features.parquet"
)

features.to_parquet(
    ruta,
    index=False
)

print("\nFeatures guardadas en:")
print(ruta)

print("\n=== FEATURES TERMINADAS ===")