import pandas as pd
import duckdb
# =========================
# CARGAR PATIENTS
# =========================

ruta = "data/raw/patients.csv"

patients = pd.read_csv(ruta)

print("\n=== VALIDACION PATIENTS ===")

# Cantidad de registros
print("\nCantidad de pacientes:", len(patients))

# Mostrar columnas
print("\nColumnas:")
print(patients.columns.tolist())

# =========================
# 1. PATIENT_ID UNICO
# =========================

duplicados_id = patients["patient_id"].duplicated().sum()

print("\nPatient_id duplicados:", duplicados_id)

# =========================
# 2. CAMPOS NULOS
# =========================

print("\nValores nulos por columna:")
print(patients.isnull().sum())

# =========================
# 3. VERIFICAR EDAD
# =========================

print("\nEdad minima:", patients["age_years"].min())
print("Edad maxima:", patients["age_years"].max())

# =========================
# 4. VALIDAR AGE_GROUP
# =========================

def edad_coincide_con_grupo(edad, grupo):

    grupo = str(grupo)

    # Ejemplo: 18-39
    if "-" in grupo:
        minimo, maximo = grupo.split("-")
        return int(minimo) <= edad <= int(maximo)

    # Ejemplo: 75+
    if grupo.endswith("+"):
        minimo = int(grupo.replace("+", ""))
        return edad >= minimo

    return False


patients["age_group_correcto"] = patients.apply(
    lambda fila: edad_coincide_con_grupo(
        fila["age_years"],
        fila["age_group"]
    ),
    axis=1
)

errores_edad = patients[
    patients["age_group_correcto"] == False
]

print("\nInconsistencias entre age_years y age_group:")
print(len(errores_edad))

if len(errores_edad) > 0:
    print(errores_edad[
        ["patient_id", "age_years", "age_group"]
    ])

# =========================
# 5. CATEGORIAS EXISTENTES
# =========================

columnas_categoricas = [
    "sex_at_birth",
    "age_group",
    "region_type",
    "care_program",
    "baseline_risk_profile",
    "active"
]

for columna in columnas_categoricas:

    print(f"\nValores de {columna}:")
    print(patients[columna].value_counts())


# =========================
# 6. VALIDAR ENROLLMENT_DATE
# =========================

patients["enrollment_date"] = pd.to_datetime(
    patients["enrollment_date"],
    errors="coerce"
)

fechas_invalidas = patients["enrollment_date"].isnull().sum()

print("\nEnrollment_date inválidas:", fechas_invalidas)

print("Fecha de enrollment mínima:",
      patients["enrollment_date"].min())

print("Fecha de enrollment máxima:",
      patients["enrollment_date"].max())

# ==================================================
# VALIDACION ENCOUNTERS
# ==================================================

print("\n\n=== VALIDACION ENCOUNTERS ===")

encounters = pd.read_csv("data/raw/encounters.csv")
facilities = pd.read_csv("data/raw/healthcare_facilities.csv")

print("\nCantidad de encounters:", len(encounters))

print("\nColumnas:")
print(encounters.columns.tolist())


# =========================
# 1. ENCOUNTER_ID UNICO
# =========================

duplicados_encounter = encounters["encounter_id"].duplicated().sum()

print("\nEncounter_id duplicados:", duplicados_encounter)


# =========================
# 2. VALORES NULOS
# =========================

print("\nValores nulos por columna:")
print(encounters.isnull().sum())


# =========================
# 3. VALIDAR PATIENT_ID
# =========================

pacientes_invalidos = encounters[
    ~encounters["patient_id"].isin(patients["patient_id"])
]

print("\nPatient_id inexistentes en patients:",
      len(pacientes_invalidos))


# =========================
# 4. VALIDAR FACILITY_ID
# =========================

facilities_invalidas = encounters[
    ~encounters["facility_id"].isin(facilities["facility_id"])
]

print("\nFacility_id inexistentes:",
      len(facilities_invalidas))


# =========================
# 5. CONVERTIR FECHAS
# =========================

encounters["start_datetime"] = pd.to_datetime(
    encounters["start_datetime"],
    errors="coerce"
)

encounters["end_datetime"] = pd.to_datetime(
    encounters["end_datetime"],
    errors="coerce"
)

print("\nStart_datetime inválidas:",
      encounters["start_datetime"].isnull().sum())

print("End_datetime inválidas:",
      encounters["end_datetime"].isnull().sum())


# =========================
# 6. VALIDAR ORDEN TEMPORAL
# =========================

fechas_incoherentes = encounters[
    encounters["start_datetime"] >= encounters["end_datetime"]
]

print("\nEncuentros con start >= end:",
      len(fechas_incoherentes))


# =========================
# 7. VER CATEGORIAS
# =========================

columnas_categoricas_encounter = [
    "encounter_type",
    "care_setting",
    "reason_category",
    "source_system",
    "status"
]

for columna in columnas_categoricas_encounter:

    print(f"\nValores de {columna}:")
    print(encounters[columna].value_counts())


print("\n=== FIN VALIDACION ENCOUNTERS ===")

# =========================
# 8. DURACION DE ENCOUNTERS
# =========================

encounters["duration_hours"] = (
    encounters["end_datetime"] -
    encounters["start_datetime"]
).dt.total_seconds() / 3600

print("\nDuración mínima (horas):",
      encounters["duration_hours"].min())

print("Duración máxima (horas):",
      encounters["duration_hours"].max())

print("Duración promedio (horas):",
      encounters["duration_hours"].mean())

print("\nDuración promedio por tipo de encounter:")
print(
    encounters.groupby("encounter_type")["duration_hours"].mean()
)

# ==================================================
# VALIDACION DEVICES
# ==================================================

print("\n\n=== VALIDACION DEVICES ===")

devices = pd.read_csv("data/raw/devices.csv")

print("\nCantidad de devices:", len(devices))

print("\nColumnas:")
print(devices.columns.tolist())


# 1. DEVICE_ID UNICO
duplicados_device = devices["device_id"].duplicated().sum()

print("\nDevice_id duplicados:", duplicados_device)


# 2. NULOS
print("\nValores nulos por columna:")
print(devices.isnull().sum())


# 3. VALIDAR PACIENTE ASIGNADO
pacientes_device_invalidos = devices[
    ~devices["assigned_patient_id"].isin(patients["patient_id"])
]

print("\nAssigned_patient_id inexistentes:",
      len(pacientes_device_invalidos))


# 4. VALIDAR FACILITY_ID
facilities_device_invalidas = devices[
    ~devices["facility_id"].isin(facilities["facility_id"])
]

print("\nFacility_id inexistentes:",
      len(facilities_device_invalidas))


# 5. VER CATEGORIAS
columnas_categoricas_device = [
    "device_type",
    "manufacturer_class",
    "model_family",
    "measurement_domain",
    "sampling_profile",
    "reliability_class",
    "patient_assignment_type",
    "active"
]

for columna in columnas_categoricas_device:

    print(f"\nValores de {columna}:")
    print(devices[columna].value_counts())


print("\n=== FIN VALIDACION DEVICES ===")

# ==================================================
# VALIDACION VITAL SIGNS
# ==================================================

print("\n\n=== VALIDACION VITAL SIGNS ===")

con = duckdb.connect()

# Crear vistas temporales
con.execute("""
CREATE OR REPLACE VIEW vital AS
SELECT *
FROM read_csv_auto('data/raw/vital_signs.csv');
""")

con.execute("""
CREATE OR REPLACE VIEW variable_catalog AS
SELECT *
FROM read_csv_auto('data/raw/variable_catalog.csv');
""")

con.execute("""
CREATE OR REPLACE VIEW units_catalog AS
SELECT *
FROM read_csv_auto('data/raw/units_catalog.csv');
""")

con.execute("""
CREATE OR REPLACE VIEW encounters_sql AS
SELECT *
FROM read_csv_auto('data/raw/encounters.csv');
""")

con.execute("""
CREATE OR REPLACE VIEW patients_sql AS
SELECT *
FROM read_csv_auto('data/raw/patients.csv');
""")

con.execute("""
CREATE OR REPLACE VIEW devices_sql AS
SELECT *
FROM read_csv_auto('data/raw/devices.csv');
""")


# =========================
# 1. CANTIDAD
# =========================

cantidad = con.execute("""
SELECT COUNT(*)
FROM vital
""").fetchone()[0]

print("\nCantidad de vital signs:", cantidad)


# =========================
# 2. OBSERVATION_ID UNICO
# =========================

duplicados_id = con.execute("""
SELECT COUNT(*) - COUNT(DISTINCT observation_id)
FROM vital
""").fetchone()[0]

print("\nObservation_id duplicados:", duplicados_id)


# =========================
# 3. VALIDAR PATIENT_ID
# =========================

pacientes_invalidos = con.execute("""
SELECT COUNT(*)
FROM vital v
LEFT JOIN patients_sql p
    ON v.patient_id = p.patient_id
WHERE p.patient_id IS NULL
""").fetchone()[0]

print("\nPatient_id inexistentes:", pacientes_invalidos)


# =========================
# 4. VALIDAR ENCOUNTER_ID
# =========================

encounters_invalidos = con.execute("""
SELECT COUNT(*)
FROM vital v
LEFT JOIN encounters_sql e
    ON v.encounter_id = e.encounter_id
WHERE e.encounter_id IS NULL
""").fetchone()[0]

print("Encounter_id inexistentes:", encounters_invalidos)


# =========================
# 5. VALIDAR DEVICE_ID
# =========================

devices_invalidos = con.execute("""
SELECT COUNT(*)
FROM vital v
LEFT JOIN devices_sql d
    ON v.device_id = d.device_id
WHERE d.device_id IS NULL
""").fetchone()[0]

print("Device_id inexistentes:", devices_invalidos)


# =========================
# 6. VALIDAR VARIABLE_CODE
# =========================

variables_invalidas = con.execute("""
SELECT COUNT(*)
FROM vital v
LEFT JOIN variable_catalog c
    ON v.variable_code = c.variable_code
WHERE c.variable_code IS NULL
""").fetchone()[0]

print("Variable_code inexistentes:", variables_invalidas)


# =========================
# 7. VARIABLES EXISTENTES
# =========================

print("\nCantidad por variable:")

print(
    con.execute("""
    SELECT variable_code, COUNT(*) AS cantidad
    FROM vital
    GROUP BY variable_code
    ORDER BY cantidad DESC
    """).df()
)


# =========================
# 8. QUALITY FLAG
# =========================

print("\nQuality flags:")

print(
    con.execute("""
    SELECT quality_flag, COUNT(*) AS cantidad
    FROM vital
    GROUP BY quality_flag
    ORDER BY cantidad DESC
    """).df()
)


# =========================
# 9. SOURCE SYSTEM
# =========================

print("\nSource systems:")

print(
    con.execute("""
    SELECT source_system, COUNT(*) AS cantidad
    FROM vital
    GROUP BY source_system
    ORDER BY cantidad DESC
    """).df()
)


# =========================
# 10. UNIDADES UTILIZADAS
# =========================

print("\nVariables y unidades:")

print(
    con.execute("""
    SELECT
        variable_code,
        unit,
        COUNT(*) AS cantidad
    FROM vital
    GROUP BY variable_code, unit
    ORDER BY variable_code, cantidad DESC
    """).df()
)


# =========================
# 11. UNIDADES NO CANONICAS
# =========================

unidades_no_canonicas = con.execute("""
SELECT COUNT(*)
FROM vital v
JOIN variable_catalog c
    ON v.variable_code = c.variable_code
WHERE v.unit <> c.canonical_unit
""").fetchone()[0]

print("\nRegistros con unidad diferente a la canónica:",
      unidades_no_canonicas)


# =========================
# 12. PLAUSIBILIDAD
# normalizando primero unidades
# =========================

print("\nValores fuera de plausibilidad por variable:")

print(
    con.execute("""
    SELECT
        variable_code,
        COUNT(*) AS fuera_plausibilidad
    FROM (
        SELECT
            v.variable_code,

            v.value * u.conversion_factor
                    + u.conversion_offset
                    AS valor_canonico,

            c.plausibility_min,
            c.plausibility_max

        FROM vital v

        JOIN units_catalog u
            ON v.unit = u.unit_code

        JOIN variable_catalog c
            ON v.variable_code = c.variable_code
    )
    WHERE
        valor_canonico < plausibility_min
        OR valor_canonico > plausibility_max

    GROUP BY variable_code
    ORDER BY fuera_plausibilidad DESC
    """).df()
)


# =========================
# 13. TIMESTAMP DENTRO DEL ENCOUNTER
# =========================

fuera_encounter = con.execute("""
SELECT COUNT(*)
FROM vital v
JOIN encounters_sql e
    ON v.encounter_id = e.encounter_id
WHERE
    v.timestamp < e.start_datetime
    OR v.timestamp > e.end_datetime
""").fetchone()[0]

print("\nMediciones fuera del periodo del encounter:",
      fuera_encounter)


# =========================
# 14. POSIBLES RETRANSMISIONES
# =========================

retransmitidos = con.execute("""
SELECT COUNT(*)
FROM vital
WHERE source_system = 'MONITOR_RETRANSMIT'
   OR quality_flag = 'RETRANSMITTED'
""").fetchone()[0]

print("\nRegistros marcados como retransmitidos:",
      retransmitidos)


# =========================
# 15. POSIBLES EVENTOS REPETIDOS
# =========================

repeticiones_semanticas = con.execute("""
SELECT COALESCE(SUM(cantidad - 1), 0)
FROM (
    SELECT
        patient_id,
        encounter_id,
        timestamp,
        variable_code,
        value,
        unit,
        device_id,
        COUNT(*) AS cantidad
    FROM vital

    GROUP BY
        patient_id,
        encounter_id,
        timestamp,
        variable_code,
        value,
        unit,
        device_id

    HAVING COUNT(*) > 1
)
""").fetchone()[0]

print("\nPosibles mediciones repetidas:",
      repeticiones_semanticas)


print("\n=== FIN VALIDACION VITAL SIGNS ===")

con.close()

# ==================================================
# PROCESAR / NORMALIZAR VITAL SIGNS
# ==================================================

print("\n=== NORMALIZANDO VITAL SIGNS ===")

con = duckdb.connect()

con.execute("""
COPY (
    SELECT
        v.*,

        -- conservar valor y unidad originales
        v.value AS value_original,
        v.unit AS unit_original,

        -- valor convertido a unidad canónica
        v.value * u.conversion_factor
                + u.conversion_offset
                AS value_canonical,

        -- unidad estándar
        u.canonical_unit AS unit_canonical,

        -- indica si hubo conversión
        CASE
            WHEN v.unit <> u.canonical_unit THEN TRUE
            ELSE FALSE
        END AS unit_was_converted

    FROM read_csv_auto('data/raw/vital_signs.csv') v

    LEFT JOIN read_csv_auto('data/raw/units_catalog.csv') u
        ON v.unit = u.unit_code
)
TO 'data/processed/vital_signs.parquet'
(FORMAT PARQUET);
""")

print("vital_signs.parquet creado correctamente.")

con.close()

# ==================================================
# VERIFICAR VITAL_SIGNS PROCESSED
# ==================================================

con = duckdb.connect()

cantidad_processed = con.execute("""
SELECT COUNT(*)
FROM read_parquet('data/processed/vital_signs.parquet')
""").fetchone()[0]

print("\nRegistros en vital_signs.parquet:", cantidad_processed)


print("\nConversiones realizadas:")

print(
    con.execute("""
    SELECT
        variable_code,
        unit_original,
        unit_canonical,
        COUNT(*) AS cantidad
    FROM read_parquet('data/processed/vital_signs.parquet')
    WHERE unit_was_converted = TRUE
    GROUP BY
        variable_code,
        unit_original,
        unit_canonical
    """).df()
)


print("\nEjemplos de temperaturas convertidas:")

print(
    con.execute("""
    SELECT
        observation_id,
        value_original,
        unit_original,
        value_canonical,
        unit_canonical
    FROM read_parquet('data/processed/vital_signs.parquet')
    WHERE unit_was_converted = TRUE
    LIMIT 10
    """).df()
)

con.close()

# ==================================================
# VITAL SIGNS FINAL PROCESSED
# ==================================================

print("\n=== CREANDO VITAL SIGNS FINAL ===")

con = duckdb.connect()

con.execute("""
COPY (
    SELECT
        v.*,

        -- Datos originales
        v.value AS value_original,
        v.unit AS unit_original,

        -- Datos normalizados
        v.value * u.conversion_factor
                + u.conversion_offset AS value_canonical,

        u.canonical_unit AS unit_canonical,

        -- Indica si se convirtió la unidad
        CASE
            WHEN v.unit <> u.canonical_unit
            THEN TRUE
            ELSE FALSE
        END AS unit_was_converted,

        -- Valor fuera de plausibilidad
        CASE
            WHEN c.plausibility_min IS NOT NULL
             AND c.plausibility_max IS NOT NULL
             AND (
                 (v.value * u.conversion_factor + u.conversion_offset)
                     < c.plausibility_min
                 OR
                 (v.value * u.conversion_factor + u.conversion_offset)
                     > c.plausibility_max
             )
            THEN TRUE
            ELSE FALSE
        END AS is_plausibility_issue,

        -- Registro retransmitido
        CASE
            WHEN v.source_system = 'MONITOR_RETRANSMIT'
              OR v.quality_flag = 'RETRANSMITTED'
            THEN TRUE
            ELSE FALSE
        END AS is_retransmission

    FROM read_csv_auto('data/raw/vital_signs.csv') v

    LEFT JOIN read_csv_auto('data/raw/units_catalog.csv') u
        ON v.unit = u.unit_code

    LEFT JOIN read_csv_auto('data/raw/variable_catalog.csv') c
        ON v.variable_code = c.variable_code
)
TO 'data/processed/vital_signs_final.parquet'
(FORMAT PARQUET);
""")

print("vital_signs_final.parquet creado.")

# ==================================================
# VERIFICACION
# ==================================================

print("\nResumen final:")

print(
    con.execute("""
    SELECT
        COUNT(*) AS registros,
        SUM(CASE WHEN unit_was_converted THEN 1 ELSE 0 END)
            AS unidades_convertidas,
        SUM(CASE WHEN is_plausibility_issue THEN 1 ELSE 0 END)
            AS problemas_plausibilidad,
        SUM(CASE WHEN is_retransmission THEN 1 ELSE 0 END)
            AS retransmisiones
    FROM read_parquet(
        'data/processed/vital_signs_final.parquet'
    )
    """).df()
)

con.close()

# ==================================================
# VALIDACION DEVICE OBSERVATIONS
# ==================================================

print("\n\n=== VALIDACION DEVICE OBSERVATIONS ===")

device_obs = pd.read_csv("data/raw/device_observations.csv")

print("\nCantidad de registros:", len(device_obs))

print("\nColumnas:")
print(device_obs.columns.tolist())


# ID unico
duplicados = device_obs["device_observation_id"].duplicated().sum()

print("\nDevice_observation_id duplicados:", duplicados)


# NULOS
print("\nValores nulos:")
print(device_obs.isnull().sum())


# PATIENT_ID
pacientes_invalidos = device_obs[
    ~device_obs["patient_id"].isin(patients["patient_id"])
]

print("\nPatient_id inexistentes:", len(pacientes_invalidos))


# ENCOUNTER_ID
encounters_invalidos = device_obs[
    ~device_obs["encounter_id"].isin(encounters["encounter_id"])
]

print("Encounter_id inexistentes:", len(encounters_invalidos))


# DEVICE_ID
devices_invalidos = device_obs[
    ~device_obs["device_id"].isin(devices["device_id"])
]

print("Device_id inexistentes:", len(devices_invalidos))


# TIMESTAMP
device_obs["timestamp"] = pd.to_datetime(
    device_obs["timestamp"],
    errors="coerce"
)

print("\nTimestamp inválidos:",
      device_obs["timestamp"].isnull().sum())


# VARIABLE CODE
print("\nVariable_code:")
print(device_obs["variable_code"].value_counts())


# UNIT
print("\nUnidades:")
print(device_obs["unit"].value_counts())


# SOURCE SYSTEM
print("\nSource_system:")
print(device_obs["source_system"].value_counts())


# SIGNAL QUALITY
print("\nEstadísticas signal_quality:")

print(
    device_obs["signal_quality"].describe()
)


# Valores de calidad fuera de 0-1
quality_invalidos = device_obs[
    (device_obs["signal_quality"] < 0) |
    (device_obs["signal_quality"] > 1)
]

print("\nSignal_quality fuera de 0-1:",
      len(quality_invalidos))


# VALUE fuera del rango oficial de SIGNAL_QUALITY_INDEX
value_invalidos = device_obs[
    (device_obs["value"] < 0) |
    (device_obs["value"] > 1)
]

print("Value fuera de 0-1:",
      len(value_invalidos))


print("\n=== FIN VALIDACION DEVICE OBSERVATIONS ===")

# ==================================================
# VALIDACION PATIENT CONTEXT
# ==================================================

print("\n\n=== VALIDACION PATIENT CONTEXT ===")

patient_context = pd.read_csv("data/raw/patient_context.csv")

print("\nCantidad de registros:", len(patient_context))

print("\nColumnas:")
print(patient_context.columns.tolist())


# 1. CONTEXT_ID UNICO
duplicados = patient_context["context_id"].duplicated().sum()

print("\nContext_id duplicados:", duplicados)


# 2. NULOS
print("\nValores nulos:")
print(patient_context.isnull().sum())


# 3. VALIDAR PATIENT_ID
pacientes_invalidos = patient_context[
    ~patient_context["patient_id"].isin(patients["patient_id"])
]

print("\nPatient_id inexistentes:", len(pacientes_invalidos))


# 4. CONVERTIR FECHAS
patient_context["start_datetime"] = pd.to_datetime(
    patient_context["start_datetime"],
    errors="coerce"
)

patient_context["end_datetime"] = pd.to_datetime(
    patient_context["end_datetime"],
    errors="coerce"
)

print("\nStart_datetime inválidas:",
      patient_context["start_datetime"].isnull().sum())

print("End_datetime inválidas:",
      patient_context["end_datetime"].isnull().sum())


# 5. VALIDAR ORDEN TEMPORAL
intervalos_invalidos = patient_context[
    patient_context["start_datetime"] >= patient_context["end_datetime"]
]

print("\nIntervalos con start >= end:",
      len(intervalos_invalidos))


# 6. CONTEXT_TYPE
print("\nValores de context_type:")
print(patient_context["context_type"].value_counts())


# 7. CONTEXT_VALUE
print("\nValores de context_value:")
print(patient_context["context_value"].value_counts())


# 8. RELACION CONTEXT_TYPE + CONTEXT_VALUE
print("\nCombinaciones context_type + context_value:")

print(
    patient_context.groupby(
        ["context_type", "context_value"]
    ).size().sort_values(ascending=False)
)


# 9. SOURCE
print("\nValores de source:")
print(patient_context["source"].value_counts())


# 10. CONFIDENCE
print("\nEstadísticas de confidence:")
print(patient_context["confidence"].describe())


confidence_invalidos = patient_context[
    (patient_context["confidence"] < 0) |
    (patient_context["confidence"] > 1)
]

print("\nConfidence fuera de 0-1:",
      len(confidence_invalidos))


# 11. DURACION DEL CONTEXTO
patient_context["duration_hours"] = (
    patient_context["end_datetime"] -
    patient_context["start_datetime"]
).dt.total_seconds() / 3600

print("\nDuración de contextos en horas:")
print(patient_context["duration_hours"].describe())


print("\nDuración promedio por contexto:")

print(
    patient_context.groupby(
        ["context_type", "context_value"]
    )["duration_hours"].mean()
)


print("\n=== FIN VALIDACION PATIENT CONTEXT ===")

# ==================================================
# VALIDACION WEARABLE OBSERVATIONS
# ==================================================

print("\n\n=== VALIDACION WEARABLE OBSERVATIONS ===")

con = duckdb.connect()

con.execute("""
CREATE OR REPLACE VIEW wearable AS
SELECT *
FROM read_csv_auto('data/raw/wearable_observations.csv');
""")

# 1. CANTIDAD
cantidad = con.execute("""
SELECT COUNT(*)
FROM wearable
""").fetchone()[0]

print("\nCantidad de registros:", cantidad)


# 2. ID UNICO
duplicados = con.execute("""
SELECT COUNT(*) - COUNT(DISTINCT wearable_observation_id)
FROM wearable
""").fetchone()[0]

print("\nWearable_observation_id duplicados:", duplicados)


# 3. PATIENT_ID EXISTENTE
pacientes_invalidos = con.execute("""
SELECT COUNT(*)
FROM wearable w
LEFT JOIN read_csv_auto('data/raw/patients.csv') p
    ON w.patient_id = p.patient_id
WHERE p.patient_id IS NULL
""").fetchone()[0]

print("\nPatient_id inexistentes:", pacientes_invalidos)


# 4. DEVICE_ID EXISTENTE
devices_invalidos = con.execute("""
SELECT COUNT(*)
FROM wearable w
LEFT JOIN read_csv_auto('data/raw/devices.csv') d
    ON w.device_id = d.device_id
WHERE d.device_id IS NULL
""").fetchone()[0]

print("Device_id inexistentes:", devices_invalidos)


# 5. DEVICE ASIGNADO AL MISMO PACIENTE
device_patient_inconsistente = con.execute("""
SELECT COUNT(*)
FROM wearable w
JOIN read_csv_auto('data/raw/devices.csv') d
    ON w.device_id = d.device_id
WHERE w.patient_id <> d.assigned_patient_id
""").fetchone()[0]

print("Device asignado a otro paciente:",
      device_patient_inconsistente)


# 6. VARIABLE_CODE EXISTENTE
variables_invalidas = con.execute("""
SELECT COUNT(*)
FROM wearable w
LEFT JOIN read_csv_auto('data/raw/variable_catalog.csv') v
    ON w.variable_code = v.variable_code
WHERE v.variable_code IS NULL
""").fetchone()[0]

print("Variable_code inexistentes:", variables_invalidas)


# 7. VARIABLES
print("\nCantidad por variable:")

print(
    con.execute("""
    SELECT variable_code, COUNT(*) AS cantidad
    FROM wearable
    GROUP BY variable_code
    ORDER BY cantidad DESC
    """).df()
)


# 8. UNIDADES
print("\nVariables y unidades:")

print(
    con.execute("""
    SELECT
        variable_code,
        unit,
        COUNT(*) AS cantidad
    FROM wearable
    GROUP BY variable_code, unit
    ORDER BY variable_code
    """).df()
)


# 9. MEASUREMENT QUALITY
print("\nMeasurement quality:")

print(
    con.execute("""
    SELECT
        measurement_quality,
        COUNT(*) AS cantidad
    FROM wearable
    GROUP BY measurement_quality
    ORDER BY cantidad DESC
    """).df()
)


# 10. VALIDAR TIMESTAMP VS SYNC_DATETIME
sync_antes_evento = con.execute("""
SELECT COUNT(*)
FROM wearable
WHERE sync_datetime < timestamp
""").fetchone()[0]

print("\nSync_datetime anterior al timestamp:",
      sync_antes_evento)


# 11. RETRASO DE SINCRONIZACION
print("\nRetraso de sincronización en minutos:")

print(
    con.execute("""
    SELECT
        MIN(date_diff('second', timestamp, sync_datetime)) / 60.0
            AS minimo_min,

        AVG(date_diff('second', timestamp, sync_datetime)) / 60.0
            AS promedio_min,

        MEDIAN(date_diff('second', timestamp, sync_datetime)) / 60.0
            AS mediana_min,

        MAX(date_diff('second', timestamp, sync_datetime)) / 60.0
            AS maximo_min

    FROM wearable
    """).df()
)


# 12. DELAY POR VARIABLE
print("\nRetraso promedio por variable:")

print(
    con.execute("""
    SELECT
        variable_code,

        AVG(
            date_diff('second', timestamp, sync_datetime)
        ) / 60.0 AS delay_promedio_min

    FROM wearable

    GROUP BY variable_code
    ORDER BY variable_code
    """).df()
)


print("\n=== FIN VALIDACION WEARABLE OBSERVATIONS ===")

con.close()

# ==================================================
# VALIDACION LABORATORY RESULTS
# ==================================================

print("\n\n=== VALIDACION LABORATORY RESULTS ===")

labs = pd.read_csv("data/raw/laboratory_results.csv")

print("\nCantidad de registros:", len(labs))

print("\nColumnas:")
print(labs.columns.tolist())


# 1. ID UNICO
duplicados = labs["lab_result_id"].duplicated().sum()

print("\nLab_result_id duplicados:", duplicados)


# 2. NULOS
print("\nValores nulos:")
print(labs.isnull().sum())


# 3. PATIENT_ID
pacientes_invalidos = labs[
    ~labs["patient_id"].isin(patients["patient_id"])
]

print("\nPatient_id inexistentes:", len(pacientes_invalidos))


# 4. ENCOUNTER_ID
encounters_invalidos = labs[
    ~labs["encounter_id"].isin(encounters["encounter_id"])
]

print("Encounter_id inexistentes:", len(encounters_invalidos))


# 5. TEST_CODE CONTRA VARIABLE_CATALOG
variable_catalog_df = pd.read_csv("data/raw/variable_catalog.csv")

tests_invalidos = labs[
    ~labs["test_code"].isin(variable_catalog_df["variable_code"])
]

print("Test_code inexistentes en variable_catalog:",
      len(tests_invalidos))


# 6. CONVERTIR FECHAS
labs["sample_datetime"] = pd.to_datetime(
    labs["sample_datetime"],
    format="mixed",
    errors="coerce"
)

labs["result_datetime"] = pd.to_datetime(
    labs["result_datetime"],
    format="mixed",
    errors="coerce"
)

print("\nSample_datetime inválidas:",
      labs["sample_datetime"].isnull().sum())

print("Result_datetime inválidas:",
      labs["result_datetime"].isnull().sum())


# 7. RESULTADO DISPONIBLE ANTES DE LA MUESTRA
tiempos_invalidos = labs[
    labs["result_datetime"] < labs["sample_datetime"]
]

print("\nResult_datetime anterior a sample_datetime:",
      len(tiempos_invalidos))


# 8. RETRASO ENTRE MUESTRA Y RESULTADO
labs["delay_hours"] = (
    labs["result_datetime"] -
    labs["sample_datetime"]
).dt.total_seconds() / 3600

print("\nRetraso muestra → resultado (horas):")
print(labs["delay_hours"].describe())


# 9. TEST CODES
print("\nCantidad por test_code:")
print(labs["test_code"].value_counts())


# 10. UNIDADES
print("\nTest_code + unit:")
print(
    labs.groupby(
        ["test_code", "unit"]
    ).size()
)


# 11. QUALITY FLAG
print("\nQuality_flag:")
print(labs["quality_flag"].value_counts())


# 12. SOURCE SYSTEM
print("\nSource_system:")
print(labs["source_system"].value_counts())


# 13. RESULTADOS FUERA DE REFERENCE RANGE
labs["outside_reference"] = (
    (labs["result_value"] < labs["reference_low"]) |
    (labs["result_value"] > labs["reference_high"])
)

print("\nResultados fuera de reference_low/high:",
      labs["outside_reference"].sum())


print("\nFuera de rango por test_code:")
print(
    labs.groupby("test_code")["outside_reference"].sum()
)


print("\n=== FIN VALIDACION LABORATORY RESULTS ===")

# VALIDAR FACILITY_ID

facilities_invalidas = labs[
    ~labs["facility_id"].isin(facilities["facility_id"])
]

print("\nFacility_id inexistentes:",
      len(facilities_invalidas))


# VALIDAR UNIDADES CONTRA UNITS_CATALOG

units_df = pd.read_csv("data/raw/units_catalog.csv")

unidades_invalidas = labs[
    ~labs["unit"].isin(units_df["unit_code"])
]

print("Unidades inexistentes en units_catalog:",
      len(unidades_invalidas))


# ==================================================
# VALIDACION CONNECTIVITY EVENTS
# ==================================================

print("\n\n=== VALIDACION CONNECTIVITY EVENTS ===")

connectivity = pd.read_csv("data/raw/connectivity_events.csv")

print("\nCantidad de registros:", len(connectivity))

print("\nColumnas:")
print(connectivity.columns.tolist())


# 1. EVENT_ID UNICO
duplicados = connectivity["event_id"].duplicated().sum()

print("\nEvent_id duplicados:", duplicados)


# 2. NULOS
print("\nValores nulos:")
print(connectivity.isnull().sum())


# 3. VALIDAR PATIENT_ID
pacientes_invalidos = connectivity[
    ~connectivity["patient_id"].isin(patients["patient_id"])
]

print("\nPatient_id inexistentes:",
      len(pacientes_invalidos))


# 4. VALIDAR DEVICE_ID
devices_invalidos = connectivity[
    ~connectivity["device_id"].isin(devices["device_id"])
]

print("Device_id inexistentes:",
      len(devices_invalidos))


# 5. VALIDAR QUE EL DEVICE PERTENEZCA AL PACIENTE
device_patient = connectivity.merge(
    devices[["device_id", "assigned_patient_id"]],
    on="device_id",
    how="left"
)

inconsistencias = device_patient[
    device_patient["patient_id"] !=
    device_patient["assigned_patient_id"]
]

print("Device asignado a otro paciente:",
      len(inconsistencias))


# 6. CONVERTIR FECHAS
connectivity["start_datetime"] = pd.to_datetime(
    connectivity["start_datetime"],
    format="mixed",
    errors="coerce"
)

connectivity["end_datetime"] = pd.to_datetime(
    connectivity["end_datetime"],
    format="mixed",
    errors="coerce"
)

print("\nStart_datetime inválidas:",
      connectivity["start_datetime"].isnull().sum())

print("End_datetime inválidas:",
      connectivity["end_datetime"].isnull().sum())


# 7. VALIDAR INTERVALOS
intervalos_invalidos = connectivity[
    connectivity["start_datetime"] >=
    connectivity["end_datetime"]
]

print("\nIntervalos con start >= end:",
      len(intervalos_invalidos))


# 8. TIPOS DE CONECTIVIDAD
print("\nConnectivity_status:")
print(
    connectivity["connectivity_status"].value_counts()
)


# 9. DELAYED RECORDS
print("\nEstadísticas delayed_records:")
print(
    connectivity["delayed_records"].describe()
)

delayed_invalidos = connectivity[
    connectivity["delayed_records"] < 0
]

print("\nDelayed_records negativos:",
      len(delayed_invalidos))


# 10. PACKET LOSS
print("\nEstadísticas packet_loss_estimate:")
print(
    connectivity["packet_loss_estimate"].describe()
)

packet_invalidos = connectivity[
    (connectivity["packet_loss_estimate"] < 0) |
    (connectivity["packet_loss_estimate"] > 1)
]

print("\nPacket_loss_estimate fuera de 0-1:",
      len(packet_invalidos))


# 11. DURACION
connectivity["duration_hours"] = (
    connectivity["end_datetime"] -
    connectivity["start_datetime"]
).dt.total_seconds() / 3600

print("\nDuración de eventos en horas:")
print(
    connectivity["duration_hours"].describe()
)


print("\nDuración promedio por connectivity_status:")

print(
    connectivity.groupby(
        "connectivity_status"
    )["duration_hours"].mean()
)


print("\n=== FIN VALIDACION CONNECTIVITY EVENTS ===")

# ==================================================
# VALIDACION CONDITIONS
# ==================================================

print("\n\n=== VALIDACION CONDITIONS ===")

conditions = pd.read_csv("data/raw/conditions.csv")

print("\nCantidad de registros:", len(conditions))

print("\nColumnas:")
print(conditions.columns.tolist())


# 1. CONDITION_ID UNICO
duplicados = conditions["condition_id"].duplicated().sum()

print("\nCondition_id duplicados:", duplicados)


# 2. NULOS
print("\nValores nulos:")
print(conditions.isnull().sum())


# 3. VALIDAR PATIENT_ID
pacientes_invalidos = conditions[
    ~conditions["patient_id"].isin(patients["patient_id"])
]

print("\nPatient_id inexistentes:",
      len(pacientes_invalidos))


# 4. CONVERTIR FECHAS
conditions["onset_date"] = pd.to_datetime(
    conditions["onset_date"],
    format="mixed",
    errors="coerce"
)

conditions["recorded_datetime"] = pd.to_datetime(
    conditions["recorded_datetime"],
    format="mixed",
    errors="coerce"
)

print("\nOnset_date inválidas:",
      conditions["onset_date"].isnull().sum())

print("Recorded_datetime inválidas:",
      conditions["recorded_datetime"].isnull().sum())


# 5. VALIDAR CAUSALIDAD TEMPORAL
recorded_antes_onset = conditions[
    conditions["recorded_datetime"] <
    conditions["onset_date"]
]

print("\nRecorded_datetime anterior a onset_date:",
      len(recorded_antes_onset))


# 6. CONDITION CATEGORY
print("\nCondition_category:")
print(
    conditions["condition_category"].value_counts()
)


# 7. STATUS
print("\nStatus:")
print(
    conditions["status"].value_counts()
)


# 8. SEVERITY CONTEXT
print("\nSeverity_context:")
print(
    conditions["severity_context"].value_counts()
)


# 9. SOURCE SYSTEM
print("\nSource_system:")
print(
    conditions["source_system"].value_counts()
)


# 10. TIEMPO ENTRE INICIO Y REGISTRO
conditions["delay_days"] = (
    conditions["recorded_datetime"] -
    conditions["onset_date"]
).dt.total_seconds() / 86400

print("\nDías entre onset_date y recorded_datetime:")
print(
    conditions["delay_days"].describe()
)


print("\n=== FIN VALIDACION CONDITIONS ===")

# =========================
# REVISAR INCONSISTENCIAS TEMPORALES
# =========================

print("\nCondiciones con recorded_datetime < onset_date:")

print(
    recorded_antes_onset[
        [
            "condition_id",
            "patient_id",
            "condition_category",
            "onset_date",
            "recorded_datetime",
            "status"
        ]
    ]
)

# ==================================================
# PROCESAR CONDITIONS
# ==================================================

conditions["temporal_issue"] = (
    conditions["recorded_datetime"] <
    conditions["onset_date"]
)

print("\nRegistros marcados con temporal_issue:",
      conditions["temporal_issue"].sum())

conditions.to_parquet(
    "data/processed/conditions.parquet",
    index=False
)

print("conditions.parquet creado correctamente.")
# ==================================================
# VALIDACION MEDICATION ADMINISTRATIONS
# ==================================================

print("\n\n=== VALIDACION MEDICATION ADMINISTRATIONS ===")

med_admin = pd.read_csv(
    "data/raw/medication_administrations.csv"
)

medications = pd.read_csv(
    "data/raw/medications.csv"
)

print("\nCantidad de registros:", len(med_admin))

print("\nColumnas:")
print(med_admin.columns.tolist())


# 1. ID UNICO
duplicados = med_admin["administration_id"].duplicated().sum()

print("\nAdministration_id duplicados:", duplicados)


# 2. NULOS
print("\nValores nulos:")
print(med_admin.isnull().sum())


# 3. VALIDAR PATIENT_ID
pacientes_invalidos = med_admin[
    ~med_admin["patient_id"].isin(patients["patient_id"])
]

print("\nPatient_id inexistentes:",
      len(pacientes_invalidos))


# 4. VALIDAR ENCOUNTER_ID
encounters_invalidos = med_admin[
    ~med_admin["encounter_id"].isin(encounters["encounter_id"])
]

print("Encounter_id inexistentes:",
      len(encounters_invalidos))


# 5. VALIDAR MEDICATION_ID
medicamentos_invalidos = med_admin[
    ~med_admin["medication_id"].isin(
        medications["medication_id"]
    )
]

print("Medication_id inexistentes:",
      len(medicamentos_invalidos))


# 6. CONVERTIR FECHAS
med_admin["start_datetime"] = pd.to_datetime(
    med_admin["start_datetime"],
    format="mixed",
    errors="coerce"
)

med_admin["end_datetime"] = pd.to_datetime(
    med_admin["end_datetime"],
    format="mixed",
    errors="coerce"
)

print("\nStart_datetime inválidas:",
      med_admin["start_datetime"].isnull().sum())

print("End_datetime inválidas:",
      med_admin["end_datetime"].isnull().sum())


# 7. VALIDAR ORDEN TEMPORAL
intervalos_invalidos = med_admin[
    med_admin["start_datetime"] >=
    med_admin["end_datetime"]
]

print("\nAdministraciones con start >= end:",
      len(intervalos_invalidos))


# 8. VALIDAR DENTRO DEL ENCOUNTER
med_enc = med_admin.merge(
    encounters[
        [
            "encounter_id",
            "start_datetime",
            "end_datetime"
        ]
    ],
    on="encounter_id",
    suffixes=("_med", "_enc")
)

fuera_encounter = med_enc[
    (med_enc["start_datetime_med"] <
     med_enc["start_datetime_enc"])
    |
    (med_enc["end_datetime_med"] >
     med_enc["end_datetime_enc"])
]

print("\nAdministraciones fuera del encounter:",
      len(fuera_encounter))


# 9. MEDICATION_ID
print("\nCantidad por medication_id:")
print(
    med_admin["medication_id"].value_counts()
)


# 10. DOSE VALUE
print("\nEstadísticas dose_value:")
print(
    med_admin["dose_value"].describe()
)


# 11. DOSE UNIT
print("\nDose_unit:")
print(
    med_admin["dose_unit"].value_counts()
)


# 12. STATUS
print("\nAdministration_status:")
print(
    med_admin["administration_status"].value_counts()
)


# 13. SOURCE SYSTEM
print("\nSource_system:")
print(
    med_admin["source_system"].value_counts()
)


# 14. DURACION
med_admin["duration_hours"] = (
    med_admin["end_datetime"] -
    med_admin["start_datetime"]
).dt.total_seconds() / 3600

print("\nDuración de administraciones:")
print(
    med_admin["duration_hours"].describe()
)


print("\n=== FIN VALIDACION MEDICATION ADMINISTRATIONS ===")

# =========================
# REVISAR MEDICACIONES FUERA DEL ENCOUNTER
# =========================

print("\nAdministraciones fuera del encounter:")

print(
    fuera_encounter[
        [
            "administration_id",
            "patient_id",
            "encounter_id",
            "medication_id",
            "start_datetime_med",
            "end_datetime_med",
            "start_datetime_enc",
            "end_datetime_enc"
        ]
    ].to_string(index=False)
)

fuera_encounter["hours_before_encounter"] = (
    fuera_encounter["start_datetime_enc"] -
    fuera_encounter["start_datetime_med"]
).dt.total_seconds() / 3600

fuera_encounter["hours_after_encounter"] = (
    fuera_encounter["end_datetime_med"] -
    fuera_encounter["end_datetime_enc"]
).dt.total_seconds() / 3600

print("\nDesfase respecto al encounter:")

print(
    fuera_encounter[
        [
            "administration_id",
            "hours_before_encounter",
            "hours_after_encounter"
        ]
    ].to_string(index=False)
)

# ==================================================
# MARCAR PROBLEMAS TEMPORALES DE MEDICACION
# ==================================================

med_check = med_admin.merge(
    encounters[
        ["encounter_id", "start_datetime", "end_datetime"]
    ],
    on="encounter_id",
    suffixes=("_med", "_enc")
)

med_check["encounter_boundary_issue"] = (
    (med_check["start_datetime_med"] < med_check["start_datetime_enc"]) |
    (med_check["end_datetime_med"] > med_check["end_datetime_enc"])
)

med_check["hours_after_encounter"] = (
    med_check["end_datetime_med"] -
    med_check["end_datetime_enc"]
).dt.total_seconds() / 3600

print(
    "\nAdministraciones marcadas con encounter_boundary_issue:",
    med_check["encounter_boundary_issue"].sum()
)

med_check.to_parquet(
    "data/processed/medication_administrations.parquet",
    index=False
)

print("medication_administrations.parquet creado correctamente.")

# ==================================================
# VALIDACION MEDICATIONS
# ==================================================

print("\n\n=== VALIDACION MEDICATIONS ===")

medications = pd.read_csv("data/raw/medications.csv")

print("\nCantidad de registros:", len(medications))

print("\nColumnas:")
print(medications.columns.tolist())

# ID unico
duplicados = medications["medication_id"].duplicated().sum()
print("\nMedication_id duplicados:", duplicados)

# Nulos
print("\nValores nulos:")
print(medications.isnull().sum())

# Mostrar catálogo completo
print("\nCatálogo de medicamentos:")
print(medications.to_string(index=False))

print("\n=== FIN VALIDACION MEDICATIONS ===")

# ==================================================
# VALIDACION HEALTHCARE FACILITIES
# ==================================================

print("\n\n=== VALIDACION HEALTHCARE FACILITIES ===")

facilities = pd.read_csv(
    "data/raw/healthcare_facilities.csv"
)

print("\nCantidad de registros:", len(facilities))

print("\nColumnas:")
print(facilities.columns.tolist())


# ID UNICO
duplicados = facilities["facility_id"].duplicated().sum()

print("\nFacility_id duplicados:", duplicados)


# NULOS
print("\nValores nulos:")
print(facilities.isnull().sum())


# CATEGORIAS
columnas_facility = [
    "facility_type",
    "region_type",
    "digital_maturity",
    "connectivity_profile",
    "monitoring_capability",
    "laboratory_capability"
]

for columna in columnas_facility:

    print(f"\nValores de {columna}:")
    print(facilities[columna].value_counts())


# MOSTRAR TABLA
print("\nInstituciones:")

print(
    facilities.to_string(index=False)
)

print("\n=== FIN VALIDACION HEALTHCARE FACILITIES ===")

# ==================================================
# VALIDACION METADATA
# ==================================================

print("\n\n=== VALIDACION METADATA ===")


# ==================================================
# SOURCE CATALOG
# ==================================================

source_catalog = pd.read_csv(
    "data/raw/source_catalog.csv"
)

print("\n--- SOURCE CATALOG ---")

print("Cantidad:", len(source_catalog))
print("Duplicados source_system:",
      source_catalog["source_system"].duplicated().sum())

print("\nNulos:")
print(source_catalog.isnull().sum())

print("\nCatálogo:")
print(source_catalog.to_string(index=False))


# ==================================================
# UNITS CATALOG
# ==================================================

units_catalog = pd.read_csv(
    "data/raw/units_catalog.csv"
)

print("\n\n--- UNITS CATALOG ---")

print("Cantidad:", len(units_catalog))

print("Duplicados unit_code:",
      units_catalog["unit_code"].duplicated().sum())

print("\nNulos:")
print(units_catalog.isnull().sum())

print("\nCatálogo:")
print(units_catalog.to_string(index=False))


# ==================================================
# VARIABLE CATALOG
# ==================================================

variable_catalog = pd.read_csv(
    "data/raw/variable_catalog.csv"
)

print("\n\n--- VARIABLE CATALOG ---")

print("Cantidad:", len(variable_catalog))

print("Duplicados variable_code:",
      variable_catalog["variable_code"].duplicated().sum())

print("\nNulos:")
print(variable_catalog.isnull().sum())

print("\nRoles analíticos:")
print(
    variable_catalog["analysis_role"].value_counts()
)

print("\nCatálogo:")
print(variable_catalog.to_string(index=False))


# ==================================================
# DATA DICTIONARY
# ==================================================

data_dictionary = pd.read_csv(
    "data/raw/data_dictionary.csv"
)

print("\n\n--- DATA DICTIONARY ---")

print("Cantidad:", len(data_dictionary))

print("\nColumnas:")
print(data_dictionary.columns.tolist())

print("\nNulos:")
print(data_dictionary.isnull().sum())


print("\n=== FIN VALIDACION METADATA ===")