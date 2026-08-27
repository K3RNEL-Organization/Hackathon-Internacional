import pandas as pd
import os

# ==================================================
# CONFIGURACION
# ==================================================

PATIENT_ID = "PAT-0001"

# Decisiones del MVP, NO umbrales clínicos
Z_THRESHOLD = 2.0
MIN_VARIABLES = 2
MIN_CONSECUTIVE_WINDOWS = 2

VARIABLES = [
    "HR",
    "RR",
    "SpO2",
    "TEMP",
    "SBP",
    "DBP"
]

print(f"\n=== DETECTOR DE SEÑALES PARA {PATIENT_ID} ===")


# ==================================================
# CARGAR FEATURES
# ==================================================

features = pd.read_parquet(
    f"data/processed/features/"
    f"{PATIENT_ID}_features.parquet"
)

features["decision_datetime"] = pd.to_datetime(
    features["decision_datetime"]
)

features["window_start"] = pd.to_datetime(
    features["window_start"]
)

features = features.sort_values(
    "decision_datetime"
).reset_index(drop=True)


# ==================================================
# CALCULAR DESVIACIONES
# ==================================================

for variable in VARIABLES:

    features[
        f"{variable}_abs_zscore"
    ] = features[
        f"{variable}_zscore"
    ].abs()


# ==================================================
# CONTAR VARIABLES DESVIADAS
# ==================================================

abs_columns = [
    f"{variable}_abs_zscore"
    for variable in VARIABLES
]

features["variables_over_threshold"] = (
    features[abs_columns] >= Z_THRESHOLD
).sum(axis=1)

features["is_anomalous_window"] = (
    features["variables_over_threshold"]
    >= MIN_VARIABLES
)


# ==================================================
# FUNCION PARA SABER QUE VARIABLES DISPARARON
# ==================================================

def get_trigger_variables(row):

    trigger_variables = []

    for variable in VARIABLES:

        z = row[f"{variable}_zscore"]

        if pd.notna(z) and abs(z) >= Z_THRESHOLD:
            trigger_variables.append(variable)

    return trigger_variables


# ==================================================
# DETECTAR EPISODIOS PERSISTENTES
# ==================================================

signals = []

consecutive = 0
episode_start_index = None
episode_active = False

signal_number = 1


for i, row in features.iterrows():

    if row["is_anomalous_window"]:

        if consecutive == 0:
            episode_start_index = i

        consecutive += 1

        # ------------------------------------------
        # Confirmar señal después de N ventanas
        # consecutivas
        # ------------------------------------------

        if (
            consecutive >= MIN_CONSECUTIVE_WINDOWS
            and not episode_active
        ):

            first_row = features.loc[
                episode_start_index
            ]

            trigger_variables = (
                get_trigger_variables(row)
            )

            max_abs_zscore = max(
                abs(row[f"{v}_zscore"])
                for v in trigger_variables
            )

            signal_id = (
                f"CAND-{signal_number:06d}"
            )

            # --------------------------------------
            # Construir explicación automática
            # --------------------------------------

            movements = []

            for variable in trigger_variables:

                z = row[
                    f"{variable}_zscore"
                ]

                if z > 0:
                    direction = "aumento"
                else:
                    direction = "descenso"

                movements.append(
                    f"{variable}: {direction} "
                    f"({z:.2f} z)"
                )

            explanation = (
                "Desviación multivariable persistente "
                "respecto del baseline personal. "
                + "; ".join(movements)
            )

            signals.append(
                {
                    "signal_id": signal_id,
                    "patient_id": PATIENT_ID,

                    # Momento en que el detector
                    # tiene evidencia suficiente
                    "decision_datetime":
                        row["decision_datetime"],

                    # Inicio de la evidencia utilizada
                    "evidence_start":
                        first_row["window_start"],

                    "evidence_end":
                        row["decision_datetime"],

                    "consecutive_windows":
                        consecutive,

                    "variables_triggering":
                        ",".join(
                            trigger_variables
                        ),

                    "variables_over_threshold":
                        row[
                            "variables_over_threshold"
                        ],

                    "max_abs_zscore":
                        max_abs_zscore,

                    "explanation":
                        explanation
                }
            )

            signal_number += 1

            # Evita generar una alerta nueva
            # cada hora durante el mismo episodio
            episode_active = True

    else:

        # Terminó el episodio
        consecutive = 0
        episode_start_index = None
        episode_active = False


# ==================================================
# RESULTADOS
# ==================================================

signals_df = pd.DataFrame(signals)

print(
    "\nCantidad de señales candidatas:",
    len(signals_df)
)

if len(signals_df) > 0:

    print("\n=== SEÑALES CANDIDATAS ===")

    print(
        signals_df.to_string(
            index=False
        )
    )

else:

    print(
        "\nNo se detectaron episodios "
        "multivariables persistentes."
    )


# ==================================================
# MOSTRAR VENTANAS ANOMALAS
# ==================================================

anomalous = features[
    features["is_anomalous_window"]
].copy()

print(
    "\nVentanas anómalas individuales:",
    len(anomalous)
)

if len(anomalous) > 0:

    print(
        anomalous[
            [
                "decision_datetime",
                "variables_over_threshold",
                "HR_zscore",
                "RR_zscore",
                "SpO2_zscore",
                "TEMP_zscore",
                "SBP_zscore",
                "DBP_zscore"
            ]
        ].to_string(index=False)
    )


# ==================================================
# GUARDAR CANDIDATOS
# ==================================================

os.makedirs(
    "data/processed/signals",
    exist_ok=True
)

ruta = (
    f"data/processed/signals/"
    f"{PATIENT_ID}_candidate_signals.parquet"
)

signals_df.to_parquet(
    ruta,
    index=False
)

print("\nCandidatos guardados en:")
print(ruta)

print("\n=== DETECCION TERMINADA ===")