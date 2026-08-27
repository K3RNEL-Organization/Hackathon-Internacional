"""Read-only aggregation of the data-quality flags RISA already produces during
validation/normalization (vital_signs_final.parquet, conditions.parquet,
medication_administrations.parquet, laboratory_results.csv).

This module does not detect anything new, does not touch risk_score/priority,
and never reads signals.csv or evidence.csv: those remain the sole source of
truth for risk signals. It only reshapes existing quality flags for display.
"""

import pandas as pd

from . import data as data_module

ISSUE_TYPES = [
    "PLAUSIBILITY",
    "RETRANSMISSION",
    "UNIT_NORMALIZED",
    "TEMPORAL",
    "ENCOUNTER_BOUNDARY",
    "LAB_REFERENCE",
]

TREATMENT_LABEL = {
    "PLAUSIBILITY": "Marcado, no eliminado",
    "RETRANSMISSION": "Excluido del doble conteo fisiológico",
    "UNIT_NORMALIZED": "Convertido a unidad canónica",
    "TEMPORAL": "Conservado y marcado",
    "ENCOUNTER_BOUNDARY": "Conservado y marcado",
    "LAB_REFERENCE": "Revisable, no es señal de riesgo automática",
}

_ISSUE_COLUMNS = [
    "patient_id",
    "issue_type",
    "variable_code",
    "value_original",
    "value_canonical",
    "detected_issue",
    "treatment",
    "event_datetime",
]


def _empty_issues() -> pd.DataFrame:
    return pd.DataFrame(columns=_ISSUE_COLUMNS)


def _plausibility_rows(vitals: pd.DataFrame) -> pd.DataFrame:
    rows = vitals[vitals["is_plausibility_issue"]]
    if rows.empty:
        return _empty_issues()
    return pd.DataFrame(
        {
            "patient_id": rows["patient_id"],
            "issue_type": "PLAUSIBILITY",
            "variable_code": rows["variable_code"],
            "value_original": rows["value_original"].round(2).astype(str),
            "value_canonical": rows["value_canonical"].round(2).astype(str),
            "detected_issue": "Valor fuera del rango de plausibilidad fisiológica",
            "treatment": TREATMENT_LABEL["PLAUSIBILITY"],
            "event_datetime": rows["timestamp"],
        }
    )


def _retransmission_rows(vitals: pd.DataFrame) -> pd.DataFrame:
    rows = vitals[vitals["is_retransmission"]]
    if rows.empty:
        return _empty_issues()
    return pd.DataFrame(
        {
            "patient_id": rows["patient_id"],
            "issue_type": "RETRANSMISSION",
            "variable_code": rows["variable_code"],
            "value_original": rows["value_original"].round(2).astype(str),
            "value_canonical": rows["value_canonical"].round(2).astype(str),
            "detected_issue": "Retransmisión de monitor detectada (" + rows["quality_flag"].astype(str) + ")",
            "treatment": TREATMENT_LABEL["RETRANSMISSION"],
            "event_datetime": rows["timestamp"],
        }
    )


def _unit_normalized_rows(vitals: pd.DataFrame) -> pd.DataFrame:
    rows = vitals[vitals["unit_was_converted"]]
    if rows.empty:
        return _empty_issues()
    return pd.DataFrame(
        {
            "patient_id": rows["patient_id"],
            "issue_type": "UNIT_NORMALIZED",
            "variable_code": rows["variable_code"],
            "value_original": rows["value_original"].round(2).astype(str) + " " + rows["unit_original"].astype(str),
            "value_canonical": rows["value_canonical"].round(2).astype(str)
            + " "
            + rows["unit_canonical"].astype(str),
            "detected_issue": "Unidad distinta a la unidad canónica",
            "treatment": TREATMENT_LABEL["UNIT_NORMALIZED"],
            "event_datetime": rows["timestamp"],
        }
    )


def _temporal_rows(conditions: pd.DataFrame) -> pd.DataFrame:
    rows = conditions[conditions["temporal_issue"]]
    if rows.empty:
        return _empty_issues()
    return pd.DataFrame(
        {
            "patient_id": rows["patient_id"],
            "issue_type": "TEMPORAL",
            "variable_code": rows["condition_category"],
            "value_original": rows["recorded_datetime"].astype(str),
            "value_canonical": rows["onset_date"].astype(str),
            "detected_issue": "Fecha de registro anterior a la fecha de inicio de la condición",
            "treatment": TREATMENT_LABEL["TEMPORAL"],
            "event_datetime": rows["recorded_datetime"],
        }
    )


def _encounter_boundary_rows(medications: pd.DataFrame) -> pd.DataFrame:
    rows = medications[medications["encounter_boundary_issue"]]
    if rows.empty:
        return _empty_issues()
    return pd.DataFrame(
        {
            "patient_id": rows["patient_id"],
            "issue_type": "ENCOUNTER_BOUNDARY",
            "variable_code": rows["medication_id"],
            "value_original": rows["end_datetime_med"].astype(str),
            "value_canonical": rows["end_datetime_enc"].astype(str),
            "detected_issue": "La administración finaliza después del límite del encounter",
            "treatment": TREATMENT_LABEL["ENCOUNTER_BOUNDARY"],
            "event_datetime": rows["start_datetime_med"],
        }
    )


def _lab_reference_rows(labs: pd.DataFrame) -> pd.DataFrame:
    rows = labs[labs["out_of_reference"]]
    if rows.empty:
        return _empty_issues()
    return pd.DataFrame(
        {
            "patient_id": rows["patient_id"],
            "issue_type": "LAB_REFERENCE",
            "variable_code": rows["test_code"],
            "value_original": rows["result_value"].astype(str) + " " + rows["unit"].astype(str),
            "value_canonical": "Referencia " + rows["reference_low"].astype(str) + "-" + rows["reference_high"].astype(str),
            "detected_issue": "Resultado fuera del rango de referencia",
            "treatment": TREATMENT_LABEL["LAB_REFERENCE"],
            "event_datetime": rows["result_datetime"],
        }
    )


def build_summary() -> dict:
    vitals = data_module.get_vital_signs_quality_df()
    conditions = data_module.get_conditions_df()
    medications = data_module.get_medication_administrations_df()
    labs = data_module.get_lab_results_df()

    return {
        "plausibility_issues": int(vitals["is_plausibility_issue"].sum()),
        "retransmissions": int(vitals["is_retransmission"].sum()),
        "normalized_units": int(vitals["unit_was_converted"].sum()),
        "temporal_issues": int(conditions["temporal_issue"].sum()),
        "encounter_boundary_issues": int(medications["encounter_boundary_issue"].sum()),
        "lab_out_of_reference": int(labs["out_of_reference"].sum()),
    }


def build_plausibility_breakdown() -> list[dict]:
    vitals = data_module.get_vital_signs_quality_df()
    counts = vitals[vitals["is_plausibility_issue"]]["variable_code"].value_counts()
    return [{"variable_code": str(code), "count": int(count)} for code, count in counts.items()]


def build_issues_df() -> pd.DataFrame:
    vitals = data_module.get_vital_signs_quality_df()
    conditions = data_module.get_conditions_df()
    medications = data_module.get_medication_administrations_df()
    labs = data_module.get_lab_results_df()

    combined = pd.concat(
        [
            _plausibility_rows(vitals),
            _retransmission_rows(vitals),
            _unit_normalized_rows(vitals),
            _temporal_rows(conditions),
            _encounter_boundary_rows(medications),
            _lab_reference_rows(labs),
        ],
        ignore_index=True,
    )
    combined["event_datetime"] = pd.to_datetime(combined["event_datetime"])
    return combined.sort_values("event_datetime", ascending=False).reset_index(drop=True)
