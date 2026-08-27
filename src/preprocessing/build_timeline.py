import duckdb
import os

# ==================================================
# CONFIGURACION
# ==================================================

PATIENT_ID = "PAT-0001"

os.makedirs("data/processed/timelines", exist_ok=True)

con = duckdb.connect()

print(f"\n=== CONSTRUYENDO TIMELINE DE {PATIENT_ID} ===")


# ==================================================
# CREAR TIMELINE
# ==================================================

query = f"""

-- =================================================
-- SIGNOS VITALES
-- event_datetime = timestamp
-- available_datetime = timestamp
-- =================================================

SELECT
    observation_id AS record_id,
    patient_id,
    encounter_id,
    device_id,

    'VITAL_SIGN' AS source_type,
    'vital_signs.csv' AS source_file,

    variable_code,

    CAST(value_canonical AS VARCHAR) AS value,
    unit_canonical AS unit,

    timestamp AS event_datetime,
    timestamp AS available_datetime,

    source_system,

    quality_flag AS quality_info,
    is_plausibility_issue

FROM read_parquet(
    'data/processed/vital_signs_final.parquet'
)

WHERE patient_id = '{PATIENT_ID}'
  AND is_retransmission = FALSE


UNION ALL


-- =================================================
-- WEARABLE
-- event_datetime = timestamp
-- available_datetime = sync_datetime
-- =================================================

SELECT
    wearable_observation_id AS record_id,
    patient_id,

    NULL AS encounter_id,

    device_id,

    'WEARABLE' AS source_type,
    'wearable_observations.csv' AS source_file,

    variable_code,

    CAST(value AS VARCHAR) AS value,
    unit,

    timestamp AS event_datetime,
    sync_datetime AS available_datetime,

    'WEARABLE_GATEWAY' AS source_system,

    measurement_quality AS quality_info,
    FALSE AS is_plausibility_issue

FROM read_csv_auto(
    'data/raw/wearable_observations.csv'
)

WHERE patient_id = '{PATIENT_ID}'


UNION ALL


-- =================================================
-- CALIDAD DE DISPOSITIVO
-- event_datetime = timestamp
-- available_datetime = timestamp
-- =================================================

SELECT
    device_observation_id AS record_id,
    patient_id,
    encounter_id,
    device_id,

   'DEVICE_QUALITY' AS source_type,
    'device_observations.csv' AS source_file,

    variable_code,

    CAST(value AS VARCHAR) AS value,
    unit,

    timestamp AS event_datetime,
    timestamp AS available_datetime,

    source_system,

    CAST(signal_quality AS VARCHAR) AS quality_info,
    FALSE AS is_plausibility_issue

FROM read_csv_auto(
    'data/raw/device_observations.csv'
)

WHERE patient_id = '{PATIENT_ID}'


UNION ALL


-- =================================================
-- LABORATORIO
-- event_datetime = sample_datetime
-- available_datetime = result_datetime
-- =================================================

SELECT
    lab_result_id AS record_id,
    patient_id,
    encounter_id,

    NULL AS device_id,

    'LABORATORY' AS source_type,
    'laboratory_results.csv' AS source_file,

    test_code AS variable_code,

    CAST(result_value AS VARCHAR) AS value,
    unit,

    sample_datetime AS event_datetime,
    result_datetime AS available_datetime,

    source_system,

    quality_flag AS quality_info,
    FALSE AS is_plausibility_issue

FROM read_csv_auto(
    'data/raw/laboratory_results.csv'
)

WHERE patient_id = '{PATIENT_ID}'

"""

timeline = con.execute(query).df()


# ==================================================
# ORDENAR
# ==================================================

timeline = timeline.sort_values(
    by=["event_datetime", "available_datetime"]
)


# ==================================================
# MOSTRAR RESUMEN
# ==================================================

print("\nCantidad total de eventos:", len(timeline))

print("\nEventos por fuente:")
print(
    timeline["source_type"].value_counts()
)

print("\nPrimeros 30 eventos:")
print(
    timeline.head(30).to_string(index=False)
)


# ==================================================
# GUARDAR
# ==================================================

ruta_parquet = (
    f"data/processed/timelines/"
    f"{PATIENT_ID}_timeline.parquet"
)

ruta_csv = (
    f"data/processed/timelines/"
    f"{PATIENT_ID}_timeline.csv"
)

timeline.to_parquet(
    ruta_parquet,
    index=False
)

timeline.to_csv(
    ruta_csv,
    index=False
)

print("\nTimeline guardada en:")
print(ruta_parquet)
print(ruta_csv)

# ==================================================
# VALIDACIONES DE LA TIMELINE
# ==================================================

print("\n=== VALIDACION TIMELINE ===")

# 1. Evidencia disponible antes de ocurrir
temporal_invalidos = timeline[
    timeline["available_datetime"] <
    timeline["event_datetime"]
]

print(
    "available_datetime < event_datetime:",
    len(temporal_invalidos)
)


# 2. Record IDs duplicados
duplicados = timeline["record_id"].duplicated().sum()

print("Record_id duplicados:", duplicados)


# 3. Rango temporal
print(
    "Inicio timeline:",
    timeline["event_datetime"].min()
)

print(
    "Fin timeline:",
    timeline["event_datetime"].max()
)

print("\n=== FIN VALIDACION TIMELINE ===")





con.close()

print("\n=== TIMELINE TERMINADA ===")