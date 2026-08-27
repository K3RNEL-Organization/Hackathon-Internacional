from pathlib import Path
from threading import Lock

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SIGNALS_PATH = REPO_ROOT / "results" / "signals.csv"
EVIDENCE_PATH = REPO_ROOT / "results" / "evidence.csv"
CONDITIONS_PATH = REPO_ROOT / "K3RNEL" / "healthsignal" / "data" / "processed" / "conditions.parquet"
MEDICATION_ADMINISTRATIONS_PATH = (
    REPO_ROOT / "K3RNEL" / "healthsignal" / "data" / "processed" / "medication_administrations.parquet"
)
VITAL_SIGNS_FINAL_PATH = REPO_ROOT / "data" / "processed" / "vital_signs_final.parquet"
LABORATORY_RESULTS_PATH = REPO_ROOT / "data" / "raw" / "laboratory_results.csv"

_signals_cache: pd.DataFrame | None = None
_evidence_cache: pd.DataFrame | None = None
_conditions_cache: pd.DataFrame | None = None
_encounters_cache: pd.DataFrame | None = None
_medication_administrations_cache: pd.DataFrame | None = None
_vital_signs_quality_cache: pd.DataFrame | None = None
_lab_results_cache: pd.DataFrame | None = None
_lock = Lock()


def get_signals_df() -> pd.DataFrame:
    global _signals_cache
    with _lock:
        if _signals_cache is None:
            _signals_cache = pd.read_csv(
                SIGNALS_PATH, parse_dates=["decision_datetime", "evidence_start", "evidence_end"]
            )
        return _signals_cache.copy()


def get_evidence_df() -> pd.DataFrame:
    global _evidence_cache
    with _lock:
        if _evidence_cache is None:
            _evidence_cache = pd.read_csv(
                EVIDENCE_PATH, parse_dates=["event_datetime", "available_datetime"]
            )
        return _evidence_cache.copy()


def get_conditions_df() -> pd.DataFrame:
    global _conditions_cache
    with _lock:
        if _conditions_cache is None:
            df = pd.read_parquet(CONDITIONS_PATH)
            df["onset_date"] = pd.to_datetime(df["onset_date"])
            df["recorded_datetime"] = pd.to_datetime(df["recorded_datetime"])
            _conditions_cache = df
        return _conditions_cache.copy()


def get_encounters_df() -> pd.DataFrame:
    """One row per distinct encounter, derived from medication administration records."""
    global _encounters_cache
    with _lock:
        if _encounters_cache is None:
            df = pd.read_parquet(MEDICATION_ADMINISTRATIONS_PATH)
            df["start_datetime_enc"] = pd.to_datetime(df["start_datetime_enc"])
            df["end_datetime_enc"] = pd.to_datetime(df["end_datetime_enc"])
            _encounters_cache = (
                df[["patient_id", "encounter_id", "start_datetime_enc", "end_datetime_enc"]]
                .drop_duplicates()
                .reset_index(drop=True)
            )
        return _encounters_cache.copy()


def get_medication_administrations_df() -> pd.DataFrame:
    """Raw medication administration records, including the encounter_boundary_issue
    flag produced during RISA's validation stage."""
    global _medication_administrations_cache
    with _lock:
        if _medication_administrations_cache is None:
            df = pd.read_parquet(MEDICATION_ADMINISTRATIONS_PATH)
            for column in ["start_datetime_med", "end_datetime_med", "start_datetime_enc", "end_datetime_enc"]:
                df[column] = pd.to_datetime(df[column])
            _medication_administrations_cache = df
        return _medication_administrations_cache.copy()


def get_vital_signs_quality_df() -> pd.DataFrame:
    """Subset of vital_signs_final.parquet limited to rows RISA flagged during
    validation/normalization: plausibility issues, retransmissions and unit
    conversions. The full vital_signs table has ~1.6M rows, so only the flagged
    subset (~1.5k rows) is cached to keep this cheap to query."""
    global _vital_signs_quality_cache
    with _lock:
        if _vital_signs_quality_cache is None:
            df = pd.read_parquet(VITAL_SIGNS_FINAL_PATH)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            mask = df["is_plausibility_issue"] | df["is_retransmission"] | df["unit_was_converted"]
            _vital_signs_quality_cache = df[mask].reset_index(drop=True)
        return _vital_signs_quality_cache.copy()


def get_lab_results_df() -> pd.DataFrame:
    """Laboratory results with an out_of_reference flag computed from the
    reference_low/reference_high bounds already present in the raw data.
    Being out of reference is NOT treated as a risk signal here."""
    global _lab_results_cache
    with _lock:
        if _lab_results_cache is None:
            df = pd.read_csv(LABORATORY_RESULTS_PATH, parse_dates=["sample_datetime", "result_datetime"])
            df["out_of_reference"] = (df["result_value"] < df["reference_low"]) | (
                df["result_value"] > df["reference_high"]
            )
            _lab_results_cache = df
        return _lab_results_cache.copy()


def patient_exists(patient_id: str) -> bool:
    return patient_id in get_conditions_df()["patient_id"].values
