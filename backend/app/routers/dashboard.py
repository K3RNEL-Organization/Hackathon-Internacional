from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..data import get_signals_df
from ..models import User, UserRole
from ..schemas import DashboardSummary, PatientSignalOut
from ..signal_utils import PRIORITY_ORDER, to_patient_signal_out
from .auth import require_role

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _top_signal_per_patient(df):
    if df.empty:
        return df
    ranked = df.copy()
    ranked["priority_rank"] = ranked["priority_level"].map(PRIORITY_ORDER).fillna(99)
    ranked = ranked.sort_values(
        ["priority_rank", "risk_score", "decision_datetime"],
        ascending=[True, False, False],
    )
    return ranked.groupby("patient_id", as_index=False).first()


@router.get("/summary", response_model=DashboardSummary)
def summary(current_user: User = Depends(require_role(UserRole.PROFESIONAL_SALUD.value))) -> DashboardSummary:
    df = get_signals_df()
    counts = df["priority_level"].value_counts()

    return DashboardSummary(
        patients_monitored=int(df["patient_id"].nunique()),
        active_signals=int(len(df)),
        priority_critical=int(counts.get("CRITICAL", 0)),
        priority_high=int(counts.get("HIGH", 0)),
        priority_medium=int(counts.get("MEDIUM", 0)),
        priority_low=int(counts.get("LOW", 0)),
        last_updated=df["decision_datetime"].max() if not df.empty else None,
    )


@router.get("/patients", response_model=list[PatientSignalOut])
def patients(
    priority: Optional[str] = Query(default=None, description="ALL, LOW, MEDIUM, HIGH o CRITICAL"),
    current_user: User = Depends(require_role(UserRole.PROFESIONAL_SALUD.value)),
) -> list[PatientSignalOut]:
    df = get_signals_df()
    top = _top_signal_per_patient(df)

    if priority and priority.upper() != "ALL":
        requested = priority.upper()
        if requested not in PRIORITY_ORDER:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prioridad inválida.")
        top = top[top["priority_level"] == requested]

    if top.empty:
        return []

    top = top.sort_values(
        ["priority_rank", "risk_score", "decision_datetime"],
        ascending=[True, False, False],
    )

    return [to_patient_signal_out(row) for row in top.itertuples()]
