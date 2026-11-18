from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.integrations.eligibility.mock_provider import MOCK_SCENARIOS
from app.models import EligibilityHistory, EligibilityRequest
from app.schemas.eligibility import (
    EligibilityHistoryOut,
    EligibilityListOut,
    EligibilityRequestOut,
    EligibilityVerifyIn,
    ScenarioListOut,
)
from app.services.eligibility_service import retry_eligibility, verify_eligibility

router = APIRouter(tags=["eligibility"])

DISCLAIMER = "MOCK DATA – NOT REAL INSURANCE VERIFICATION"


@router.get("/eligibility/mock-scenarios", response_model=ScenarioListOut)
def mock_scenarios():
    return {"scenarios": MOCK_SCENARIOS, "disclaimer": DISCLAIMER}


@router.post("/eligibility/verify", response_model=EligibilityRequestOut)
def verify(body: EligibilityVerifyIn, db: Session = Depends(get_db)):
    req = verify_eligibility(
        db,
        patient_id=body.patient_id,
        insurance_policy_id=body.insurance_policy_id,
        encounter_id=body.encounter_id,
        service_date=body.service_date,
        scenario=body.scenario,
    )
    return req


@router.get("/eligibility", response_model=EligibilityListOut)
def list_eligibility(
    patient_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(EligibilityRequest).options(joinedload(EligibilityRequest.response))
    if patient_id:
        stmt = stmt.where(EligibilityRequest.patient_id == patient_id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(
        stmt.order_by(EligibilityRequest.requested_at.desc()).offset(skip).limit(limit)
    ).unique().all()
    return {"items": items, "total": total}


@router.get("/eligibility/{request_id}", response_model=EligibilityRequestOut)
def get_eligibility(request_id: UUID, db: Session = Depends(get_db)):
    req = db.scalar(
        select(EligibilityRequest)
        .options(joinedload(EligibilityRequest.response))
        .where(EligibilityRequest.id == request_id)
    )
    if not req:
        raise HTTPException(404, "Eligibility request not found")
    return req


@router.post("/eligibility/{request_id}/retry", response_model=EligibilityRequestOut)
def retry(request_id: UUID, db: Session = Depends(get_db)):
    return retry_eligibility(db, request_id)


@router.get(
    "/patients/{patient_id}/eligibility-history",
    response_model=list[EligibilityHistoryOut],
)
def patient_history(patient_id: UUID, db: Session = Depends(get_db)):
    return db.scalars(
        select(EligibilityHistory)
        .where(EligibilityHistory.patient_id == patient_id)
        .order_by(EligibilityHistory.created_at.desc())
    ).all()


@router.get("/eligibility-history", response_model=list[EligibilityHistoryOut])
def history(
    patient_id: UUID | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(EligibilityHistory)
    if patient_id:
        stmt = stmt.where(EligibilityHistory.patient_id == patient_id)
    if status:
        stmt = stmt.where(EligibilityHistory.current_status == status)
    return db.scalars(stmt.order_by(EligibilityHistory.created_at.desc())).all()
