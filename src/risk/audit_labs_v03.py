from pathlib import Path
import pandas as pd


# ============================================================
# RUTAS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
RESULTS_DIR = PROJECT_ROOT / "results"

SIGNALS_PATH = RESULTS_DIR / "signals.csv"
EVIDENCE_PATH = RESULTS_DIR / "evidence.csv"
LABS_PATH = RAW_DIR / "laboratory_results.csv"


# ============================================================
# CARGAR DATOS
# ============================================================

print()
print("==========================================")
print(" AUDITORIA LABORATORIOS RISA V0.3")
print("==========================================")

signals = pd.read_csv(
    SIGNALS_PATH
)

evidence = pd.read_csv(
    EVIDENCE_PATH
)

labs = pd.read_csv(
    LABS_PATH
)


# ============================================================
# CONVERTIR FECHAS
# ============================================================

signals["decision_datetime"] = pd.to_datetime(
    signals["decision_datetime"],
    format="mixed"
)

evidence["event_datetime"] = pd.to_datetime(
    evidence["event_datetime"],
    format="mixed"
)

evidence["available_datetime"] = pd.to_datetime(
    evidence["available_datetime"],
    format="mixed"
)

labs["sample_datetime"] = pd.to_datetime(
    labs["sample_datetime"],
    format="mixed"
)

labs["result_datetime"] = pd.to_datetime(
    labs["result_datetime"],
    format="mixed"
)


# ============================================================
# SOLO LABORATORIOS SUPPORTING
# ============================================================

lab_evidence = evidence[
    (
        evidence["source_file"]
        == "laboratory_results.csv"
    )
    &
    (
        evidence["evidence_role"]
        == "SUPPORTING"
    )
].copy()


print()
print("==========================================")
print(" RESUMEN GENERAL")
print("==========================================")

print(
    "Señales totales:",
    len(signals)
)

print(
    "Evidencias totales:",
    len(evidence)
)

print(
    "Evidencias de laboratorio SUPPORTING:",
    len(lab_evidence)
)

print(
    "Señales con laboratorio:",
    lab_evidence["signal_id"].nunique()
)


# ============================================================
# UNIR CON LABORATORY_RESULTS
# ============================================================

detail = lab_evidence.merge(
    labs,
    left_on="record_id",
    right_on="lab_result_id",
    how="left",
    suffixes=(
        "_evidence",
        "_lab"
    )
)


# ============================================================
# UNIR CON SIGNALS
# ============================================================

detail = detail.merge(
    signals[
        [
            "signal_id",
            "patient_id",
            "decision_datetime",
            "risk_score",
            "priority_level",
            "confidence_score"
        ]
    ],
    on="signal_id",
    how="left",
    suffixes=(
        "_lab",
        "_signal"
    )
)


# ============================================================
# VALIDACIONES TEMPORALES
# ============================================================

print()
print("==========================================")
print(" VALIDACIONES TEMPORALES")
print("==========================================")


# Resultado disponible después de decisión
future_results = detail[
    detail["result_datetime"]
    >
    detail["decision_datetime"]
]

print(
    "Resultados disponibles DESPUES "
    "de la decisión:",
    len(future_results)
)


# Evidencia available_datetime posterior
future_evidence = detail[
    detail["available_datetime"]
    >
    detail["decision_datetime"]
]

print(
    "available_datetime > decision_datetime:",
    len(future_evidence)
)


# Result before sample
invalid_lab_order = detail[
    detail["result_datetime"]
    <
    detail["sample_datetime"]
]

print(
    "result_datetime < sample_datetime:",
    len(invalid_lab_order)
)


# La disponibilidad registrada en evidence
# debe coincidir con result_datetime
availability_mismatch = detail[
    detail["available_datetime"]
    !=
    detail["result_datetime"]
]

print(
    "available_datetime distinto "
    "de result_datetime:",
    len(availability_mismatch)
)


# El evento debe corresponder a sample_datetime
event_mismatch = detail[
    detail["event_datetime"]
    !=
    detail["sample_datetime"]
]

print(
    "event_datetime distinto "
    "de sample_datetime:",
    len(event_mismatch)
)


# ============================================================
# REGISTROS QUE NO SE ENCONTRARON EN RAW
# ============================================================

missing_raw = detail[
    detail["lab_result_id"].isna()
]

print(
    "record_id sin correspondencia "
    "en laboratory_results.csv:",
    len(missing_raw)
)


# ============================================================
# TEST CODES
# ============================================================

print()
print("==========================================")
print(" LABORATORIOS UTILIZADOS")
print("==========================================")

print(
    detail[
        "test_code"
    ]
    .value_counts(
        dropna=False
    )
    .to_string()
)


# ============================================================
# RESULTADOS FUERA DE REFERENCIA
#
# Esto es SOLO contexto.
# No se interpreta automáticamente como riesgo.
# ============================================================

detail["outside_reference"] = (
    (
        detail["result_value"]
        <
        detail["reference_low"]
    )
    |
    (
        detail["result_value"]
        >
        detail["reference_high"]
    )
)


print()
print("==========================================")
print(" REFERENCIA DE LABORATORIO")
print("==========================================")

print(
    "SUPPORTING dentro de referencia:",
    int(
        (
            ~detail["outside_reference"]
        ).sum()
    )
)

print(
    "SUPPORTING fuera de referencia:",
    int(
        detail[
            "outside_reference"
        ].sum()
    )
)


if detail["outside_reference"].any():

    print(
        "\nFuera de referencia por test:"
    )

    print(
        detail[
            detail[
                "outside_reference"
            ]
        ][
            "test_code"
        ]
        .value_counts()
        .to_string()
    )


# ============================================================
# PRIORIDAD DE LAS SEÑALES CON LABS
# ============================================================

signals_with_labs = signals[
    signals["signal_id"].isin(
        lab_evidence[
            "signal_id"
        ].unique()
    )
].copy()


print()
print("==========================================")
print(" PRIORIDADES CON LABORATORIO")
print("==========================================")

print(
    signals_with_labs[
        "priority_level"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# TOP SEÑALES CON LABORATORIOS
# ============================================================

print()
print("==========================================")
print(" TOP SEÑALES CON LABORATORIOS")
print("==========================================")


top_signals = (
    signals_with_labs.sort_values(
        "risk_score",
        ascending=False
    )
)


for _, signal in top_signals.iterrows():

    signal_id = signal[
        "signal_id"
    ]

    signal_labs = detail[
        detail[
            "signal_id"
        ]
        == signal_id
    ]


    print()
    print("=" * 75)

    print(
        "Signal:",
        signal_id
    )

    print(
        "Paciente:",
        signal[
            "patient_id"
        ]
    )

    print(
        "Decisión:",
        signal[
            "decision_datetime"
        ]
    )

    print(
        "Risk score:",
        signal[
            "risk_score"
        ]
    )

    print(
        "Prioridad:",
        signal[
            "priority_level"
        ]
    )

    print(
        "Confidence:",
        signal[
            "confidence_score"
        ]
    )

    print(
        "\nLaboratorios SUPPORTING:",
        len(signal_labs)
    )


    for _, lab in signal_labs.iterrows():

        print()
        print(
            "  -----------------------------"
        )

        print(
            "  Test:",
            lab[
                "test_code"
            ]
        )

        print(
            "  Resultado:",
            lab[
                "result_value"
            ],
            lab[
                "unit"
            ]
        )

        print(
            "  Referencia:",
            lab[
                "reference_low"
            ],
            "-",
            lab[
                "reference_high"
            ]
        )

        print(
            "  Fuera referencia:",
            lab[
                "outside_reference"
            ]
        )

        print(
            "  Muestra:",
            lab[
                "sample_datetime"
            ]
        )

        print(
            "  Disponible:",
            lab[
                "result_datetime"
            ]
        )


# ============================================================
# RESULTADO FINAL
# ============================================================

problems = (
    len(future_results)
    +
    len(future_evidence)
    +
    len(invalid_lab_order)
    +
    len(availability_mismatch)
    +
    len(event_mismatch)
    +
    len(missing_raw)
)


print()
print("==========================================")
print(" RESULTADO AUDITORIA")
print("==========================================")

print(
    "Problemas estructurales/temporales:",
    problems
)

if problems == 0:

    print(
        "AUDITORIA LABS: PASS"
    )

else:

    print(
        "AUDITORIA LABS: REVISAR"
    )


print()
print("==========================================")
print(" AUDITORIA TERMINADA")
print("==========================================")