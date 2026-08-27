import pandas as pd

PATIENT_ID = "PAT-0001"

print(f"\n=== AGREGANDO CONECTIVIDAD A {PATIENT_ID} ===")

# ==================================================
# CARGAR TIMELINE CONTEXTUALIZADA
# ==================================================

timeline = pd.read_parquet(
    f"data/processed/timelines/"
    f"{PATIENT_ID}_timeline_context.parquet"
)

timeline["event_datetime"] = pd.to_datetime(
    timeline["event_datetime"]
)

# ==================================================
# CARGAR EVENTOS DE CONECTIVIDAD
# ==================================================

connectivity = pd.read_csv(
    "data/raw/connectivity_events.csv"
)

connectivity = connectivity[
    connectivity["patient_id"] == PATIENT_ID
].copy()

connectivity["start_datetime"] = pd.to_datetime(
    connectivity["start_datetime"],
    format="mixed"
)

connectivity["end_datetime"] = pd.to_datetime(
    connectivity["end_datetime"],
    format="mixed"
)

print(
    "\nEventos de conectividad del paciente:",
    len(connectivity)
)

# ==================================================
# COLUMNAS NUEVAS
# ==================================================

timeline["connectivity_status"] = None
timeline["delayed_records"] = 0
timeline["packet_loss_estimate"] = 0.0

# ==================================================
# ASOCIAR CONECTIVIDAD
# ==================================================

for _, conn in connectivity.iterrows():

    mask = (
        (timeline["event_datetime"] >= conn["start_datetime"]) &
        (timeline["event_datetime"] <= conn["end_datetime"]) &
        (timeline["device_id"] == conn["device_id"])
    )

    timeline.loc[
        mask,
        "connectivity_status"
    ] = conn["connectivity_status"]

    timeline.loc[
        mask,
        "delayed_records"
    ] = conn["delayed_records"]

    timeline.loc[
        mask,
        "packet_loss_estimate"
    ] = conn["packet_loss_estimate"]

# ==================================================
# RESUMEN
# ==================================================

print("\nEventos según conectividad:")

print(
    timeline["connectivity_status"].value_counts(
        dropna=False
    )
)

print("\nPacket loss máximo asociado:")

print(
    timeline["packet_loss_estimate"].max()
)

# ==================================================
# MOSTRAR EJEMPLOS
# ==================================================

afectados = timeline[
    timeline["connectivity_status"].notna()
]

print("\nPrimeros eventos afectados por conectividad:")

if len(afectados) > 0:

    print(
        afectados[
            [
                "event_datetime",
                "device_id",
                "source_type",
                "variable_code",
                "value",
                "connectivity_status",
                "delayed_records",
                "packet_loss_estimate"
            ]
        ].head(30).to_string(index=False)
    )

else:
    print("Este paciente no tiene eventos coincidentes.")

# ==================================================
# GUARDAR
# ==================================================

ruta = (
    f"data/processed/timelines/"
    f"{PATIENT_ID}_timeline_enriched.parquet"
)

timeline.to_parquet(
    ruta,
    index=False
)

print("\nTimeline enriquecida guardada en:")
print(ruta)

print("\n=== CONECTIVIDAD TERMINADA ===")