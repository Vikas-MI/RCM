"""Synthetic FHIR R4 bundles for offline learning (no PHI)."""

MOCK_CAPABILITY = {
    "resourceType": "CapabilityStatement",
    "status": "active",
    "fhirVersion": "4.0.1",
    "source": "MOCK",
    "rest": [
        {
            "mode": "server",
            "resource": [
                {"type": "Patient", "interaction": [{"code": "search-type"}, {"code": "read"}]},
                {"type": "Encounter", "interaction": [{"code": "search-type"}, {"code": "read"}]},
                {"type": "Coverage", "interaction": [{"code": "search-type"}, {"code": "read"}]},
            ],
        }
    ],
    "message": "Synthetic CapabilityStatement — HAPI unreachable or offline mode.",
}

MOCK_PATIENT_BUNDLE = {
    "resourceType": "Bundle",
    "type": "searchset",
    "total": 3,
    "entry": [
        {
            "resource": {
                "resourceType": "Patient",
                "id": "mock-pat-ava",
                "name": [{"family": "Chen", "given": ["Ava"]}],
                "gender": "female",
                "birthDate": "1988-04-12",
                "telecom": [
                    {"system": "phone", "value": "555-0101"},
                    {"system": "email", "value": "ava.chen@example.com"},
                ],
                "address": [
                    {
                        "line": ["100 Maple St"],
                        "city": "Austin",
                        "state": "TX",
                        "postalCode": "78701",
                    }
                ],
            }
        },
        {
            "resource": {
                "resourceType": "Patient",
                "id": "mock-pat-liam",
                "name": [{"family": "Patel", "given": ["Liam"]}],
                "gender": "male",
                "birthDate": "1975-09-03",
                "telecom": [{"system": "phone", "value": "555-0102"}],
                "address": [
                    {
                        "line": ["22 River Rd"],
                        "city": "Dallas",
                        "state": "TX",
                        "postalCode": "75201",
                    }
                ],
            }
        },
        {
            "resource": {
                "resourceType": "Patient",
                "id": "mock-pat-sofia",
                "name": [{"family": "Martinez", "given": ["Sofia"]}],
                "gender": "female",
                "birthDate": "1992-01-28",
                "telecom": [{"system": "email", "value": "sofia.m@example.com"}],
                "address": [
                    {
                        "line": ["9 Oak Ave"],
                        "city": "Houston",
                        "state": "TX",
                        "postalCode": "77002",
                    }
                ],
            }
        },
    ],
}

MOCK_ENCOUNTER_BUNDLE = {
    "resourceType": "Bundle",
    "type": "searchset",
    "total": 3,
    "entry": [
        {
            "resource": {
                "resourceType": "Encounter",
                "id": "mock-enc-ava-office",
                "status": "finished",
                "class": {"code": "AMB", "display": "ambulatory"},
                "type": [{"text": "Office Visit"}],
                "subject": {"reference": "Patient/mock-pat-ava"},
                "period": {"start": "2026-10-01T14:00:00Z", "end": "2026-10-01T14:30:00Z"},
                "reasonCode": [{"text": "Annual wellness"}],
            }
        },
        {
            "resource": {
                "resourceType": "Encounter",
                "id": "mock-enc-liam-er",
                "status": "finished",
                "class": {"code": "EMER", "display": "emergency"},
                "type": [{"text": "ER Visit"}],
                "subject": {"reference": "Patient/mock-pat-liam"},
                "period": {"start": "2026-09-15T08:00:00Z", "end": "2026-09-15T11:00:00Z"},
                "reasonCode": [{"text": "Chest pain"}],
            }
        },
        {
            "resource": {
                "resourceType": "Encounter",
                "id": "mock-enc-sofia-tele",
                "status": "in-progress",
                "class": {"code": "VR", "display": "virtual"},
                "type": [{"text": "Telehealth"}],
                "subject": {"reference": "Patient/mock-pat-sofia"},
                "period": {"start": "2026-11-10T16:00:00Z"},
                "reasonCode": [{"text": "Follow-up"}],
            }
        },
    ],
}

MOCK_COVERAGE_BUNDLE = {
    "resourceType": "Bundle",
    "type": "searchset",
    "total": 3,
    "entry": [
        {
            "resource": {
                "resourceType": "Coverage",
                "id": "mock-cov-ava-acme",
                "status": "active",
                "subscriberId": "MEM-AVA-1001",
                "beneficiary": {"reference": "Patient/mock-pat-ava"},
                "relationship": {"coding": [{"code": "self"}]},
                "payor": [{"display": "Acme Health Insurance", "identifier": {"value": "PAYER001"}}],
                "class": [{"type": {"text": "group"}, "value": "GRP-ACME-9"}],
                "period": {"start": "2026-01-01", "end": "2026-12-31"},
                "order": 1,
            }
        },
        {
            "resource": {
                "resourceType": "Coverage",
                "id": "mock-cov-liam-blue",
                "status": "active",
                "subscriberId": "MEM-LIAM-2002",
                "beneficiary": {"reference": "Patient/mock-pat-liam"},
                "relationship": {"coding": [{"code": "self"}]},
                "payor": [{"display": "Blue Ridge Mutual", "identifier": {"value": "PAYER002"}}],
                "class": [{"type": {"text": "group"}, "value": "GRP-BR-22"}],
                "period": {"start": "2025-06-01", "end": "2026-05-31"},
                "order": 1,
            }
        },
        {
            "resource": {
                "resourceType": "Coverage",
                "id": "mock-cov-sofia-summit",
                "status": "cancelled",
                "subscriberId": "MEM-SOF-3003",
                "beneficiary": {"reference": "Patient/mock-pat-sofia"},
                "relationship": {"coding": [{"code": "self"}]},
                "payor": [{"display": "Summit Care Plan", "identifier": {"value": "PAYER003"}}],
                "period": {"start": "2025-01-01", "end": "2025-12-31"},
                "order": 1,
            }
        },
    ],
}
