import re

import pandas as pd

from .schemas import PatientSignalOut, VariableDeviationOut

PRIORITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
DESCRIPTION_LIMIT = 140

_DEVIATION_PATTERN = re.compile(r"([A-Za-z0-9_]+):\s*(aumento|descenso)\s*\(([-+]?\d+(?:\.\d+)?)\s*z\)")


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
        generated_at=row.decision_datetime,
    )
