import pandas as pd

PATIENT_ID = "PAT-0001"

print(f"\n=== INSPECCION DE FEATURES DE {PATIENT_ID} ===")

# ==================================================
# CARGAR FEATURES
# ==================================================

features = pd.read_parquet(
    f"data/processed/features/"
    f"{PATIENT_ID}_features.parquet"
)

variables = [
    "HR",
    "RR",
    "SpO2",
    "TEMP",
    "SBP",
    "DBP"
]

# ==================================================
# DESVIACION ABSOLUTA
# ==================================================

zscore_columns = []

for variable in variables:

    columna = f"{variable}_zscore"

    features[
        f"{variable}_abs_zscore"
    ] = features[columna].abs()

    zscore_columns.append(
        f"{variable}_abs_zscore"
    )

# Mayor desviación de cualquier variable
features["max_abs_zscore"] = features[
    zscore_columns
].max(axis=1)

# Qué variable produjo la mayor desviación
features["most_deviated_variable"] = features[
    zscore_columns
].idxmax(axis=1)

features["most_deviated_variable"] = (
    features["most_deviated_variable"]
    .str.replace("_abs_zscore", "")
)

# Cantidad de variables con |z| >= 2
features["variables_over_2z"] = (
    features[zscore_columns] >= 2
).sum(axis=1)


# ==================================================
# ORDENAR VENTANAS MÁS DIFERENTES
# ==================================================

top = features.sort_values(
    "max_abs_zscore",
    ascending=False
).head(20)


columnas = [
    "decision_datetime",
    "most_deviated_variable",
    "max_abs_zscore",
    "variables_over_2z",

    "HR_zscore",
    "RR_zscore",
    "SpO2_zscore",
    "TEMP_zscore",
    "SBP_zscore",
    "DBP_zscore"
]

print("\n20 ventanas con mayor desviación:")

print(
    top[columnas].to_string(
        index=False
    )
)


# ==================================================
# RESUMEN GENERAL
# ==================================================

print("\nMáximo |z-score| por variable:")

for variable in variables:

    valor = features[
        f"{variable}_abs_zscore"
    ].max()

    print(
        f"{variable}: {valor:.2f}"
    )


print("\nVentanas con varias variables desviadas:")

print(
    features[
        "variables_over_2z"
    ].value_counts().sort_index()
)


print("\n=== INSPECCION TERMINADA ===")