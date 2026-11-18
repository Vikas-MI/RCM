from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Payer, PayerMapping
from app.schemas.payer import (
    PayerCreate,
    PayerListOut,
    PayerMappingCreate,
    PayerMappingOut,
    PayerOut,
    PayerUpdate,
)

router = APIRouter(tags=["payers"])


@router.get("/payers", response_model=PayerListOut)
def list_payers(
    q: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Payer)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Payer.payer_name.ilike(like), Payer.payer_code.ilike(like)))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.order_by(Payer.payer_name).offset(skip).limit(limit)).all()
    return {"items": items, "total": total}


@router.post("/payers", response_model=PayerOut, status_code=201)
def create_payer(body: PayerCreate, db: Session = Depends(get_db)):
    payer = Payer(**body.model_dump())
    db.add(payer)
    db.commit()
    db.refresh(payer)
    return payer


@router.get("/payers/{payer_id}", response_model=PayerOut)
def get_payer(payer_id: UUID, db: Session = Depends(get_db)):
    payer = db.get(Payer, payer_id)
    if not payer:
        raise HTTPException(404, "Payer not found")
    return payer


@router.put("/payers/{payer_id}", response_model=PayerOut)
def update_payer(payer_id: UUID, body: PayerUpdate, db: Session = Depends(get_db)):
    payer = db.get(Payer, payer_id)
    if not payer:
        raise HTTPException(404, "Payer not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(payer, k, v)
    db.commit()
    db.refresh(payer)
    return payer


@router.get("/payer-mappings", response_model=list[PayerMappingOut])
def list_mappings(db: Session = Depends(get_db)):
    return db.scalars(select(PayerMapping)).all()


@router.post("/payer-mappings", response_model=PayerMappingOut, status_code=201)
def create_mapping(body: PayerMappingCreate, db: Session = Depends(get_db)):
    if not db.get(Payer, body.internal_payer_id):
        raise HTTPException(400, "Payer not found")
    mapping = PayerMapping(**body.model_dump())
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping
