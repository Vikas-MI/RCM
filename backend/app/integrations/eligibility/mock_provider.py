"""Internal Mock Eligibility Provider — NOT a real clearinghouse."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.integrations.eligibility.base import EligibilityProvider

MOCK_SCENARIOS = [
    "ACTIVE",
    "INACTIVE",
    "TERMINATED",
    "PENDING",
    "UNABLE_TO_VERIFY",
    "ERROR",
]

_DISCLAIMER = "Synthetic eligibility response for demonstration. MOCK DATA – NOT REAL INSURANCE VERIFICATION."


class MockEligibilityProvider(EligibilityProvider):
    def verify(self, request: dict[str, Any]) -> dict[str, Any]:
        scenario = str(request.get("scenario", "ACTIVE")).upper()
        member_id = str(request.get("member_id", "")).strip()
        payer_name = str(request.get("payer_name") or "ABC Health Insurance")
        service_date = _parse_date(request.get("service_date"))
        cov_start = _parse_date(request.get("coverage_start_date")) or date(2026, 1, 1)
        cov_end = _parse_date(request.get("coverage_end_date")) or date(2026, 12, 31)

        if not member_id:
            return _error("Member ID is required.", scenario="ERROR")

        if service_date is None:
            return _error("Valid service_date (YYYY-MM-DD) is required.", scenario="ERROR")

        if scenario not in MOCK_SCENARIOS:
            return _error(f"Unknown scenario: {scenario}", scenario="ERROR")

        # Deterministic coverage-window check for ACTIVE
        if scenario == "ACTIVE" and not (cov_start <= service_date <= cov_end):
            return {
                "status": "INACTIVE",
                "payer_name": payer_name,
                "member_id": member_id,
                "coverage_start": cov_start.isoformat(),
                "coverage_end": cov_end.isoformat(),
                "copay": None,
                "deductible": None,
                "deductible_remaining": None,
                "coinsurance": None,
                "benefits": {"note": "Service date outside coverage period."},
                "source": "MOCK",
                "message": f"Service date {service_date} is outside coverage. {_DISCLAIMER}",
            }

        templates: dict[str, dict[str, Any]] = {
            "ACTIVE": {
                "status": "ACTIVE",
                "copay": 30,
                "deductible": 1500,
                "deductible_remaining": 800,
                "coinsurance": "20%",
                "benefits": {
                    "office_visit": "Covered with $30 copay",
                    "preventive": "Covered 100%",
                    "er": "Covered after deductible",
                },
                "message": f"Policy active for service date. {_DISCLAIMER}",
            },
            "INACTIVE": {
                "status": "INACTIVE",
                "copay": None,
                "deductible": None,
                "deductible_remaining": None,
                "coinsurance": None,
                "benefits": {"note": "Policy inactive."},
                "message": f"Policy inactive. {_DISCLAIMER}",
            },
            "TERMINATED": {
                "status": "TERMINATED",
                "copay": None,
                "deductible": None,
                "deductible_remaining": None,
                "coinsurance": None,
                "benefits": {"termination_date": cov_end.isoformat()},
                "message": f"Policy terminated. {_DISCLAIMER}",
            },
            "PENDING": {
                "status": "PENDING",
                "copay": None,
                "deductible": None,
                "deductible_remaining": None,
                "coinsurance": None,
                "benefits": {"note": "Verification pending with mock payer."},
                "message": f"Verification pending. {_DISCLAIMER}",
            },
            "UNABLE_TO_VERIFY": {
                "status": "UNABLE_TO_VERIFY",
                "copay": None,
                "deductible": None,
                "deductible_remaining": None,
                "coinsurance": None,
                "benefits": {"note": "Mock payer could not verify membership."},
                "message": f"Unable to verify. {_DISCLAIMER}",
            },
            "ERROR": {
                "status": "ERROR",
                "copay": None,
                "deductible": None,
                "deductible_remaining": None,
                "coinsurance": None,
                "benefits": {"error_code": "MOCK_INTEGRATION_ERROR"},
                "message": f"Simulated integration error. {_DISCLAIMER}",
            },
        }

        body = templates[scenario]
        return {
            "status": body["status"],
            "payer_name": payer_name,
            "member_id": member_id,
            "coverage_start": cov_start.isoformat(),
            "coverage_end": cov_end.isoformat(),
            "copay": body["copay"],
            "deductible": body["deductible"],
            "deductible_remaining": body["deductible_remaining"],
            "coinsurance": body["coinsurance"],
            "benefits": body["benefits"],
            "source": "MOCK",
            "message": body["message"],
        }


def _parse_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _error(message: str, scenario: str = "ERROR") -> dict[str, Any]:
    return {
        "status": scenario,
        "payer_name": None,
        "member_id": None,
        "coverage_start": None,
        "coverage_end": None,
        "copay": None,
        "deductible": None,
        "deductible_remaining": None,
        "coinsurance": None,
        "benefits": None,
        "source": "MOCK",
        "message": f"{message} {_DISCLAIMER}",
    }
