from fastapi import APIRouter, Depends

from .. import data as data_module
from ..models import User, UserRole
from ..schemas import AlertFunnelSummaryOut
from .auth import require_role

router = APIRouter(prefix="/alert-control", tags=["alert-control"])


@router.get("/funnel-summary", response_model=AlertFunnelSummaryOut)
def funnel_summary(
    current_user: User = Depends(require_role(UserRole.PROFESIONAL_SALUD.value)),
) -> AlertFunnelSummaryOut:
    summary = data_module.get_alert_funnel_summary()

    candidates = summary["windows_with_multivariable_deviation"]
    reduction_pct = (
        round((1 - summary["final_signals"] / candidates) * 100, 1) if candidates > 0 else 0.0
    )

    return AlertFunnelSummaryOut(**summary, candidate_reduction_pct=reduction_pct)
