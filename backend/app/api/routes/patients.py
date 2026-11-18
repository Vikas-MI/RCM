from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Patient
from app.schemas.patient import PatientCreate, PatientListOut, PatientOut, PatientUpdate

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=PatientListOut)
def list_patients(
    q: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Patient)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                Patient.first_name.ilike(like),
                Patient.last_name.ilike(like),
                Patient.external_ehr_patient_id.ilike(like),
            )
        )
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.order_by(Patient.last_name).offset(skip).limit(limit)).all()
    return {"items": items, "total": total}


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: UUID, db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    return patient


@router.post("", response_model=PatientOut, status_code=201)
def create_patient(body: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**body.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: UUID, body: PatientUpdate, db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(patient, k, v)
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: UUID, db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    db.delete(patient)
    db.commit()
