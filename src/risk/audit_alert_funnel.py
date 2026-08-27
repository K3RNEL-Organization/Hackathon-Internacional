"""Read-only audit of the alert funnel already implemented in run_pipeline_v03.py.

This script does NOT change the detection algorithm, thresholds, risk_score,
or priorities. It reproduces the exact same windowing / z-score / persistence
logic (same constants, same functions) purely to COUNT how many windows pass
each stage of the existing pipeline, and writes those counts to a small JSON
artifact for the "Control de alertas" dashboard section.

As a correctness check, the script asserts that the number of confirmed
episodes it counts matches the number of rows in results/signals.csv exactly.
If it doesn't, the script fails loudly instead of writing a wrong summary.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"

VITALS_PATH = PROCESSED_DIR / "vital_signs_final.parquet"
PATIENTS_PATH = RAW_DIR / "patients.csv"
SIGNALS_PATH = RESULTS_DIR / "signals.csv"

OUTPUT_PATH = PROCESSED_DIR / "alert_funnel_summary.json"

# Same MVP decisions as run_pipeline_v03.py. NOT clinical thresholds.
BASELINE_HOURS = 24
WINDOW_HOURS = 4
STEP_HOURS = 1

Z_THRESHOLD = 2.0
MIN_VARIABLES = 2
MIN_CONSECUTIVE_WINDOWS = 2
MIN_BASELINE_COUNT = 3

VARIABLES = ["HR", "RR", "SpO2", "TEMP", "SBP", "DBP"]


def calculate_baseline(patient_vitals, patient_start):
    baseline_end = patient_start + pd.Timedelta(hours=BASELINE_HOURS)
    baseline_data = patient_vitals[
        (patient_vitals["timestamp"] >= patient_start)
        & (patient_vitals["timestamp"] < baseline_end)
        & (patient_vitals["quality_flag"] == "OK")
        & (~patient_vitals["is_plausibility_issue"])
    ]

    baseline = {}
    for variable in VARIABLES:
        values = baseline_data[baseline_data["variable_code"] == variable]["value_numeric"].dropna()
        if len(values) < MIN_BASELINE_COUNT:
            continue
        std = values.std()
        if pd.isna(std) or std <= 0:
            continue
        baseline[variable] = {"median": values.median(), "std": std}

    return baseline, baseline_end


def prepare_variable_arrays(patient_vitals):
    arrays = {}
    valid = patient_vitals[
        (patient_vitals["quality_flag"] == "OK") & (~patient_vitals["is_plausibility_issue"])
    ]
    for variable in VARIABLES:
        subset = valid[valid["variable_code"] == variable].sort_values("timestamp")
        subset = subset.dropna(subset=["value_numeric"])
        if subset.empty:
            continue
        times = subset["timestamp"].to_numpy(dtype="datetime64[ns]")
        values = subset["value_numeric"].astype(float).to_numpy()
        arrays[variable] = (times, values)
    return arrays


def calculate_window_zscores(decision_time, baseline, variable_arrays):
    window_start = decision_time - pd.Timedelta(hours=WINDOW_HOURS)
    decision_np = np.datetime64(decision_time.to_datetime64(), "ns")
    start_np = np.datetime64(window_start.to_datetime64(), "ns")

    zscores = {}
    for variable in VARIABLES:
        if variable not in baseline or variable not in variable_arrays:
            zscores[variable] = np.nan
            continue
        times, values = variable_arrays[variable]
        left = np.searchsorted(times, start_np, side="right")
        right = np.searchsorted(times, decision_np, side="right")
        if right <= left:
            zscores[variable] = np.nan
            continue
        window_values = values[left:right]
        if len(window_values) == 0:
            zscores[variable] = np.nan
            continue
        window_mean = np.nanmean(window_values)
        zscores[variable] = (window_mean - baseline[variable]["median"]) / baseline[variable]["std"]

    return zscores


def main() -> None:
    print("Cargando pacientes...")
    patients = pd.read_csv(PATIENTS_PATH, usecols=["patient_id"])
    patient_ids = patients["patient_id"].dropna().drop_duplicates().tolist()

    print("Cargando vital_signs_final.parquet...")
    vitals = pd.read_parquet(
        VITALS_PATH,
        columns=[
            "patient_id",
            "timestamp",
            "variable_code",
            "value_canonical",
            "quality_flag",
            "is_plausibility_issue",
            "is_retransmission",
        ],
    )
    vitals["timestamp"] = pd.to_datetime(vitals["timestamp"])
    vitals["value_numeric"] = pd.to_numeric(vitals["value_canonical"], errors="coerce")
    vitals["is_plausibility_issue"] = vitals["is_plausibility_issue"].fillna(False).astype(bool)
    vitals["is_retransmission"] = vitals["is_retransmission"].fillna(False).astype(bool)

    retransmissions_excluded = int(vitals["is_retransmission"].sum())

    # Retransmissions do not count as new physiological events (same rule as run_pipeline_v03.py).
    vitals = vitals[~vitals["is_retransmission"]]
    vitals = vitals[vitals["variable_code"].isin(VARIABLES)]
    vitals = vitals.sort_values(["patient_id", "timestamp"])

    vital_groups = vitals.groupby("patient_id", sort=False)

    total_windows = 0
    windows_ge1_variable = 0
    windows_ge2_variables = 0
    persistence_confirmed = 0

    processed_patients = 0

    print("Procesando pacientes...")
    for patient_index, patient_id in enumerate(patient_ids, start=1):
        try:
            patient_vitals = vital_groups.get_group(patient_id)
        except KeyError:
            continue

        if patient_vitals.empty:
            continue

        patient_start = patient_vitals["timestamp"].min()
        baseline, baseline_end = calculate_baseline(patient_vitals, patient_start)

        if len(baseline) < MIN_VARIABLES:
            continue

        variable_arrays = prepare_variable_arrays(patient_vitals)

        valid_for_end = patient_vitals[
            (patient_vitals["quality_flag"] == "OK") & (~patient_vitals["is_plausibility_issue"])
        ]
        if valid_for_end.empty:
            continue

        analysis_end = valid_for_end["timestamp"].max()
        if analysis_end < baseline_end:
            continue

        decision_times = pd.date_range(start=baseline_end, end=analysis_end, freq=f"{STEP_HOURS}h")

        consecutive = 0
        episode_active = False

        for decision_time in decision_times:
            total_windows += 1

            zscores = calculate_window_zscores(decision_time, baseline, variable_arrays)
            trigger_variables = [
                variable for variable, zscore in zscores.items() if pd.notna(zscore) and abs(zscore) >= Z_THRESHOLD
            ]
            variables_over_threshold = len(trigger_variables)

            if variables_over_threshold >= 1:
                windows_ge1_variable += 1
            if variables_over_threshold >= MIN_VARIABLES:
                windows_ge2_variables += 1

            anomalous = variables_over_threshold >= MIN_VARIABLES

            if anomalous:
                consecutive += 1
                if consecutive >= MIN_CONSECUTIVE_WINDOWS and not episode_active:
                    persistence_confirmed += 1
                    episode_active = True
            else:
                consecutive = 0
                episode_active = False

        processed_patients += 1

        if patient_index % 100 == 0:
            print(f"[{patient_index}/{len(patient_ids)}] procesados")

    final_signals = int(pd.read_csv(SIGNALS_PATH).shape[0])

    print("\n=== RESULTADOS ===")
    print("Pacientes procesados:", processed_patients)
    print("Ventanas evaluadas:", total_windows)
    print("Ventanas con >=1 variable desviada:", windows_ge1_variable)
    print("Ventanas con >=2 variables desviadas:", windows_ge2_variables)
    print("Casos que cumplen persistencia (episodios confirmados):", persistence_confirmed)
    print("Señales finales (results/signals.csv):", final_signals)
    print("Retransmisiones excluidas:", retransmissions_excluded)

    # In this pipeline, a confirmed episode immediately becomes exactly one
    # final signal row (no separate merging step exists beyond persistence
    # itself), so these two counts must match exactly.
    assert persistence_confirmed == final_signals, (
        f"Inconsistencia: episodios confirmados ({persistence_confirmed}) "
        f"!= señales finales ({final_signals}). No se escribe el resumen."
    )

    summary = {
        "windows_evaluated": total_windows,
        "windows_with_deviation": windows_ge1_variable,
        "windows_with_multivariable_deviation": windows_ge2_variables,
        "persistence_confirmed_cases": persistence_confirmed,
        "consolidated_episodes": persistence_confirmed,
        "final_signals": final_signals,
        "retransmissions_excluded": retransmissions_excluded,
    }

    OUTPUT_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nResumen guardado en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
