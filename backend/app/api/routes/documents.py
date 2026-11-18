from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.document import DocumentExtractIn, DocumentListOut, DocumentOut
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentListOut)
def list_documents(
    patient_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    items = document_service.list_documents(db, patient_id=patient_id)
    return {"items": items, "total": len(items)}


@router.post("/extract", response_model=DocumentOut, status_code=201)
def extract(body: DocumentExtractIn, db: Session = Depends(get_db)):
    """ELI5: Pretend we scanned a PDF with Azure OCR and pulled out the fields."""
    return document_service.extract_document(
        db,
        filename=body.filename,
        doc_type=body.doc_type,
        patient_id=body.patient_id,
        use_azure=body.use_azure,
        hint=body.hint,
    )


@router.get("/types")
def document_types():
    return {
        "types": [
            {
                "id": "insurance_card",
                "label": "Insurance card",
                "eli5": "Photo of the plastic insurance card → member ID, payer, group #",
            },
            {
                "id": "eob",
                "label": "EOB (Explanation of Benefits)",
                "eli5": "Payer letter saying what they paid / denied on a claim",
            },
            {
                "id": "medical_record",
                "label": "Medical record note",
                "eli5": "Doctor visit note → complaint, diagnosis, plan",
            },
            {
                "id": "cms1500",
                "label": "CMS-1500 claim form",
                "eli5": "Paper claim form with CPT/ICD codes and charges",
            },
        ],
        "note": "MOCK OCR uses templates — Azure DI not required.",
    }
