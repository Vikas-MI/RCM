from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models import InsurancePolicy, Payer
from app.schemas.insurance import (
    InsuranceCreate,
    InsuranceListOut,
    InsuranceOut,
    InsuranceUpdate,
)

router = APIRouter(tags=["insurance"])


def _to_out(policy: InsurancePolicy) -> dict:
    data = InsuranceOut.model_validate(policy).model_dump()
    data["payer_name"] = policy.payer.payer_name if policy.payer else None
    return data


@router.get("/insurance", response_model=InsuranceListOut)
def list_insurance(
    patient_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(InsurancePolicy).options(joinedload(InsurancePolicy.payer))
    if patient_id:
        stmt = stmt.where(InsurancePolicy.patient_id == patient_id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.offset(skip).limit(limit)).unique().all()
    return {"items": [_to_out(i) for i in items], "total": total}


@router.post("/insurance", response_model=InsuranceOut, status_code=201)
def create_insurance(body: InsuranceCreate, db: Session = Depends(get_db)):
    if not db.get(Payer, body.payer_id):
        raise HTTPException(400, "Payer not found")
    policy = InsurancePolicy(**body.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    policy = db.scalar(
        select(InsurancePolicy)
        .options(joinedload(InsurancePolicy.payer))
        .where(InsurancePolicy.id == policy.id)
    )
    return _to_out(policy)


@router.get("/insurance/{policy_id}", response_model=InsuranceOut)
def get_insurance(policy_id: UUID, db: Session = Depends(get_db)):
    policy = db.scalar(
        select(InsurancePolicy)
        .options(joinedload(InsurancePolicy.payer))
        .where(InsurancePolicy.id == policy_id)
    )
    if not policy:
        raise HTTPException(404, "Insurance policy not found")
    return _to_out(policy)


@router.put("/insurance/{policy_id}", response_model=InsuranceOut)
def update_insurance(
    policy_id: UUID, body: InsuranceUpdate, db: Session = Depends(get_db)
):
    policy = db.get(InsurancePolicy, policy_id)
    if not policy:
        raise HTTPException(404, "Insurance policy not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(policy, k, v)
    db.commit()
    policy = db.scalar(
        select(InsurancePolicy)
        .options(joinedload(InsurancePolicy.payer))
        .where(InsurancePolicy.id == policy_id)
    )
    return _to_out(policy)


@router.delete("/insurance/{policy_id}", status_code=204)
def delete_insurance(policy_id: UUID, db: Session = Depends(get_db)):
    policy = db.get(InsurancePolicy, policy_id)
    if not policy:
        raise HTTPException(404, "Insurance policy not found")
    db.delete(policy)
    db.commit()


@router.get("/patients/{patient_id}/insurance", response_model=InsuranceListOut)
def patient_insurance(patient_id: UUID, db: Session = Depends(get_db)):
    items = db.scalars(
        select(InsurancePolicy)
        .options(joinedload(InsurancePolicy.payer))
        .where(InsurancePolicy.patient_id == patient_id)
    ).unique().all()
    return {"items": [_to_out(i) for i in items], "total": len(items)}
