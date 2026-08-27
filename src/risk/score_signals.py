import pandas as pd
import os

PATIENT_ID = "PAT-0001"

print(f"\n=== SCORING DE SEÑALES PARA {PATIENT_ID} ===")


# ==================================================
# CARGAR CANDIDATOS
# ==================================================

signals = pd.read_parquet(
    f"data/processed/signals/"
    f"{PATIENT_ID}_candidate_signals.parquet"
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


# ==================================================
# CALCULAR SCORE
#
# IMPORTANTE:
# Estos pesos son una decisión del MVP.
# NO son umbrales clínicos.
# ==================================================

resultados = []

for _, signal in signals.iterrows():

    evidence_start = pd.to_datetime(
        signal["evidence_start"]
    )

    decision_time = pd.to_datetime(
        signal["decision_datetime"]
    )

    # ----------------------------------------------
    # Evidencia disponible hasta la decisión
    # ----------------------------------------------

    evidence = timeline[
        (timeline["event_datetime"] >= evidence_start) &
        (timeline["event_datetime"] <= decision_time) &
        (timeline["available_datetime"] <= decision_time)
    ].copy()


    # ==============================================
    # 1. MAGNITUD
    # ==============================================

    magnitude_score = min(
        signal["max_abs_zscore"] / 8.0,
        1.0
    )


    # ==============================================
    # 2. MULTIVARIABLE
    # ==============================================

    breadth_score = min(
        signal["variables_over_threshold"] / 4.0,
        1.0
    )


    # ==============================================
    # 3. PERSISTENCIA
    # ==============================================

    persistence_score = min(
        signal["consecutive_windows"] / 4.0,
        1.0
    )


    # ==============================================
    # 4. CALIDAD DEL DISPOSITIVO
    # ==============================================

    device_quality = evidence[
        evidence["source_type"] == "DEVICE_QUALITY"
    ].copy()

    if len(device_quality) > 0:

        device_quality["quality_numeric"] = pd.to_numeric(
            device_quality["value"],
            errors="coerce"
        )

        quality_score = (
            device_quality[
                "quality_numeric"
            ].mean()
        )

    else:
        quality_score = None


    # ==============================================
    # 5. CONTEXTO DE ACTIVIDAD
    # ==============================================

    wearable_activity = evidence[
        (
            evidence["source_type"] == "WEARABLE"
        )
        &
        (
            evidence["variable_code"] ==
            "ACTIVITY_LEVEL"
        )
    ]

    high_activity_count = wearable_activity[
        wearable_activity["value"].isin(
            ["HIGH", "MODERATE"]
        )
    ].shape[0]

    total_activity_count = len(
        wearable_activity
    )

    if total_activity_count > 0:

        activity_fraction = (
            high_activity_count /
            total_activity_count
        )

    else:
        activity_fraction = 0


    # ==============================================
    # SCORE BASE
    # ==============================================

    risk_score = (
        magnitude_score * 0.50
        +
        breadth_score * 0.30
        +
        persistence_score * 0.20
    )


    # ==============================================
    # AJUSTE SUAVE POR CALIDAD
    # ==============================================

    if (
        quality_score is not None
        and pd.notna(quality_score)
    ):

        quality_factor = (
            0.8 +
            (0.2 * quality_score)
        )

        risk_score *= quality_factor


    # ==============================================
    # AJUSTE POR ACTIVIDAD
    #
    # Si gran parte de la ventana ocurrió con
    # actividad física, reducimos ligeramente
    # la prioridad.
    # ==============================================

    if activity_fraction >= 0.50:
        risk_score *= 0.85


    # Garantizar 0-1
    risk_score = max(
        0,
        min(risk_score, 1)
    )


    # ==============================================
    # PRIORIDAD
    #
    # Decisión interna del MVP.
    # ==============================================

    if risk_score < 0.30:
        priority = "LOW"

    elif risk_score < 0.50:
        priority = "MEDIUM"

    elif risk_score < 0.75:
        priority = "HIGH"

    else:
        priority = "CRITICAL"


    # ==============================================
    # EXPLICACION
    # ==============================================

    explanation = (
        signal["explanation"]
        +
        f". Persistencia observada: "
        f"{signal['consecutive_windows']} "
        f"ventanas consecutivas."
    )

    if (
        quality_score is not None
        and pd.notna(quality_score)
    ):

        explanation += (
            f" Calidad de dispositivo "
            f"promedio: {quality_score:.2f}."
        )

    if activity_fraction == 0:

        explanation += (
            " Sin actividad física moderada/alta "
            "registrada en la evidencia disponible."
        )


    resultados.append(
        {
            "signal_id":
                signal["signal_id"],

            "patient_id":
                signal["patient_id"],

            "decision_datetime":
                decision_time,

            "risk_score":
                round(risk_score, 4),

            "priority_level":
                priority,

            "evidence_start":
                evidence_start,

            "evidence_end":
                decision_time,

            "quality_score":
                quality_score,

            "activity_fraction":
                activity_fraction,

            "variables_triggering":
                signal["variables_triggering"],

            "explanation":
                explanation,

            "model_version":
                "risa_mvp_v0.1"
        }
    )


# ==================================================
# RESULTADO
# ==================================================

scored = pd.DataFrame(
    resultados
)

print("\n=== SEÑALES PRIORIZADAS ===")

print(
    scored.to_string(
        index=False
    )
)


# ==================================================
# GUARDAR
# ==================================================

os.makedirs(
    "data/processed/signals",
    exist_ok=True
)

ruta = (
    f"data/processed/signals/"
    f"{PATIENT_ID}_scored_signals.parquet"
)

scored.to_parquet(
    ruta,
    index=False
)

print("\nSeñales guardadas en:")
print(ruta)

print("\n=== SCORING TERMINADO ===")