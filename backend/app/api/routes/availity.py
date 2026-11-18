"""Mock Availity API surface for the RCM POC."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations.eligibility.availity_mock import MockAvailityProvider
from app.schemas.eligibility import EligibilityRequestOut, EligibilityVerifyIn
from app.services import eligibility_service, sync_service

router = APIRouter(prefix="/availity", tags=["availity-mock"])

_DISCLAIMER = (
    "MOCK AVAILITY – Not live Availity. No real payer credentials or X12 traffic."
)


@router.get("/payers")
def list_payers(db: Session = Depends(get_db)):
    """Supported payers + Availity payer IDs (mock directory)."""
    sync_service.ensure_availity_payer_mappings(db)
    data = MockAvailityProvider().list_payers()
    data["disclaimer"] = _DISCLAIMER
    return data


@router.post("/payers/sync-mappings")
def sync_mappings(db: Session = Depends(get_db)):
    """Write Mock Availity payer IDs into PostgreSQL payer_mappings."""
    result = sync_service.ensure_availity_payer_mappings(db)
    result["disclaimer"] = _DISCLAIMER
    return result


@router.post("/eligibility/verify", response_model=EligibilityRequestOut)
def verify(body: EligibilityVerifyIn, db: Session = Depends(get_db)):
    """Submit eligibility via Mock Availity; store request/response/history in Postgres."""
    sync_service.ensure_availity_payer_mappings(db)
    return eligibility_service.verify_eligibility(
        db,
        patient_id=body.patient_id,
        insurance_policy_id=body.insurance_policy_id,
        encounter_id=body.encounter_id,
        service_date=body.service_date,
        scenario=body.scenario,
    )


@router.get("/status")
def status():
    return {
        "provider": "MOCK_AVAILITY",
        "live": False,
        "configured_credentials": False,
        "transactions": ["270", "271"],
        "disclaimer": _DISCLAIMER,
    }
