"""EHR sync endpoints — Epic / Oracle Health / HAPI (mock when no credentials)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations.ehr.factory import VALID_SOURCES, get_ehr_adapter
from app.services import sync_service

router = APIRouter(prefix="/ehr", tags=["ehr"])

_DISCLAIMER = (
    "Simulated EHR integration for POC. Not live Epic, Oracle Health, or credentialed HAPI."
)


@router.get("/sources")
def list_sources():
    return {
        "sources": [
            {
                "id": "epic",
                "label": "Mock Epic",
                "live": False,
                "note": "Synthetic Epic FHIR — no Epic credentials",
            },
            {
                "id": "oracle",
                "label": "Mock Oracle Health",
                "live": False,
                "note": "Synthetic Oracle/Cerner FHIR — no Oracle credentials",
            },
            {
                "id": "mock",
                "label": "Mock FHIR (generic)",
                "live": False,
                "note": "Built-in synthetic bundles",
            },
            {
                "id": "hapi",
                "label": "HAPI FHIR (public / mock fallback)",
                "live": False,
                "note": "Public test server optional; defaults to mock offline",
            },
        ],
        "disclaimer": _DISCLAIMER,
    }


@router.get("/{source}/metadata")
def metadata(source: str):
    if source not in VALID_SOURCES:
        return {"error": f"Unknown source. Use {VALID_SOURCES}", "disclaimer": _DISCLAIMER}
    return get_ehr_adapter(source).get_capability_statement()


@router.get("/{source}/patients")
def patients(source: str):
    return get_ehr_adapter(source).search_patients()


@router.get("/{source}/encounters")
def encounters(source: str):
    return get_ehr_adapter(source).search_encounters()


@router.get("/{source}/coverage")
def coverage(source: str):
    return get_ehr_adapter(source).search_coverage()


@router.post("/{source}/sync/all")
def sync_all(
    source: str,
    mock_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Pull patient + encounter + insurance from mock EHR into PostgreSQL."""
    if source not in VALID_SOURCES:
        return {"error": f"Unknown source. Use {VALID_SOURCES}", "disclaimer": _DISCLAIMER}
    # Also ensure Availity payer ID mappings exist after coverage sync
    result = sync_service.sync_all(db, use_mock_only=mock_only, ehr_source=source)
    result["availity_mappings"] = sync_service.ensure_availity_payer_mappings(db)
    result["disclaimer"] = _DISCLAIMER
    return result
