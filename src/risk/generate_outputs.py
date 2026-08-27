import pandas as pd
import os

PATIENT_ID = "PAT-0001"

print(f"\n=== GENERANDO OUTPUTS RISA PARA {PATIENT_ID} ===")


# ==================================================
# CARGAR DATOS
# ==================================================

signals = pd.read_parquet(
    f"data/processed/signals/"
    f"{PATIENT_ID}_scored_signals.parquet"
)

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

signals["decision_datetime"] = pd.to_datetime(
    signals["decision_datetime"]
)

signals["evidence_start"] = pd.to_datetime(
    signals["evidence_start"]
)

signals["evidence_end"] = pd.to_datetime(
    signals["evidence_end"]
)


# ==================================================
# CAMBIAR CAND-XXXXXX A SIGNAL-XXXXXX
# ==================================================

id_mapping = {}

for i, old_id in enumerate(
    signals["signal_id"],
    start=1
):
    id_mapping[old_id] = f"SIGNAL-{i:06d}"

signals["signal_id"] = (
    signals["signal_id"].map(id_mapping)
)


# ==================================================
# CONFIDENCE SCORE
#
# Para este MVP usamos quality_score como confianza
# cuando existe.
# ==================================================

signals["confidence_score"] = (
    signals["quality_score"]
    .fillna(0.5)
    .clip(0, 1)
)


# ==================================================
# SIGNALS.CSV
# ==================================================

signals_output = signals[
    [
        "signal_id",
        "patient_id",
        "decision_datetime",
        "risk_score",
        "priority_level",
        "confidence_score",
        "evidence_start",
        "evidence_end",
        "explanation",
        "model_version"
    ]
].copy()


# ==================================================
# EVIDENCE.CSV
# ==================================================

evidence_rows = []

for _, signal in signals.iterrows():

    signal_id = signal["signal_id"]

    decision_time = signal[
        "decision_datetime"
    ]

    evidence_start = signal[
        "evidence_start"
    ]

    evidence_end = signal[
        "evidence_end"
    ]

    trigger_variables = (
        signal["variables_triggering"]
        .split(",")
    )


    # ==============================================
    # SOLO EVIDENCIA DISPONIBLE HASTA LA DECISION
    # ==============================================

    periodo = timeline[
        (timeline["event_datetime"] >= evidence_start)
        &
        (timeline["event_datetime"] <= evidence_end)
        &
        (timeline["available_datetime"] <= decision_time)
    ].copy()


    # ==============================================
    # PRIMARY
    #
    # Signos vitales que activaron el episodio
    # ==============================================

    primary = periodo[
        (periodo["source_type"] == "VITAL_SIGN")
        &
        (periodo["variable_code"].isin(trigger_variables))
    ].copy()

    for _, row in primary.iterrows():

        evidence_rows.append(
            {
                "signal_id": signal_id,
                "source_file": row["source_file"],
                "record_id": row["record_id"],
                "variable_code": row["variable_code"],
                "event_datetime": row["event_datetime"],
                "available_datetime": row["available_datetime"],
                "evidence_role": "PRIMARY",
                "contribution": 1.0
            }
        )


    # ==============================================
    # CONTEXT
    #
    # Actividad del wearable
    # ==============================================

    context = periodo[
        (periodo["source_type"] == "WEARABLE")
        &
        (periodo["variable_code"] == "ACTIVITY_LEVEL")
    ].copy()

    for _, row in context.iterrows():

        evidence_rows.append(
            {
                "signal_id": signal_id,
                "source_file": row["source_file"],
                "record_id": row["record_id"],
                "variable_code": row["variable_code"],
                "event_datetime": row["event_datetime"],
                "available_datetime": row["available_datetime"],
                "evidence_role": "CONTEXT",
                "contribution": 0.0
            }
        )


    # ==============================================
    # QUALITY
    #
    # Observaciones de calidad del dispositivo
    # ==============================================

    quality = periodo[
        periodo["source_type"] == "DEVICE_QUALITY"
    ].copy()

    for _, row in quality.iterrows():

        evidence_rows.append(
            {
                "signal_id": signal_id,
                "source_file": row["source_file"],
                "record_id": row["record_id"],
                "variable_code": row["variable_code"],
                "event_datetime": row["event_datetime"],
                "available_datetime": row["available_datetime"],
                "evidence_role": "QUALITY",
                "contribution": 0.0
            }
        )


# ==================================================
# DATAFRAME FINAL DE EVIDENCIA
# ==================================================

evidence_output = pd.DataFrame(
    evidence_rows,
    columns=[
        "signal_id",
        "source_file",
        "record_id",
        "variable_code",
        "event_datetime",
        "available_datetime",
        "evidence_role",
        "contribution"
    ]
)


# ==================================================
# VALIDACIONES INTERNAS
# ==================================================

print("\n=== VALIDACIONES ===")

print(
    "Señales:",
    len(signals_output)
)

print(
    "Registros de evidencia:",
    len(evidence_output)
)


# --------------------------------------------------
# Evidencia disponible DESPUES de decision_datetime
# Debe ser 0
# --------------------------------------------------

future_evidence = evidence_output.merge(
    signals_output[
        [
            "signal_id",
            "decision_datetime"
        ]
    ],
    on="signal_id"
)

future_invalid = future_evidence[
    future_evidence["available_datetime"]
    >
    future_evidence["decision_datetime"]
]

print(
    "Evidencias disponibles después "
    "de la decisión:",
    len(future_invalid)
)


# --------------------------------------------------
# Señales sin evidencia
# Debe ser 0
# --------------------------------------------------

signals_without_evidence = (
    set(signals_output["signal_id"])
    -
    set(evidence_output["signal_id"])
)

print(
    "Señales sin evidencia:",
    len(signals_without_evidence)
)


# ==================================================
# GUARDAR RESULTADOS
# ==================================================

os.makedirs(
    "results",
    exist_ok=True
)

signals_output.to_csv(
    "results/signals.csv",
    index=False
)

evidence_output.to_csv(
    "results/evidence.csv",
    index=False
)


# ==================================================
# MOSTRAR RESULTADO
# ==================================================

print("\n=== SIGNALS.CSV ===")

print(
    signals_output.to_string(
        index=False
    )
)

print("\nRoles de evidencia:")

print(
    evidence_output[
        "evidence_role"
    ].value_counts()
)

print("\nArchivos generados:")

print("results/signals.csv")
print("results/evidence.csv")

print("\n=== OUTPUTS TERMINADOS ===")