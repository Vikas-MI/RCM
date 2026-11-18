"""Mock Azure Document Intelligence — NO Azure credentials required."""

from __future__ import annotations

from typing import Any

from app.integrations.documents.base import DocumentIntelligenceProvider

_DISCLAIMER = (
    "MOCK OCR – NOT Azure Document Intelligence. Synthetic extraction for learning only."
)

# Pretend “templates” the OCR engine recognized
_TEMPLATES: dict[str, dict[str, Any]] = {
    "insurance_card": {
        "fields": {
            "payer_name": "Acme Health Insurance",
            "member_id": "MEM-AVA-1001",
            "group_number": "GRP-ACME-9",
            "subscriber_name": "Ava Chen",
            "plan_type": "PPO",
            "effective_date": "2026-01-01",
        },
        "confidence": 0.94,
    },
    "eob": {
        "fields": {
            "claim_number": "CLM-2026-1001",
            "patient_name": "Ava Chen",
            "service_date": "2026-03-12",
            "billed_amount": 450.00,
            "allowed_amount": 320.00,
            "paid_amount": 0.00,
            "patient_responsibility": 320.00,
            "denial_code": "CO-50",
            "denial_reason": "These are non-covered services because this is not deemed a medical necessity.",
        },
        "confidence": 0.91,
    },
    "medical_record": {
        "fields": {
            "patient_name": "Liam Patel",
            "visit_date": "2026-02-20",
            "chief_complaint": "Persistent lower back pain for 6 weeks",
            "assessment": "M54.5 Low back pain",
            "plan": "PT referral; MRI if no improvement in 4 weeks",
            "provider": "Dr. Rivera",
        },
        "confidence": 0.88,
    },
    "cms1500": {
        "fields": {
            "patient_name": "Sofia Martinez",
            "dob": "1992-01-28",
            "cpt": ["99213", "97110"],
            "icd10": ["M54.5"],
            "place_of_service": "11",
            "charges": 285.00,
            "npi": "1234567890",
        },
        "confidence": 0.90,
    },
}


class MockAzureDocumentIntelligence(DocumentIntelligenceProvider):
    def extract(
        self, *, doc_type: str, filename: str, hint: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        key = doc_type.lower().strip()
        template = _TEMPLATES.get(key) or {
            "fields": {"note": f"Unrecognized doc_type '{doc_type}' — used generic mock."},
            "confidence": 0.5,
        }
        fields = dict(template["fields"])
        if hint:
            # Allow seed / UI to override a few fields for demos
            fields.update({k: v for k, v in hint.items() if v is not None})

        return {
            "provider": "MOCK_AZURE_DI",
            "model": "prebuilt-mock-healthcare-v1",
            "doc_type": key,
            "filename": filename,
            "fields": fields,
            "confidence": template.get("confidence", 0.8),
            "pages": 1,
            "message": _DISCLAIMER,
        }


class AzureDocumentIntelligenceStub(DocumentIntelligenceProvider):
    """Real Azure DI would go here — intentionally disabled for this POC."""

    def extract(
        self, *, doc_type: str, filename: str, hint: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return {
            "provider": "AZURE_DI",
            "configured": False,
            "doc_type": doc_type,
            "filename": filename,
            "fields": {},
            "confidence": 0,
            "message": (
                "Azure Document Intelligence is not configured (by design for learning). "
                "Use MOCK_AZURE_DI instead."
            ),
        }
