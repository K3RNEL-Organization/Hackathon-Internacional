import re

import pandas as pd

from .schemas import PatientSignalOut, VariableDeviationOut

PRIORITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
DESCRIPTION_LIMIT = 140

_DEVIATION_PATTERN = re.compile(r"([A-Za-z0-9_]+):\s*(aumento|descenso)\s*\(([-+]?\d+(?:\.\d+)?)\s*z\)")
_PERSISTENCE_PATTERN = re.compile(r"Persistencia observada:\s*(\d+)\s*ventanas")
_QUALITY_PATTERN = re.compile(r"Calidad de dispositivo promedio:\s*(\d+(?:\.\d+)?)")
_ACTIVITY_PATTERN = re.compile(r"([^.]*actividad f[ií]sica[^.]*\.)", re.IGNORECASE)
_CONTEXT_PATTERN = re.compile(r"([^.]*(?:sue[ñn]o|recuperaci[oó]n)[^.]*\.)", re.IGNORECASE)


def parse_variable_deviations(explanation: str) -> list[VariableDeviationOut]:
    """Extracts the per-variable z-score deviations RISA already computed and wrote
    into the explanation text (e.g. "HR: aumento (2.30 z)"). Does not compute anything new."""
    text = str(explanation)
    deviations = []
    for match in _DEVIATION_PATTERN.finditer(text):
        variable_code, direction_word, z_value = match.groups()
        deviations.append(
            VariableDeviationOut(
                variable_code=variable_code,
                direction="INCREASE" if direction_word == "aumento" else "DECREASE",
                z_score=float(z_value),
            )
        )
    return deviations


def parse_pattern_summary(explanation: str) -> str:
    """The first sentence of the explanation is RISA's stated pattern
    (e.g. "Desviacion multivariable persistente respecto del baseline personal.")."""
    text = str(explanation).strip()
    first_period = text.find(". ")
    if first_period == -1:
        return text
    return text[: first_period + 1]


def parse_persistence_windows(explanation: str) -> int | None:
    match = _PERSISTENCE_PATTERN.search(str(explanation))
    return int(match.group(1)) if match else None


def parse_device_quality_pct(explanation: str) -> float | None:
    match = _QUALITY_PATTERN.search(str(explanation))
    return round(float(match.group(1)) * 100, 0) if match else None


def parse_activity_note(explanation: str) -> str | None:
    match = _ACTIVITY_PATTERN.search(str(explanation))
    return match.group(1).strip() if match else None


def parse_context_note(explanation: str) -> str | None:
    match = _CONTEXT_PATTERN.search(str(explanation))
    return match.group(1).strip() if match else None


def short_description(explanation: str) -> str:
    text = str(explanation).strip()
    if len(text) <= DESCRIPTION_LIMIT:
        return text
    truncated = text[:DESCRIPTION_LIMIT].rsplit(" ", 1)[0]
    return f"{truncated}..."


def to_patient_signal_out(row) -> PatientSignalOut:
    return PatientSignalOut(
        patient_id=row.patient_id,
        signal_id=row.signal_id,
        priority_level=row.priority_level,
        risk_score=round(float(row.risk_score), 2) if pd.notna(row.risk_score) else None,
        short_description=short_description(row.explanation),
        pattern_summary=parse_pattern_summary(row.explanation),
        variable_deviations=parse_variable_deviations(row.explanation),
        generated_at=row.decision_datetime,
    )
