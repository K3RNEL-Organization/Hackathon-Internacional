from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from .. import data_quality as dq
from ..models import User, UserRole
from ..schemas import (
    DataQualityIssueOut,
    DataQualityIssuesPageOut,
    DataQualitySummaryOut,
    PlausibilityBreakdownItemOut,
)
from .auth import require_role

router = APIRouter(prefix="/data-quality", tags=["data-quality"])


@router.get("/summary", response_model=DataQualitySummaryOut)
def summary(
    current_user: User = Depends(require_role(UserRole.PROFESIONAL_SALUD.value)),
) -> DataQualitySummaryOut:
    return DataQualitySummaryOut(**dq.build_summary())


@router.get("/plausibility-breakdown", response_model=list[PlausibilityBreakdownItemOut])
def plausibility_breakdown(
    current_user: User = Depends(require_role(UserRole.PROFESIONAL_SALUD.value)),
) -> list[PlausibilityBreakdownItemOut]:
    return [PlausibilityBreakdownItemOut(**item) for item in dq.build_plausibility_breakdown()]


@router.get("/issues", response_model=DataQualityIssuesPageOut)
def issues(
    type: Optional[str] = Query(default=None, description="ALL o uno de los tipos de incidencia"),
    patient_id: Optional[str] = Query(default=None),
    variable: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=15, ge=1, le=200),
    current_user: User = Depends(require_role(UserRole.PROFESIONAL_SALUD.value)),
) -> DataQualityIssuesPageOut:
    df = dq.build_issues_df()

    if type and type.upper() != "ALL":
        requested = type.upper()
        if requested not in dq.ISSUE_TYPES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de incidencia inválido.")
        df = df[df["issue_type"] == requested]

    if patient_id:
        df = df[df["patient_id"].str.upper().str.contains(patient_id.strip().upper(), regex=False)]

    if variable:
        df = df[df["variable_code"].astype(str).str.upper() == variable.strip().upper()]

    if search:
        query = search.strip().upper()
        df = df[
            df["patient_id"].str.upper().str.contains(query, regex=False)
            | df["variable_code"].astype(str).str.upper().str.contains(query, regex=False)
            | df["detected_issue"].str.upper().str.contains(query, regex=False)
        ]

    total = int(len(df))
    start = (page - 1) * page_size
    page_df = df.iloc[start : start + page_size]

    items = [
        DataQualityIssueOut(
            patient_id=row.patient_id,
            issue_type=row.issue_type,
            variable_code=str(row.variable_code),
            value_original=row.value_original,
            value_canonical=row.value_canonical,
            detected_issue=row.detected_issue,
            treatment=row.treatment,
            event_datetime=row.event_datetime,
        )
        for row in page_df.itertuples()
    ]

    return DataQualityIssuesPageOut(items=items, total=total, page=page, page_size=page_size)
