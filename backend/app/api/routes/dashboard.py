from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import (
    Appeal,
    Claim,
    Denial,
    EligibilityRequest,
    Encounter,
    HealthcareDocument,
    InsurancePolicy,
    Patient,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    def count(model):
        return db.scalar(select(func.count()).select_from(model)) or 0

    status_rows = db.execute(
        select(EligibilityRequest.request_status, func.count()).group_by(
            EligibilityRequest.request_status
        )
    ).all()
    by_status = {row[0]: row[1] for row in status_rows}

    recent = db.scalars(
        select(EligibilityRequest)
        .order_by(EligibilityRequest.requested_at.desc())
        .limit(8)
    ).all()

    return {
        "patients": count(Patient),
        "encounters": count(Encounter),
        "insurance_policies": count(InsurancePolicy),
        "eligibility_verifications": count(EligibilityRequest),
        "documents": count(HealthcareDocument),
        "claims": count(Claim),
        "denials": count(Denial),
        "appeals": count(Appeal),
        "active_eligibility": by_status.get("ACTIVE", 0),
        "inactive_eligibility": by_status.get("INACTIVE", 0)
        + by_status.get("TERMINATED", 0),
        "pending_eligibility": by_status.get("PENDING", 0),
        "status_breakdown": by_status,
        "recent_activity": [
            {
                "id": str(r.id),
                "status": r.request_status,
                "scenario": r.scenario,
                "member_id": r.member_id,
                "requested_at": r.requested_at.isoformat(),
            }
            for r in recent
        ],
        "disclaimer": "MOCK DATA – NOT REAL INSURANCE VERIFICATION",
    }
