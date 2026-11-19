"""Mock Availity clearinghouse — NOT live Availity.

Satisfies POC requirements for:
- retrieving supported payer identifiers (Availity Payer IDs)
- submitting eligibility verification
- returning benefits / status to the RCM app

All traffic is local/synthetic. No Availity API keys or network calls.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.integrations.eligibility.base import EligibilityProvider
from app.integrations.eligibility.mock_provider import (
    MOCK_SCENARIOS,
    MockEligibilityProvider,
)

_DISCLAIMER = (
    "MOCK AVAILITY – Simulated clearinghouse response for POC only. "
    "Not live Availity. No real payer credentials or X12 270/271 traffic."
)

# Synthetic Availity-style payer directory
MOCK_AVAILITY_PAYERS: list[dict[str, Any]] = [
    {
        "availity_payer_id": "AVAIL-ACME-001",
        "payer_name": "Acme Health Insurance",
        "internal_payer_code": "PAYER001",
        "supported_transactions": ["270", "271"],
        "active": True,
    },
    {
        "availity_payer_id": "AVAIL-BLUERIDGE-002",
        "payer_name": "Blue Ridge Mutual",
        "internal_payer_code": "PAYER002",
        "supported_transactions": ["270", "271"],
        "active": True,
    },
    {
        "availity_payer_id": "AVAIL-SUMMIT-003",
        "payer_name": "Summit Care Plan",
        "internal_payer_code": "PAYER003",
        "supported_transactions": ["270", "271"],
        "active": True,
    },
    {
        "availity_payer_id": "AVAIL-BCBS-001",
        "payer_name": "Blue Cross Blue Shield",
        "internal_payer_code": "PAYER_BCBS",
        "supported_transactions": ["270", "271", "837P", "835"],
        "active": True,
    },
    {
        "availity_payer_id": "AVAIL-UHC-001",
        "payer_name": "UnitedHealthcare",
        "internal_payer_code": "PAYER_UHC",
        "supported_transactions": ["270", "271"],
        "active": True,
    },
    {
        "availity_payer_id": "AVAIL-MERCYCARE-001",
        "payer_name": "MercyCare Health Plan",
        "internal_payer_code": "Organization-14404",
        "supported_transactions": ["270", "271"],
        "active": True,
    },
]


class MockAvailityProvider(EligibilityProvider):
    """Drop-in eligibility provider that looks like Availity but is fully mock."""

    def list_payers(self) -> dict[str, Any]:
        return {
            "payers": MOCK_AVAILITY_PAYERS,
            "source": "MOCK_AVAILITY",
            "message": _DISCLAIMER,
            "count": len(MOCK_AVAILITY_PAYERS),
        }

    def verify(self, request: dict[str, Any]) -> dict[str, Any]:
        # Resolve Availity payer id when only internal code provided
        availity_id = request.get("availity_payer_id")
        if not availity_id and request.get("payer_id"):
            availity_id = _lookup_availity_id(str(request["payer_id"]))

        inner = MockEligibilityProvider().verify(request)
        txn = f"MOCK-AVY-{uuid.uuid4().hex[:12].upper()}"
        inner["source"] = "MOCK_AVAILITY"
        inner["clearinghouse"] = "MOCK_AVAILITY"
        inner["availity_payer_id"] = availity_id
        inner["transaction_id"] = txn
        inner["transaction_type"] = "270/271"
        msg = inner.get("message") or ""
        inner["message"] = f"{msg} | {_DISCLAIMER} | txn={txn}"
        return inner


def _lookup_availity_id(payer_code_or_id: str) -> str | None:
    norm = payer_code_or_id.lower().strip()
    for p in MOCK_AVAILITY_PAYERS:
        if (
            p["internal_payer_code"].lower() == norm
            or p["availity_payer_id"].lower() == norm
            or p["payer_name"].lower() in norm
            or norm in p["payer_name"].lower()
        ):
            return p["availity_payer_id"]
    return None


__all__ = [
    "MockAvailityProvider",
    "MOCK_AVAILITY_PAYERS",
    "MOCK_SCENARIOS",
]
