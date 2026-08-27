import duckdb
import pandas as pd

PATIENT_ID = "PAT-0001"

print(f"\n=== AGREGANDO CONTEXTO A {PATIENT_ID} ===")

# Timeline ya creada
timeline = pd.read_parquet(
    f"data/processed/timelines/{PATIENT_ID}_timeline.parquet"
)

# Contextos
context = pd.read_csv(
    "data/raw/patient_context.csv"
)

context = context[
    context["patient_id"] == PATIENT_ID
].copy()

context["start_datetime"] = pd.to_datetime(
    context["start_datetime"],
    format="mixed"
)

context["end_datetime"] = pd.to_datetime(
    context["end_datetime"],
    format="mixed"
)

timeline["event_datetime"] = pd.to_datetime(
    timeline["event_datetime"]
)

# Nuevas columnas
timeline["sleep_state"] = None
timeline["activity_level"] = None
timeline["recovery_phase"] = None
timeline["context_confidence"] = None


# ==================================================
# ASOCIAR CONTEXTOS TEMPORALES
# ==================================================

for _, ctx in context.iterrows():

    mask = (
        (timeline["event_datetime"] >= ctx["start_datetime"]) &
        (timeline["event_datetime"] <= ctx["end_datetime"])
    )

    if ctx["context_type"] == "SLEEP_STATE":

        timeline.loc[
            mask,
            "sleep_state"
        ] = ctx["context_value"]

    elif ctx["context_type"] == "PHYSICAL_ACTIVITY":

        timeline.loc[
            mask,
            "activity_level"
        ] = ctx["context_value"]

    elif ctx["context_type"] == "RECOVERY_PHASE":

        timeline.loc[
            mask,
            "recovery_phase"
        ] = ctx["context_value"]

    timeline.loc[
        mask,
        "context_confidence"
    ] = ctx["confidence"]


# ==================================================
# RESUMEN
# ==================================================

print("\nEventos durante sueño:")
print(
    timeline["sleep_state"].value_counts(
        dropna=False
    )
)

print("\nEventos según actividad:")
print(
    timeline["activity_level"].value_counts(
        dropna=False
    )
)

print("\nEventos durante recuperación:")
print(
    timeline["recovery_phase"].value_counts(
        dropna=False
    )
)


# ==================================================
# EJEMPLOS CON CONTEXTO
# ==================================================

ejemplos = timeline[
    timeline["sleep_state"].notna()
    |
    timeline["activity_level"].notna()
    |
    timeline["recovery_phase"].notna()
]

print("\nPrimeros eventos con contexto:")

print(
    ejemplos[
        [
            "event_datetime",
            "source_type",
            "variable_code",
            "value",
            "sleep_state",
            "activity_level",
            "recovery_phase"
        ]
    ].head(30).to_string(index=False)
)


# ==================================================
# GUARDAR
# ==================================================

ruta = (
    f"data/processed/timelines/"
    f"{PATIENT_ID}_timeline_context.parquet"
)

timeline.to_parquet(
    ruta,
    index=False
)

print("\nTimeline contextualizada guardada:")
print(ruta)

print("\n=== CONTEXTO TERMINADO ===")