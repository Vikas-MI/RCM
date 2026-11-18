from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations.ehr.hapi_adapter import HAPIFHIRAdapter
from app.services import sync_service

router = APIRouter(prefix="/fhir", tags=["fhir"])


@router.get("/patients")
def fhir_patients(name: str | None = None, _count: int = Query(20, ge=1, le=50)):
    adapter = HAPIFHIRAdapter()
    params = {"_count": _count}
    if name:
        params["name"] = name
    return adapter.search_patients(**params)


@router.get("/patients/{external_id}")
def fhir_patient(external_id: str):
    return HAPIFHIRAdapter().get_patient(external_id)


@router.get("/encounters")
def fhir_encounters(patient: str | None = None, _count: int = Query(20, ge=1, le=50)):
    params: dict = {"_count": _count}
    if patient:
        params["patient"] = patient
    return HAPIFHIRAdapter().search_encounters(**params)


@router.get("/coverage")
def fhir_coverage(patient: str | None = None, _count: int = Query(20, ge=1, le=50)):
    params: dict = {"_count": _count}
    if patient:
        params["beneficiary"] = patient
    return HAPIFHIRAdapter().search_coverage(**params)


@router.get("/metadata")
def fhir_metadata():
    return HAPIFHIRAdapter().get_capability_statement()


@router.post("/sync/patients")
def sync_patients(mock_only: bool = True, db: Session = Depends(get_db)):
    """Default mock_only=True so learning works offline with synthetic FHIR."""
    return sync_service.sync_patients(db, use_mock_only=mock_only)


@router.post("/sync/encounters")
def sync_encounters(mock_only: bool = True, db: Session = Depends(get_db)):
    return sync_service.sync_encounters(db, use_mock_only=mock_only)


@router.post("/sync/coverage")
def sync_coverage(mock_only: bool = True, db: Session = Depends(get_db)):
    return sync_service.sync_coverage(db, use_mock_only=mock_only)


@router.post("/sync/all")
def sync_all(
    mock_only: bool = True,
    ehr_source: str = "mock",
    db: Session = Depends(get_db),
):
    result = sync_service.sync_all(db, use_mock_only=mock_only, ehr_source=ehr_source)
    result["availity_mappings"] = sync_service.ensure_availity_payer_mappings(db)
    result["note"] = (
        "Prefer POST /api/ehr/{epic|oracle}/sync/all for POC demos. "
        "MOCK FHIR / Mock Epic / Mock Oracle — not live credentials."
    )
    return result
