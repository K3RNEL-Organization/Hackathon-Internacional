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

_signals_cache: pd.DataFrame | None = None
_evidence_cache: pd.DataFrame | None = None
_conditions_cache: pd.DataFrame | None = None
_encounters_cache: pd.DataFrame | None = None
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


def patient_exists(patient_id: str) -> bool:
    return patient_id in get_conditions_df()["patient_id"].values
