from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    db_ok = False
    db_error: str | None = None
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:  # noqa: BLE001
        db_error = str(exc.__class__.__name__)

    return {
        "status": "ok" if db_ok else "degraded",
        "app": settings.app_name,
        "env": settings.app_env,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {
            "connected": db_ok,
            "error": db_error,
        },
        "note": (
            "RCM POC — Mock Epic/Oracle EHR + PostgreSQL + Mock Availity. "
            "Not live insurance verification."
        ),
    }


@router.get("/integrations/status")
def integrations_status(settings: Settings = Depends(get_settings)) -> dict:
    return {
        "ehr": {
            "epic": {
                "mode": "MOCK",
                "live": False,
                "note": "Mock Epic FHIR adapter — no Epic credentials",
            },
            "oracle_health": {
                "mode": "MOCK",
                "live": False,
                "note": "Mock Oracle Health FHIR adapter — no Oracle credentials",
            },
            "hapi_fhir": {
                "mode": "MOCK_OR_PUBLIC",
                "base_url": settings.hapi_fhir_base_url,
                "live": False,
                "note": "Optional public HAPI; sync defaults to mock bundles",
            },
        },
        "availity": {
            "mode": "MOCK",
            "live": False,
            "enabled": False,
            "active_provider": "MOCK_AVAILITY",
            "note": "Mock Availity payer directory + 270/271-style eligibility. Not live Availity.",
        },
        "eligibility_provider": {
            "active": "MOCK_AVAILITY",
            "status": "ready",
            "note": "Eligibility verify stores request/response/history in PostgreSQL.",
        },
        "document_intelligence": {
            "active": "MOCK_AZURE_DI",
            "azure_configured": False,
            "note": "Optional learning module — not part of core Availity POC.",
        },
        "disclaimer": (
            "All external systems are simulated for this POC. Results are mock, not live."
        ),
    }
