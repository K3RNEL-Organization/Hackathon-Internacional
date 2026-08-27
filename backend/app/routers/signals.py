from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..data import get_evidence_df, get_signals_df
from ..models import User, UserRole
from ..schemas import EvidenceRecordOut, PatientSignalOut, SignalDetailOut
from ..signal_utils import (
    PRIORITY_ORDER,
    parse_activity_note,
    parse_context_note,
    parse_device_quality_pct,
    parse_pattern_summary,
    parse_persistence_windows,
    parse_variable_deviations,
    to_patient_signal_out,
)
from .auth import require_role

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("", response_model=list[PatientSignalOut])
def list_signals(
    priority: Optional[str] = Query(default=None, description="ALL, LOW, MEDIUM, HIGH o CRITICAL"),
    current_user: User = Depends(require_role(UserRole.PROFESIONAL_SALUD.value)),
) -> list[PatientSignalOut]:
    df = get_signals_df()

    if priority and priority.upper() != "ALL":
        requested = priority.upper()
        if requested not in PRIORITY_ORDER:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prioridad inválida.")
        df = df[df["priority_level"] == requested]

    if df.empty:
        return []

    ranked = df.copy()
    ranked["priority_rank"] = ranked["priority_level"].map(PRIORITY_ORDER).fillna(99)
    ranked = ranked.sort_values(
        ["priority_rank", "risk_score", "decision_datetime"],
        ascending=[True, False, False],
    )

    return [to_patient_signal_out(row) for row in ranked.itertuples()]


@router.get("/{signal_id}", response_model=SignalDetailOut)
def get_signal_detail(
    signal_id: str,
    current_user: User = Depends(require_role(UserRole.PROFESIONAL_SALUD.value)),
) -> SignalDetailOut:
    signals_df = get_signals_df()
    match = signals_df[signals_df["signal_id"] == signal_id]

    if match.empty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Señal no encontrada.")

    signal = match.iloc[0]
    decision_datetime = signal["decision_datetime"]

    evidence_df = get_evidence_df()
    signal_evidence = evidence_df[evidence_df["signal_id"] == signal_id]

    # RISA temporal rule: a signal must never present as evidence a data point
    # that was not yet available at the moment the decision was made.
    signal_evidence = signal_evidence[signal_evidence["available_datetime"] <= decision_datetime]
    signal_evidence = signal_evidence.sort_values("event_datetime")

    evidence_out = [
        EvidenceRecordOut(
            source_file=row.source_file,
            variable_code=row.variable_code,
            record_id=row.record_id,
            event_datetime=row.event_datetime,
            available_datetime=row.available_datetime,
            evidence_role=row.evidence_role,
            contribution=float(row.contribution),
        )
        for row in signal_evidence.itertuples()
    ]

    return SignalDetailOut(
        signal_id=signal["signal_id"],
        patient_id=signal["patient_id"],
        priority_level=signal["priority_level"],
        risk_score=round(float(signal["risk_score"]), 2) if pd.notna(signal["risk_score"]) else None,
        confidence_score=(
            round(float(signal["confidence_score"]), 2) if pd.notna(signal["confidence_score"]) else None
        ),
        generated_at=decision_datetime,
        model_version=signal["model_version"],
        explanation=str(signal["explanation"]).strip(),
        evidence_window_start=signal["evidence_start"] if pd.notna(signal["evidence_start"]) else None,
        evidence_window_end=signal["evidence_end"] if pd.notna(signal["evidence_end"]) else None,
        variable_deviations=parse_variable_deviations(signal["explanation"]),
        pattern_summary=parse_pattern_summary(signal["explanation"]),
        persistence_windows=parse_persistence_windows(signal["explanation"]),
        device_quality_pct=parse_device_quality_pct(signal["explanation"]),
        activity_note=parse_activity_note(signal["explanation"]),
        context_note=parse_context_note(signal["explanation"]),
        evidence=evidence_out,
    )
