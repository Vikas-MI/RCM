from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Encounter
from app.schemas.encounter import EncounterListOut, EncounterOut

router = APIRouter(tags=["encounters"])


@router.get("/encounters", response_model=EncounterListOut)
def list_encounters(
    patient_id: UUID | None = None,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Encounter)
    if patient_id:
        stmt = stmt.where(Encounter.patient_id == patient_id)
    if status:
        stmt = stmt.where(Encounter.encounter_status == status)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(
        stmt.order_by(Encounter.start_date.desc().nullslast()).offset(skip).limit(limit)
    ).all()
    return {"items": items, "total": total}


@router.get("/encounters/{encounter_id}", response_model=EncounterOut)
def get_encounter(encounter_id: UUID, db: Session = Depends(get_db)):
    enc = db.get(Encounter, encounter_id)
    if not enc:
        raise HTTPException(404, "Encounter not found")
    return enc


@router.get("/patients/{patient_id}/encounters", response_model=EncounterListOut)
def patient_encounters(patient_id: UUID, db: Session = Depends(get_db)):
    items = db.scalars(
        select(Encounter)
        .where(Encounter.patient_id == patient_id)
        .order_by(Encounter.start_date.desc().nullslast())
    ).all()
    return {"items": items, "total": len(items)}
