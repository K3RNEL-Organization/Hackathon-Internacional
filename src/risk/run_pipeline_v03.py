from pathlib import Path
import time

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURACION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"

VITALS_PATH = PROCESSED_DIR / "vital_signs_final.parquet"

PATIENTS_PATH = RAW_DIR / "patients.csv"
WEARABLE_PATH = RAW_DIR / "wearable_observations.csv"
DEVICE_QUALITY_PATH = RAW_DIR / "device_observations.csv"
PATIENT_CONTEXT_PATH = RAW_DIR / "patient_context.csv"
CONNECTIVITY_PATH = RAW_DIR / "connectivity_events.csv"
LABORATORY_PATH = RAW_DIR / "laboratory_results.csv"

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# PARAMETROS DEL MVP
#
# Son decisiones del equipo.
# NO son thresholds clinicos oficiales.
# ============================================================

BASELINE_HOURS = 24
WINDOW_HOURS = 4
STEP_HOURS = 1

Z_THRESHOLD = 2.0
MIN_VARIABLES = 2
MIN_CONSECUTIVE_WINDOWS = 2
MIN_BASELINE_COUNT = 3

# Superposicion minima real para contexto/conectividad.
MIN_CONTEXT_OVERLAP_MINUTES = 15

MODEL_VERSION = "risa_mvp_v0.3"

VARIABLES = [
    "HR",
    "RR",
    "SpO2",
    "TEMP",
    "SBP",
    "DBP"
]


# ============================================================
# COLUMNAS DE SALIDA
# ============================================================

SIGNALS_COLUMNS = [
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

EVIDENCE_COLUMNS = [
    "signal_id",
    "source_file",
    "record_id",
    "variable_code",
    "event_datetime",
    "available_datetime",
    "evidence_role",
    "contribution"
]


# ============================================================
# PRIORIDAD
# ============================================================

def get_priority(risk_score):

    if risk_score < 0.30:
        return "LOW"

    elif risk_score < 0.50:
        return "MEDIUM"

    elif risk_score < 0.75:
        return "HIGH"

    return "CRITICAL"


# ============================================================
# OBTENER DATOS DE UN PACIENTE
# ============================================================

def get_group_or_empty(
    grouped,
    patient_id,
    template
):

    try:
        return grouped.get_group(
            patient_id
        ).copy()

    except KeyError:
        return template.iloc[
            0:0
        ].copy()


# ============================================================
# BASELINE PERSONAL
# ============================================================

def calculate_baseline(
    patient_vitals,
    patient_start
):

    baseline_end = (
        patient_start
        +
        pd.Timedelta(
            hours=BASELINE_HOURS
        )
    )

    baseline_data = patient_vitals[
        (patient_vitals["timestamp"] >= patient_start)
        &
        (patient_vitals["timestamp"] < baseline_end)
        &
        (patient_vitals["quality_flag"] == "OK")
        &
        (~patient_vitals["is_plausibility_issue"])
    ].copy()

    baseline = {}

    for variable in VARIABLES:

        values = baseline_data[
            baseline_data["variable_code"]
            == variable
        ]["value_numeric"].dropna()

        if len(values) < MIN_BASELINE_COUNT:
            continue

        std = values.std()

        if pd.isna(std) or std <= 0:
            continue

        baseline[variable] = {
            "count": len(values),
            "mean": values.mean(),
            "median": values.median(),
            "std": std
        }

    return (
        baseline,
        baseline_end
    )


# ============================================================
# PREPARAR SERIES TEMPORALES
# ============================================================

def prepare_variable_arrays(
    patient_vitals
):

    arrays = {}

    valid = patient_vitals[
        (patient_vitals["quality_flag"] == "OK")
        &
        (~patient_vitals["is_plausibility_issue"])
    ].copy()

    for variable in VARIABLES:

        subset = valid[
            valid["variable_code"] == variable
        ].sort_values(
            "timestamp"
        )

        subset = subset.dropna(
            subset=["value_numeric"]
        )

        if subset.empty:
            continue

        times = subset[
            "timestamp"
        ].to_numpy(
            dtype="datetime64[ns]"
        )

        values = subset[
            "value_numeric"
        ].astype(
            float
        ).to_numpy()

        arrays[variable] = (
            times,
            values
        )

    return arrays


# ============================================================
# Z-SCORE POR VENTANA
# ============================================================

def calculate_window_zscores(
    decision_time,
    baseline,
    variable_arrays
):

    window_start = (
        decision_time
        -
        pd.Timedelta(
            hours=WINDOW_HOURS
        )
    )

    decision_np = np.datetime64(
        decision_time.to_datetime64(),
        "ns"
    )

    start_np = np.datetime64(
        window_start.to_datetime64(),
        "ns"
    )

    zscores = {}

    for variable in VARIABLES:

        if variable not in baseline:
            zscores[variable] = np.nan
            continue

        if variable not in variable_arrays:
            zscores[variable] = np.nan
            continue

        times, values = (
            variable_arrays[
                variable
            ]
        )

        left = np.searchsorted(
            times,
            start_np,
            side="right"
        )

        right = np.searchsorted(
            times,
            decision_np,
            side="right"
        )

        if right <= left:
            zscores[variable] = np.nan
            continue

        window_values = values[
            left:right
        ]

        if len(window_values) == 0:
            zscores[variable] = np.nan
            continue

        window_mean = np.nanmean(
            window_values
        )

        baseline_median = (
            baseline[
                variable
            ]["median"]
        )

        baseline_std = (
            baseline[
                variable
            ]["std"]
        )

        zscore = (
            window_mean
            -
            baseline_median
        ) / baseline_std

        zscores[variable] = zscore

    return (
        zscores,
        window_start
    )


# ============================================================
# ACTIVIDAD + CALIDAD
# ============================================================

def calculate_context_scores(
    patient_activity,
    patient_quality,
    evidence_start,
    decision_time
):

    # --------------------------------------------------------
    # ACTIVIDAD
    #
    # Wearable solo puede usarse si ya sincronizo.
    # --------------------------------------------------------

    activity_period = patient_activity[
        (
            patient_activity["timestamp"]
            >= evidence_start
        )
        &
        (
            patient_activity["timestamp"]
            <= decision_time
        )
        &
        (
            patient_activity["sync_datetime"]
            <= decision_time
        )
    ].copy()

    if len(activity_period) > 0:

        high_activity = activity_period[
            activity_period[
                "value"
            ].isin(
                [
                    "HIGH",
                    "MODERATE"
                ]
            )
        ]

        activity_fraction = (
            len(high_activity)
            /
            len(activity_period)
        )

    else:
        activity_fraction = 0.0


    # --------------------------------------------------------
    # CALIDAD DEL DISPOSITIVO
    # --------------------------------------------------------

    quality_period = patient_quality[
        (
            patient_quality["timestamp"]
            >= evidence_start
        )
        &
        (
            patient_quality["timestamp"]
            <= decision_time
        )
    ].copy()

    if len(quality_period) > 0:

        quality_values = pd.to_numeric(
            quality_period[
                "signal_quality"
            ],
            errors="coerce"
        ).dropna()

        if len(quality_values) > 0:
            quality_score = (
                quality_values.mean()
            )

        else:
            quality_score = None

    else:
        quality_score = None


    return (
        activity_fraction,
        quality_score,
        activity_period,
        quality_period
    )


# ============================================================
# SUPERPOSICION TEMPORAL REAL
# ============================================================

def filter_by_real_overlap(
    dataframe,
    evidence_start,
    decision_time
):

    if dataframe.empty:
        return dataframe.copy()

    period = dataframe[
        (
            dataframe["start_datetime"]
            < decision_time
        )
        &
        (
            dataframe["end_datetime"]
            > evidence_start
        )
    ].copy()

    if period.empty:
        return period

    # Inicio real de la interseccion
    period["overlap_start"] = period[
        "start_datetime"
    ].apply(
        lambda x: max(
            x,
            evidence_start
        )
    )

    # Fin real de la interseccion
    period["overlap_end"] = period[
        "end_datetime"
    ].apply(
        lambda x: min(
            x,
            decision_time
        )
    )

    period[
        "overlap_minutes"
    ] = (
        period["overlap_end"]
        -
        period["overlap_start"]
    ).dt.total_seconds() / 60.0

    period = period[
        period[
            "overlap_minutes"
        ]
        >= MIN_CONTEXT_OVERLAP_MINUTES
    ].copy()

    return period


# ============================================================
# CONTEXTO TEMPORAL ADICIONAL
# ============================================================

def get_additional_context(
    patient_context_data,
    patient_connectivity,
    evidence_start,
    decision_time
):

    # --------------------------------------------------------
    # SUEÑO / RECUPERACION
    # --------------------------------------------------------

    context_period = filter_by_real_overlap(
        patient_context_data,
        evidence_start,
        decision_time
    )

    if not context_period.empty:

        normalized_type = (
            context_period[
                "context_type"
            ]
            .astype(str)
            .str.upper()
        )

        context_period = context_period[
            normalized_type.str.contains(
                "SLEEP|RECOV",
                regex=True,
                na=False
            )
        ].copy()


    # --------------------------------------------------------
    # CONECTIVIDAD
    # --------------------------------------------------------

    connectivity_period = (
        filter_by_real_overlap(
            patient_connectivity,
            evidence_start,
            decision_time
        )
    )


    return (
        context_period,
        connectivity_period
    )


# ============================================================
# LABORATORIO DISPONIBLE
#
# sample_datetime = event time
# result_datetime = availability time
#
# NO modifica risk_score en v0.3.
# ============================================================

def get_laboratory_support(
    patient_labs,
    evidence_start,
    decision_time
):

    if patient_labs.empty:
        return patient_labs.copy()

    laboratory_period = patient_labs[
        # La muestra corresponde a la
        # ventana de evidencia.
        (
            patient_labs[
                "sample_datetime"
            ]
            >= evidence_start
        )
        &
        (
            patient_labs[
                "sample_datetime"
            ]
            <= decision_time
        )

        # El resultado ya estaba disponible
        # en el momento de decision.
        &
        (
            patient_labs[
                "result_datetime"
            ]
            <= decision_time
        )

        # En este dataset la calidad es OK,
        # pero lo dejamos explicitamente.
        &
        (
            patient_labs[
                "quality_flag"
            ]
            == "OK"
        )
    ].copy()

    return laboratory_period


# ============================================================
# RISK SCORE
# ============================================================

def calculate_risk_score(
    max_abs_zscore,
    variables_over_threshold,
    consecutive_windows,
    quality_score,
    activity_fraction
):

    magnitude_score = min(
        max_abs_zscore / 8.0,
        1.0
    )

    breadth_score = min(
        variables_over_threshold / 4.0,
        1.0
    )

    persistence_score = min(
        consecutive_windows / 4.0,
        1.0
    )

    risk_score = (
        magnitude_score * 0.50
        +
        breadth_score * 0.30
        +
        persistence_score * 0.20
    )


    # --------------------------------------------------------
    # CALIDAD
    # --------------------------------------------------------

    if (
        quality_score is not None
        and
        pd.notna(quality_score)
    ):

        quality_score = max(
            0.0,
            min(
                float(
                    quality_score
                ),
                1.0
            )
        )

        quality_factor = (
            0.8
            +
            0.2 * quality_score
        )

    else:

        # Calidad desconocida.
        quality_factor = 0.90


    risk_score *= quality_factor


    # --------------------------------------------------------
    # ACTIVIDAD
    # --------------------------------------------------------

    if activity_fraction >= 0.50:
        risk_score *= 0.85


    return max(
        0.0,
        min(
            float(
                risk_score
            ),
            1.0
        )
    )


# ============================================================
# INICIO DEL PIPELINE
# ============================================================

start_time = time.time()

print()
print("==========================================")
print(" HEALTHSIGNAL LATAM - PIPELINE RISA V0.3")
print("==========================================")

print(
    "\nCargando datos..."
)


# ============================================================
# PACIENTES
# ============================================================

patients = pd.read_csv(
    PATIENTS_PATH,
    usecols=[
        "patient_id"
    ]
)

patient_ids = (
    patients[
        "patient_id"
    ]
    .dropna()
    .drop_duplicates()
    .tolist()
)

print(
    "Pacientes:",
    len(patient_ids)
)


# ============================================================
# VITALES
# ============================================================

print(
    "\nCargando vital_signs_final.parquet..."
)

vitals = pd.read_parquet(
    VITALS_PATH,
    columns=[
        "observation_id",
        "patient_id",
        "encounter_id",
        "device_id",
        "timestamp",
        "variable_code",
        "value_canonical",
        "unit_canonical",
        "quality_flag",
        "is_plausibility_issue",
        "is_retransmission"
    ]
)

vitals["timestamp"] = pd.to_datetime(
    vitals["timestamp"]
)

vitals[
    "value_numeric"
] = pd.to_numeric(
    vitals[
        "value_canonical"
    ],
    errors="coerce"
)

vitals[
    "is_plausibility_issue"
] = (
    vitals[
        "is_plausibility_issue"
    ]
    .fillna(False)
    .astype(bool)
)

vitals[
    "is_retransmission"
] = (
    vitals[
        "is_retransmission"
    ]
    .fillna(False)
    .astype(bool)
)


# Retransmisiones no cuentan
# como eventos fisiologicos nuevos.

vitals = vitals[
    ~vitals[
        "is_retransmission"
    ]
].copy()


vitals = vitals[
    vitals[
        "variable_code"
    ].isin(
        VARIABLES
    )
].copy()


vitals = vitals.sort_values(
    [
        "patient_id",
        "timestamp"
    ]
)

print(
    "Vitales cargados:",
    len(vitals)
)


# ============================================================
# WEARABLE
# ============================================================

print(
    "\nCargando wearable..."
)

wearable = pd.read_csv(
    WEARABLE_PATH,
    usecols=[
        "wearable_observation_id",
        "patient_id",
        "device_id",
        "timestamp",
        "sync_datetime",
        "variable_code",
        "value",
        "unit"
    ]
)

wearable = wearable[
    wearable[
        "variable_code"
    ]
    == "ACTIVITY_LEVEL"
].copy()

wearable[
    "timestamp"
] = pd.to_datetime(
    wearable[
        "timestamp"
    ],
    format="mixed"
)

wearable[
    "sync_datetime"
] = pd.to_datetime(
    wearable[
        "sync_datetime"
    ],
    format="mixed"
)

print(
    "Contextos ACTIVITY_LEVEL:",
    len(wearable)
)


# ============================================================
# CALIDAD DE DISPOSITIVOS
# ============================================================

print(
    "\nCargando calidad de dispositivos..."
)

device_quality = pd.read_csv(
    DEVICE_QUALITY_PATH,
    usecols=[
        "device_observation_id",
        "patient_id",
        "encounter_id",
        "device_id",
        "timestamp",
        "variable_code",
        "value",
        "unit",
        "signal_quality"
    ]
)

device_quality[
    "timestamp"
] = pd.to_datetime(
    device_quality[
        "timestamp"
    ],
    format="mixed"
)

print(
    "Observaciones de calidad:",
    len(
        device_quality
    )
)


# ============================================================
# PATIENT CONTEXT
# ============================================================

print(
    "\nCargando contexto del paciente..."
)

patient_context = pd.read_csv(
    PATIENT_CONTEXT_PATH,
    usecols=[
        "context_id",
        "patient_id",
        "start_datetime",
        "end_datetime",
        "context_type",
        "context_value",
        "source",
        "confidence"
    ]
)

patient_context[
    "start_datetime"
] = pd.to_datetime(
    patient_context[
        "start_datetime"
    ],
    format="mixed"
)

patient_context[
    "end_datetime"
] = pd.to_datetime(
    patient_context[
        "end_datetime"
    ],
    format="mixed"
)

print(
    "Registros de contexto:",
    len(
        patient_context
    )
)


# ============================================================
# CONECTIVIDAD
# ============================================================

print(
    "\nCargando conectividad..."
)

connectivity = pd.read_csv(
    CONNECTIVITY_PATH,
    usecols=[
        "event_id",
        "device_id",
        "patient_id",
        "start_datetime",
        "end_datetime",
        "connectivity_status",
        "delayed_records",
        "packet_loss_estimate"
    ]
)

connectivity[
    "start_datetime"
] = pd.to_datetime(
    connectivity[
        "start_datetime"
    ],
    format="mixed"
)

connectivity[
    "end_datetime"
] = pd.to_datetime(
    connectivity[
        "end_datetime"
    ],
    format="mixed"
)

print(
    "Eventos de conectividad:",
    len(
        connectivity
    )
)


# ============================================================
# LABORATORIOS
# ============================================================

print(
    "\nCargando laboratorios..."
)

laboratory = pd.read_csv(
    LABORATORY_PATH,
    usecols=[
        "lab_result_id",
        "patient_id",
        "encounter_id",
        "test_code",
        "test_name",
        "result_value",
        "unit",
        "reference_low",
        "reference_high",
        "sample_datetime",
        "result_datetime",
        "facility_id",
        "source_system",
        "quality_flag"
    ]
)

laboratory[
    "sample_datetime"
] = pd.to_datetime(
    laboratory[
        "sample_datetime"
    ],
    format="mixed"
)

laboratory[
    "result_datetime"
] = pd.to_datetime(
    laboratory[
        "result_datetime"
    ],
    format="mixed"
)

laboratory[
    "result_value"
] = pd.to_numeric(
    laboratory[
        "result_value"
    ],
    errors="coerce"
)

laboratory[
    "reference_low"
] = pd.to_numeric(
    laboratory[
        "reference_low"
    ],
    errors="coerce"
)

laboratory[
    "reference_high"
] = pd.to_numeric(
    laboratory[
        "reference_high"
    ],
    errors="coerce"
)

print(
    "Resultados de laboratorio:",
    len(
        laboratory
    )
)


# ============================================================
# AGRUPAR POR PACIENTE
# ============================================================

vital_groups = vitals.groupby(
    "patient_id",
    sort=False
)

activity_groups = wearable.groupby(
    "patient_id",
    sort=False
)

quality_groups = device_quality.groupby(
    "patient_id",
    sort=False
)

context_groups = patient_context.groupby(
    "patient_id",
    sort=False
)

connectivity_groups = connectivity.groupby(
    "patient_id",
    sort=False
)

laboratory_groups = laboratory.groupby(
    "patient_id",
    sort=False
)


# ============================================================
# RESULTADOS
# ============================================================

signal_rows = []
evidence_rows = []

signal_counter = 1

processed_patients = 0
skipped_patients = 0


# ============================================================
# PROCESAR PACIENTES
# ============================================================

print(
    "\nProcesando pacientes...\n"
)

for patient_index, patient_id in enumerate(
    patient_ids,
    start=1
):

    try:

        patient_vitals = (
            vital_groups
            .get_group(
                patient_id
            )
            .copy()
        )

    except KeyError:

        skipped_patients += 1
        continue


    if patient_vitals.empty:

        skipped_patients += 1
        continue


    patient_activity = get_group_or_empty(
        activity_groups,
        patient_id,
        wearable
    )

    patient_quality = get_group_or_empty(
        quality_groups,
        patient_id,
        device_quality
    )

    patient_context_data = get_group_or_empty(
        context_groups,
        patient_id,
        patient_context
    )

    patient_connectivity = get_group_or_empty(
        connectivity_groups,
        patient_id,
        connectivity
    )

    patient_labs = get_group_or_empty(
        laboratory_groups,
        patient_id,
        laboratory
    )


    # ========================================================
    # BASELINE
    # ========================================================

    patient_start = (
        patient_vitals[
            "timestamp"
        ].min()
    )

    (
        baseline,
        baseline_end
    ) = calculate_baseline(
        patient_vitals,
        patient_start
    )


    if len(baseline) < MIN_VARIABLES:

        skipped_patients += 1
        continue


    # ========================================================
    # SERIES TEMPORALES
    # ========================================================

    variable_arrays = (
        prepare_variable_arrays(
            patient_vitals
        )
    )


    valid_for_end = patient_vitals[
        (
            patient_vitals[
                "quality_flag"
            ]
            == "OK"
        )
        &
        (
            ~patient_vitals[
                "is_plausibility_issue"
            ]
        )
    ]


    if valid_for_end.empty:

        skipped_patients += 1
        continue


    analysis_end = (
        valid_for_end[
            "timestamp"
        ].max()
    )


    if analysis_end < baseline_end:

        skipped_patients += 1
        continue


    # ========================================================
    # DECISIONES
    # ========================================================

    decision_times = pd.date_range(
        start=baseline_end,
        end=analysis_end,
        freq=f"{STEP_HOURS}h"
    )


    consecutive = 0
    episode_start = None
    episode_active = False


    # ========================================================
    # RECORRER VENTANAS
    # ========================================================

    for decision_time in decision_times:

        (
            zscores,
            window_start
        ) = calculate_window_zscores(
            decision_time,
            baseline,
            variable_arrays
        )


        trigger_variables = [
            variable
            for variable, zscore
            in zscores.items()
            if (
                pd.notna(zscore)
                and
                abs(zscore)
                >= Z_THRESHOLD
            )
        ]


        variables_over_threshold = (
            len(
                trigger_variables
            )
        )


        anomalous = (
            variables_over_threshold
            >= MIN_VARIABLES
        )


        # ====================================================
        # VENTANA ANOMALA
        # ====================================================

        if anomalous:

            if consecutive == 0:

                episode_start = (
                    window_start
                )

            consecutive += 1


            # =================================================
            # CONFIRMAR EPISODIO
            # =================================================

            if (
                consecutive
                >= MIN_CONSECUTIVE_WINDOWS
                and
                not episode_active
            ):

                max_abs_zscore = max(
                    abs(
                        zscores[
                            variable
                        ]
                    )
                    for variable
                    in trigger_variables
                )


                # =============================================
                # ACTIVIDAD + CALIDAD
                # =============================================

                (
                    activity_fraction,
                    quality_score,
                    activity_period,
                    quality_period
                ) = calculate_context_scores(
                    patient_activity,
                    patient_quality,
                    episode_start,
                    decision_time
                )


                # =============================================
                # CONTEXTO + CONECTIVIDAD
                # =============================================

                (
                    context_period,
                    connectivity_period
                ) = get_additional_context(
                    patient_context_data,
                    patient_connectivity,
                    episode_start,
                    decision_time
                )


                # =============================================
                # LABORATORIO DISPONIBLE
                # =============================================

                laboratory_period = (
                    get_laboratory_support(
                        patient_labs,
                        episode_start,
                        decision_time
                    )
                )


                # =============================================
                # RISK SCORE
                # =============================================

                risk_score = calculate_risk_score(
                    max_abs_zscore,
                    variables_over_threshold,
                    consecutive,
                    quality_score,
                    activity_fraction
                )

                priority = get_priority(
                    risk_score
                )


                # =============================================
                # SIGNAL ID
                # =============================================

                signal_id = (
                    f"SIGNAL-"
                    f"{signal_counter:06d}"
                )

                signal_counter += 1


                # =============================================
                # EXPLICACION
                # =============================================

                movements = []

                for variable in trigger_variables:

                    z = zscores[
                        variable
                    ]

                    if z > 0:
                        direction = "aumento"

                    else:
                        direction = "descenso"

                    movements.append(
                        f"{variable}: "
                        f"{direction} "
                        f"({z:.2f} z)"
                    )


                explanation = (
                    "Desviación multivariable "
                    "persistente respecto del "
                    "baseline personal. "
                    +
                    "; ".join(
                        movements
                    )
                    +
                    ". Persistencia observada: "
                    f"{consecutive} ventanas "
                    "consecutivas."
                )


                # =============================================
                # CALIDAD EN EXPLICACION
                # =============================================

                if (
                    quality_score is not None
                    and
                    pd.notna(
                        quality_score
                    )
                ):

                    explanation += (
                        " Calidad de dispositivo "
                        "promedio: "
                        f"{quality_score:.2f}."
                    )

                else:

                    explanation += (
                        " Sin observaciones de "
                        "calidad disponibles durante "
                        "la ventana; se aplicó "
                        "penalización por incertidumbre."
                    )


                # =============================================
                # ACTIVIDAD EN EXPLICACION
                # =============================================

                if activity_fraction == 0:

                    explanation += (
                        " Sin actividad física "
                        "moderada/alta registrada "
                        "en la evidencia disponible."
                    )

                elif activity_fraction >= 0.50:

                    explanation += (
                        " Se observó actividad física "
                        "moderada/alta; el score fue "
                        "ajustado por contexto."
                    )


                # =============================================
                # CONTEXTO EN EXPLICACION
                # =============================================

                if len(context_period) > 0:

                    explanation += (
                        " Existe contexto de sueño "
                        "o recuperación con al menos "
                        f"{MIN_CONTEXT_OVERLAP_MINUTES} "
                        "minutos de superposición "
                        "con la ventana."
                    )


                # =============================================
                # CONECTIVIDAD EN EXPLICACION
                # =============================================

                if len(connectivity_period) > 0:

                    explanation += (
                        " Se registraron eventos de "
                        "conectividad con superposición "
                        "temporal relevante."
                    )


                # =============================================
                # LABS EN EXPLICACION
                # =============================================

                if len(laboratory_period) > 0:

                    explanation += (
                        f" {len(laboratory_period)} "
                        "resultado(s) de laboratorio "
                        "estaban disponibles dentro "
                        "de la ventana y se adjuntan "
                        "como evidencia de apoyo; "
                        "no modifican el risk score."
                    )


                # =============================================
                # CONFIDENCE
                # =============================================

                if (
                    quality_score is not None
                    and
                    pd.notna(
                        quality_score
                    )
                ):

                    confidence_score = max(
                        0.0,
                        min(
                            float(
                                quality_score
                            ),
                            1.0
                        )
                    )

                else:

                    confidence_score = 0.5


                # =============================================
                # SIGNAL
                # =============================================

                signal_rows.append(
                    {
                        "signal_id":
                            signal_id,

                        "patient_id":
                            patient_id,

                        "decision_datetime":
                            decision_time,

                        "risk_score":
                            round(
                                risk_score,
                                4
                            ),

                        "priority_level":
                            priority,

                        "confidence_score":
                            round(
                                confidence_score,
                                4
                            ),

                        "evidence_start":
                            episode_start,

                        "evidence_end":
                            decision_time,

                        "explanation":
                            explanation,

                        "model_version":
                            MODEL_VERSION
                    }
                )


                # =============================================
                # PRIMARY - VITALES
                # =============================================

                primary = patient_vitals[
                    (
                        patient_vitals[
                            "timestamp"
                        ]
                        >= episode_start
                    )
                    &
                    (
                        patient_vitals[
                            "timestamp"
                        ]
                        <= decision_time
                    )
                    &
                    (
                        patient_vitals[
                            "variable_code"
                        ].isin(
                            trigger_variables
                        )
                    )
                    &
                    (
                        patient_vitals[
                            "quality_flag"
                        ]
                        == "OK"
                    )
                    &
                    (
                        ~patient_vitals[
                            "is_plausibility_issue"
                        ]
                    )
                ].copy()


                for _, row in primary.iterrows():

                    evidence_rows.append(
                        {
                            "signal_id":
                                signal_id,

                            "source_file":
                                "vital_signs.csv",

                            "record_id":
                                row[
                                    "observation_id"
                                ],

                            "variable_code":
                                row[
                                    "variable_code"
                                ],

                            "event_datetime":
                                row[
                                    "timestamp"
                                ],

                            "available_datetime":
                                row[
                                    "timestamp"
                                ],

                            "evidence_role":
                                "PRIMARY",

                            "contribution":
                                1.0
                        }
                    )


                # =============================================
                # CONTEXT - WEARABLE
                # =============================================

                for _, row in activity_period.iterrows():

                    evidence_rows.append(
                        {
                            "signal_id":
                                signal_id,

                            "source_file":
                                "wearable_observations.csv",

                            "record_id":
                                row[
                                    "wearable_observation_id"
                                ],

                            "variable_code":
                                "ACTIVITY_LEVEL",

                            "event_datetime":
                                row[
                                    "timestamp"
                                ],

                            "available_datetime":
                                row[
                                    "sync_datetime"
                                ],

                            "evidence_role":
                                "CONTEXT",

                            "contribution":
                                0.0
                        }
                    )


                # =============================================
                # QUALITY - DEVICE
                # =============================================

                for _, row in quality_period.iterrows():

                    evidence_rows.append(
                        {
                            "signal_id":
                                signal_id,

                            "source_file":
                                "device_observations.csv",

                            "record_id":
                                row[
                                    "device_observation_id"
                                ],

                            "variable_code":
                                row[
                                    "variable_code"
                                ],

                            "event_datetime":
                                row[
                                    "timestamp"
                                ],

                            "available_datetime":
                                row[
                                    "timestamp"
                                ],

                            "evidence_role":
                                "QUALITY",

                            "contribution":
                                0.0
                        }
                    )


                # =============================================
                # CONTEXT - PATIENT CONTEXT
                # =============================================

                for _, row in context_period.iterrows():

                    evidence_rows.append(
                        {
                            "signal_id":
                                signal_id,

                            "source_file":
                                "patient_context.csv",

                            "record_id":
                                row[
                                    "context_id"
                                ],

                            "variable_code":
                                row[
                                    "context_type"
                                ],

                            "event_datetime":
                                row[
                                    "start_datetime"
                                ],

                            "available_datetime":
                                row[
                                    "start_datetime"
                                ],

                            "evidence_role":
                                "CONTEXT",

                            "contribution":
                                0.0
                        }
                    )


                # =============================================
                # QUALITY - CONNECTIVITY
                # =============================================

                for _, row in connectivity_period.iterrows():

                    evidence_rows.append(
                        {
                            "signal_id":
                                signal_id,

                            "source_file":
                                "connectivity_events.csv",

                            "record_id":
                                row[
                                    "event_id"
                                ],

                            "variable_code":
                                "CONNECTIVITY",

                            "event_datetime":
                                row[
                                    "start_datetime"
                                ],

                            "available_datetime":
                                row[
                                    "start_datetime"
                                ],

                            "evidence_role":
                                "QUALITY",

                            "contribution":
                                0.0
                        }
                    )


                # =============================================
                # SUPPORTING - LABORATORIOS
                #
                # sample_datetime = evento
                # result_datetime = disponibilidad
                # =============================================

                for _, row in laboratory_period.iterrows():

                    evidence_rows.append(
                        {
                            "signal_id":
                                signal_id,

                            "source_file":
                                "laboratory_results.csv",

                            "record_id":
                                row[
                                    "lab_result_id"
                                ],

                            "variable_code":
                                row[
                                    "test_code"
                                ],

                            "event_datetime":
                                row[
                                    "sample_datetime"
                                ],

                            "available_datetime":
                                row[
                                    "result_datetime"
                                ],

                            "evidence_role":
                                "SUPPORTING",

                            "contribution":
                                0.0
                        }
                    )


                # Solo una señal por episodio continuo.
                episode_active = True


        # ====================================================
        # TERMINO EL EPISODIO
        # ====================================================

        else:

            consecutive = 0
            episode_start = None
            episode_active = False


    processed_patients += 1


    # ========================================================
    # PROGRESO
    # ========================================================

    if (
        patient_index % 50 == 0
        or
        patient_index
        == len(
            patient_ids
        )
    ):

        print(
            f"[{patient_index}/"
            f"{len(patient_ids)}] "
            "Pacientes procesados | "
            f"Señales: "
            f"{len(signal_rows)}"
        )


# ============================================================
# DATAFRAMES FINALES
# ============================================================

signals_output = pd.DataFrame(
    signal_rows,
    columns=SIGNALS_COLUMNS
)

evidence_output = pd.DataFrame(
    evidence_rows,
    columns=EVIDENCE_COLUMNS
)


# ============================================================
# VALIDACIONES INTERNAS
# ============================================================

print()
print("==========================================")
print(" VALIDACIONES INTERNAS")
print("==========================================")

print(
    "Pacientes procesados:",
    processed_patients
)

print(
    "Pacientes omitidos:",
    skipped_patients
)

print(
    "Señales generadas:",
    len(signals_output)
)

print(
    "Evidencias generadas:",
    len(evidence_output)
)


# ------------------------------------------------------------
# SIGNAL IDS DUPLICADOS
# ------------------------------------------------------------

duplicate_signals = (
    signals_output[
        "signal_id"
    ].duplicated().sum()
)

print(
    "Signal IDs duplicados:",
    duplicate_signals
)


# ------------------------------------------------------------
# SEÑALES SIN EVIDENCIA
# ------------------------------------------------------------

if len(signals_output) > 0:

    signals_without_evidence = (
        set(
            signals_output[
                "signal_id"
            ]
        )
        -
        set(
            evidence_output[
                "signal_id"
            ]
        )
    )

else:

    signals_without_evidence = set()


print(
    "Señales sin evidencia:",
    len(
        signals_without_evidence
    )
)


# ------------------------------------------------------------
# EVIDENCIA FUTURA
# ------------------------------------------------------------

if (
    len(signals_output) > 0
    and
    len(evidence_output) > 0
):

    validation = evidence_output.merge(
        signals_output[
            [
                "signal_id",
                "decision_datetime"
            ]
        ],
        on="signal_id",
        how="left"
    )

    future_evidence = validation[
        validation[
            "available_datetime"
        ]
        >
        validation[
            "decision_datetime"
        ]
    ]

    future_count = len(
        future_evidence
    )

else:

    future_count = 0


print(
    "Evidencias disponibles "
    "después de la decisión:",
    future_count
)


# ------------------------------------------------------------
# SCORES INVALIDOS
# ------------------------------------------------------------

if len(signals_output) > 0:

    invalid_scores = signals_output[
        (
            signals_output[
                "risk_score"
            ]
            < 0
        )
        |
        (
            signals_output[
                "risk_score"
            ]
            > 1
        )
    ]

    invalid_score_count = len(
        invalid_scores
    )

else:

    invalid_score_count = 0


print(
    "Risk scores inválidos:",
    invalid_score_count
)


# ============================================================
# GUARDAR
# ============================================================

signals_path = (
    RESULTS_DIR
    / "signals.csv"
)

evidence_path = (
    RESULTS_DIR
    / "evidence.csv"
)


signals_output.to_csv(
    signals_path,
    index=False,
    encoding="utf-8"
)

evidence_output.to_csv(
    evidence_path,
    index=False,
    encoding="utf-8"
)


# ============================================================
# RESUMEN
# ============================================================

print()
print("==========================================")
print(" RESUMEN V0.3")
print("==========================================")


if len(signals_output) > 0:

    print(
        "\nPrioridades:"
    )

    print(
        signals_output[
            "priority_level"
        ].value_counts()
    )


    print(
        "\nRisk score:"
    )

    print(
        signals_output[
            "risk_score"
        ].describe()
    )


    print(
        "\nPacientes con señales:",
        signals_output[
            "patient_id"
        ].nunique()
    )


    print(
        "\nEvidencia por rol:"
    )

    print(
        evidence_output[
            "evidence_role"
        ].value_counts()
    )


    print(
        "\nEvidencia por fuente:"
    )

    print(
        evidence_output[
            "source_file"
        ].value_counts()
    )


    # ========================================================
    # CUANTAS SEÑALES TIENEN CADA NUEVA FUENTE
    # ========================================================

    context_signal_count = (
        evidence_output[
            evidence_output[
                "source_file"
            ]
            == "patient_context.csv"
        ][
            "signal_id"
        ].nunique()
    )

    connectivity_signal_count = (
        evidence_output[
            evidence_output[
                "source_file"
            ]
            == "connectivity_events.csv"
        ][
            "signal_id"
        ].nunique()
    )

    laboratory_signal_count = (
        evidence_output[
            evidence_output[
                "source_file"
            ]
            == "laboratory_results.csv"
        ][
            "signal_id"
        ].nunique()
    )


    print(
        "\nSeñales con patient_context:",
        context_signal_count
    )

    print(
        "Señales con connectivity:",
        connectivity_signal_count
    )

    print(
        "Señales con laboratorio SUPPORTING:",
        laboratory_signal_count
    )


    print(
        "\nPrimeras 10 señales:"
    )

    print(
        signals_output[
            [
                "signal_id",
                "patient_id",
                "decision_datetime",
                "risk_score",
                "priority_level",
                "confidence_score"
            ]
        ]
        .head(10)
        .to_string(
            index=False
        )
    )

else:

    print(
        "No se generaron señales."
    )


# ============================================================
# CONTROL PAT-0001
# ============================================================

if len(signals_output) > 0:

    pat_0001 = signals_output[
        signals_output[
            "patient_id"
        ]
        == "PAT-0001"
    ]

    print()
    print("==========================================")
    print(" CONTROL PAT-0001")
    print("==========================================")

    if len(pat_0001) > 0:

        print(
            pat_0001[
                [
                    "signal_id",
                    "decision_datetime",
                    "risk_score",
                    "priority_level",
                    "confidence_score"
                ]
            ].to_string(
                index=False
            )
        )

    else:

        print(
            "ADVERTENCIA: "
            "PAT-0001 no generó señal."
        )


# ============================================================
# FINAL
# ============================================================

elapsed = (
    time.time()
    -
    start_time
)

print(
    "\nArchivos generados:"
)

print(
    signals_path
)

print(
    evidence_path
)

print(
    f"\nTiempo total: "
    f"{elapsed:.1f} segundos"
)

print()
print("==========================================")
print(" PIPELINE V0.3 TERMINADO")
print("==========================================")