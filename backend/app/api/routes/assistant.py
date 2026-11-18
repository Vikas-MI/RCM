from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.claim import AssistantAskIn, AssistantAskOut
from app.services.capstone_assistant import ask_capstone

router = APIRouter(prefix="/assistant", tags=["capstone"])


@router.post("/ask", response_model=AssistantAskOut)
def ask(body: AssistantAskIn, db: Session = Depends(get_db)):
    """Capstone: one brain that peeks at patients, eligibility, OCR, claims, and policies."""
    return ask_capstone(db, question=body.question, patient_id=body.patient_id)


@router.get("/roadmap")
def roadmap():
    return {
        "eli5": (
            "Capstone ties the whole story together: patient chart data, scanned paperwork, "
            "coverage rules, bills, denials, and appeals — then answers in one chat. "
            "All practice/synthetic data."
        ),
        "modules": [
            {"id": "fhir", "name": "FHIR sync", "status": "ready"},
            {"id": "eligibility", "name": "Mock eligibility", "status": "ready"},
            {"id": "documents", "name": "Document OCR", "status": "ready"},
            {"id": "policy_rag", "name": "CMS policy RAG", "status": "ready"},
            {"id": "claims", "name": "Claims / denials / appeals", "status": "ready"},
            {"id": "assistant", "name": "Capstone assistant", "status": "ready"},
        ],
        "disclaimer": "All modules use MOCK / synthetic data for learning.",
    }
