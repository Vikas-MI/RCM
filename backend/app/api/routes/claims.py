from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.claim import AppealOut, ClaimListOut, DenialOut
from app.services import claims_service

router = APIRouter(tags=["claims"])


@router.get("/claims", response_model=ClaimListOut)
def list_claims(db: Session = Depends(get_db)):
    items = claims_service.list_claims(db)
    return {"items": items, "total": len(items)}


@router.get("/denials", response_model=list[DenialOut])
def list_denials(db: Session = Depends(get_db)):
    return claims_service.list_denials(db)


@router.post("/denials/{denial_id}/appeal", response_model=AppealOut, status_code=201)
def draft_appeal(denial_id: UUID, db: Session = Depends(get_db)):
    """ELI5: AI drafts a polite letter saying why the denial was wrong, citing policies."""
    return claims_service.create_appeal_from_denial(db, denial_id)


@router.post("/claims/seed")
def seed_claims(db: Session = Depends(get_db)):
    return claims_service.seed_claims_bundle(db)
