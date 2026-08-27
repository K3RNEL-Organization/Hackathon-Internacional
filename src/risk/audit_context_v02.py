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

PATIENT_CONTEXT_PATH = (
    RAW_DIR / "patient_context.csv"
)

CONNECTIVITY_PATH = (
    RAW_DIR / "connectivity_events.csv"
)


# ============================================================
# CARGAR DATOS
# ============================================================

print()
print("==========================================")
print(" AUDITORIA CONTEXTO RISA V0.2")
print("==========================================")

signals = pd.read_csv(
    SIGNALS_PATH
)

evidence = pd.read_csv(
    EVIDENCE_PATH
)

patient_context = pd.read_csv(
    PATIENT_CONTEXT_PATH
)

connectivity = pd.read_csv(
    CONNECTIVITY_PATH
)


print(
    "\nSeñales totales:",
    len(signals)
)

print(
    "Evidencias totales:",
    len(evidence)
)


# ============================================================
# EVIDENCIA DE CONTEXTO
# ============================================================

context_evidence = evidence[
    evidence["source_file"]
    == "patient_context.csv"
].copy()


# ============================================================
# EVIDENCIA DE CONECTIVIDAD
# ============================================================

connectivity_evidence = evidence[
    evidence["source_file"]
    == "connectivity_events.csv"
].copy()


# ============================================================
# SIGNAL IDS
# ============================================================

context_signal_ids = set(
    context_evidence["signal_id"]
)

connectivity_signal_ids = set(
    connectivity_evidence["signal_id"]
)

both_signal_ids = (
    context_signal_ids
    &
    connectivity_signal_ids
)


print()
print("==========================================")
print(" COBERTURA DE CONTEXTO")
print("==========================================")

print(
    "Evidencias patient_context:",
    len(context_evidence)
)

print(
    "Señales con patient_context:",
    len(context_signal_ids)
)

print(
    "Evidencias connectivity:",
    len(connectivity_evidence)
)

print(
    "Señales con connectivity:",
    len(connectivity_signal_ids)
)

print(
    "Señales con ambos:",
    len(both_signal_ids)
)


# ============================================================
# PORCENTAJE DE SEÑALES
# ============================================================

if len(signals) > 0:

    context_percentage = (
        len(context_signal_ids)
        * 100
        / len(signals)
    )

    connectivity_percentage = (
        len(connectivity_signal_ids)
        * 100
        / len(signals)
    )

else:

    context_percentage = 0
    connectivity_percentage = 0


print(
    f"\n% señales con contexto: "
    f"{context_percentage:.2f}%"
)

print(
    f"% señales con conectividad: "
    f"{connectivity_percentage:.2f}%"
)


# ============================================================
# UNIR PATIENT_CONTEXT CON EVIDENCE
# ============================================================

if not context_evidence.empty:

    context_detail = (
        context_evidence.merge(
            patient_context,
            left_on="record_id",
            right_on="context_id",
            how="left",
            suffixes=(
                "_evidence",
                "_raw"
            )
        )
    )


    print()
    print("==========================================")
    print(" TIPOS DE CONTEXTO")
    print("==========================================")

    if "context_type" in context_detail.columns:

        print(
            context_detail[
                "context_type"
            ]
            .value_counts(
                dropna=False
            )
            .to_string()
        )


    if "context_value" in context_detail.columns:

        print()
        print("Valores de contexto:")

        print(
            context_detail[
                "context_value"
            ]
            .value_counts(
                dropna=False
            )
            .head(20)
            .to_string()
        )


# ============================================================
# PRIORIDADES DE SEÑALES CON CONTEXTO
# ============================================================

signals_with_context = signals[
    signals["signal_id"].isin(
        context_signal_ids
    )
].copy()


if not signals_with_context.empty:

    print()
    print("==========================================")
    print(" PRIORIDADES CON CONTEXTO")
    print("==========================================")

    print(
        signals_with_context[
            "priority_level"
        ]
        .value_counts()
        .to_string()
    )


# ============================================================
# DETALLE DE CONECTIVIDAD
# ============================================================

if not connectivity_evidence.empty:

    connectivity_detail = (
        connectivity_evidence.merge(
            connectivity,
            left_on="record_id",
            right_on="event_id",
            how="left",
            suffixes=(
                "_evidence",
                "_raw"
            )
        )
    )


    print()
    print("==========================================")
    print(" ESTADOS DE CONECTIVIDAD")
    print("==========================================")

    if (
        "connectivity_status"
        in connectivity_detail.columns
    ):

        print(
            connectivity_detail[
                "connectivity_status"
            ]
            .value_counts(
                dropna=False
            )
            .to_string()
        )


    print()
    print("==========================================")
    print(" SEÑALES CON PROBLEMAS DE CONECTIVIDAD")
    print("==========================================")


    signals_with_connectivity = signals[
        signals[
            "signal_id"
        ].isin(
            connectivity_signal_ids
        )
    ].copy()


    signals_with_connectivity = (
        signals_with_connectivity.sort_values(
            "risk_score",
            ascending=False
        )
    )


    for _, signal in (
        signals_with_connectivity.iterrows()
    ):

        signal_id = signal[
            "signal_id"
        ]

        conn = connectivity_detail[
            connectivity_detail[
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
            signal["patient_id"]
        )

        print(
            "Decisión:",
            signal["decision_datetime"]
        )

        print(
            "Risk score:",
            signal["risk_score"]
        )

        print(
            "Prioridad:",
            signal["priority_level"]
        )

        print(
            "Confidence:",
            signal[
                "confidence_score"
            ]
        )


        print("\nExplicación:")

        print(
            signal[
                "explanation"
            ]
        )


        print(
            "\nEventos de conectividad:",
            len(conn)
        )


        for _, row in conn.iterrows():

            print(
                "\n  -----------------------------"
            )

            print(
                "  Estado:",
                row.get(
                    "connectivity_status",
                    "N/D"
                )
            )

            print(
                "  Inicio:",
                row.get(
                    "start_datetime",
                    "N/D"
                )
            )

            print(
                "  Fin:",
                row.get(
                    "end_datetime",
                    "N/D"
                )
            )

            print(
                "  Registros demorados:",
                row.get(
                    "delayed_records",
                    "N/D"
                )
            )

            print(
                "  Packet loss:",
                row.get(
                    "packet_loss_estimate",
                    "N/D"
                )
            )


# ============================================================
# TOP SEÑALES CON CONTEXTO
# ============================================================

if not signals_with_context.empty:

    print()
    print("==========================================")
    print(" TOP 15 SEÑALES CON CONTEXTO")
    print("==========================================")

    top_context = (
        signals_with_context.sort_values(
            "risk_score",
            ascending=False
        )
        .head(15)
    )


    for _, signal in top_context.iterrows():

        signal_id = signal[
            "signal_id"
        ]

        context_signal = context_detail[
            context_detail[
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


        if (
            "context_type"
            in context_signal.columns
        ):

            print(
                "\nContextos:"
            )

            cols = [
                column
                for column in [
                    "context_type",
                    "context_value",
                    "start_datetime",
                    "end_datetime",
                    "confidence"
                ]
                if column
                in context_signal.columns
            ]

            print(
                context_signal[
                    cols
                ]
                .drop_duplicates()
                .to_string(
                    index=False
                )
            )


# ============================================================
# SEÑALES CRITICAL CON CONTEXTO / CONECTIVIDAD
# ============================================================

critical = signals[
    signals[
        "priority_level"
    ]
    == "CRITICAL"
].copy()


critical_context = critical[
    critical[
        "signal_id"
    ].isin(
        context_signal_ids
    )
]

critical_connectivity = critical[
    critical[
        "signal_id"
    ].isin(
        connectivity_signal_ids
    )
]


print()
print("==========================================")
print(" CRITICAL")
print("==========================================")

print(
    "CRITICAL totales:",
    len(critical)
)

print(
    "CRITICAL con patient_context:",
    len(
        critical_context
    )
)

print(
    "CRITICAL con connectivity:",
    len(
        critical_connectivity
    )
)


# ============================================================
# RESUMEN FINAL
# ============================================================

print()
print("==========================================")
print(" RESUMEN AUDITORIA")
print("==========================================")

print(
    "Señales analizadas:",
    len(signals)
)

print(
    "Señales con contexto:",
    len(context_signal_ids)
)

print(
    "Señales con conectividad:",
    len(connectivity_signal_ids)
)

print(
    "Señales con ambos:",
    len(both_signal_ids)
)

print(
    "CRITICAL con contexto:",
    len(critical_context)
)

print(
    "CRITICAL con conectividad:",
    len(critical_connectivity)
)

print()
print("==========================================")
print(" AUDITORIA TERMINADA")
print("==========================================")