import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status

from ..data import get_conditions_df, get_encounters_df, get_signals_df, patient_exists
from ..models import User, UserRole
from ..schemas import (
    ConditionOut,
    EncounterOut,
    PatientDetailOut,
    TimelineEventOut,
    TimelineEventType,
)
from ..signal_utils import to_patient_signal_out
from .auth import require_role

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/{patient_id}", response_model=PatientDetailOut)
def get_patient_detail(
    patient_id: str,
    current_user: User = Depends(require_role(UserRole.PROFESIONAL_SALUD.value)),
) -> PatientDetailOut:
    if not patient_exists(patient_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")

    signals_df = get_signals_df()
    patient_signals = signals_df[signals_df["patient_id"] == patient_id].sort_values(
        "decision_datetime", ascending=False
    )

    conditions_df = get_conditions_df()
    patient_conditions = conditions_df[conditions_df["patient_id"] == patient_id].sort_values(
        "recorded_datetime", ascending=False
    )

    encounters_df = get_encounters_df()
    patient_encounters = encounters_df[encounters_df["patient_id"] == patient_id].sort_values(
        "start_datetime_enc", ascending=False
    )

    signals_out = [to_patient_signal_out(row) for row in patient_signals.itertuples()]

    latest_encounter = None
    if not patient_encounters.empty:
        top = patient_encounters.iloc[0]
        latest_encounter = EncounterOut(
            encounter_id=top["encounter_id"],
            start=top["start_datetime_enc"],
            end=top["end_datetime_enc"] if pd.notna(top["end_datetime_enc"]) else None,
        )

    conditions_out = [
        ConditionOut(
            category=row.condition_category,
            status=row.status,
            onset_date=row.onset_date if pd.notna(row.onset_date) else None,
            recorded_at=row.recorded_datetime,
        )
        for row in patient_conditions.itertuples()
    ]

    timeline: list[TimelineEventOut] = []

    for row in patient_signals.itertuples():
        timeline.append(
            TimelineEventOut(
                type=TimelineEventType.SIGNAL_DETECTED,
                label=f"Señal detectada ({row.priority_level})",
                timestamp=row.decision_datetime,
                priority_level=row.priority_level,
            )
        )

    for row in patient_encounters.itertuples():
        timeline.append(
            TimelineEventOut(
                type=TimelineEventType.ENCOUNTER_START,
                label=f"Inicio del episodio de monitoreo {row.encounter_id}",
                timestamp=row.start_datetime_enc,
            )
        )
        if pd.notna(row.end_datetime_enc):
            timeline.append(
                TimelineEventOut(
                    type=TimelineEventType.ENCOUNTER_END,
                    label=f"Fin del episodio de monitoreo {row.encounter_id}",
                    timestamp=row.end_datetime_enc,
                )
            )

    for row in patient_conditions.itertuples():
        timeline.append(
            TimelineEventOut(
                type=TimelineEventType.CONDITION_RECORDED,
                label=f"Antecedente registrado: {row.condition_category}",
                timestamp=row.recorded_datetime,
            )
        )

    timeline.sort(key=lambda event: event.timestamp, reverse=True)

    current_priority = None
    current_risk_score = None
    last_signal_id = None
    last_signal_at = None
    if not patient_signals.empty:
        latest_signal = patient_signals.iloc[0]
        current_priority = latest_signal["priority_level"]
        current_risk_score = (
            round(float(latest_signal["risk_score"]), 2) if pd.notna(latest_signal["risk_score"]) else None
        )
        last_signal_id = latest_signal["signal_id"]
        last_signal_at = latest_signal["decision_datetime"]

    candidate_dates = [event.timestamp for event in timeline]
    last_updated = max(candidate_dates) if candidate_dates else None

    return PatientDetailOut(
        patient_id=patient_id,
        current_priority=current_priority,
        current_risk_score=current_risk_score,
        last_signal_id=last_signal_id,
        last_signal_at=last_signal_at,
        last_updated=last_updated,
        encounter=latest_encounter,
        conditions=conditions_out,
        signals=signals_out,
        timeline=timeline,
    )
