"""Map FHIR R4 resources → internal dicts (ELI5: translate hospital language → our DB language)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any


def map_patient(resource: dict[str, Any], source: str = "HAPI_FHIR_OR_MOCK") -> dict[str, Any]:
    name = (resource.get("name") or [{}])[0]
    given = name.get("given") or [""]
    telecom = resource.get("telecom") or []
    phone = next((t.get("value") for t in telecom if t.get("system") == "phone"), None)
    email = next((t.get("value") for t in telecom if t.get("system") == "email"), None)
    addr = (resource.get("address") or [{}])[0]
    # Prefer meta.source / extension when adapters tag MOCK_EPIC / MOCK_ORACLE
    meta_source = (resource.get("meta") or {}).get("source")
    return {
        "external_ehr_patient_id": resource.get("id"),
        "first_name": given[0] if given else "Unknown",
        "last_name": name.get("family") or "Unknown",
        "date_of_birth": _date(resource.get("birthDate")),
        "gender": resource.get("gender"),
        "email": email,
        "phone": phone,
        "address": ", ".join(addr.get("line") or []) or None,
        "city": addr.get("city"),
        "state": addr.get("state"),
        "postal_code": addr.get("postalCode"),
        "raw_fhir_resource": resource,
        "source": meta_source or source,
    }


def map_encounter(resource: dict[str, Any], patient_id) -> dict[str, Any]:
    period = resource.get("period") or {}
    enc_type = None
    types = resource.get("type") or []
    if types:
        enc_type = types[0].get("text") or (types[0].get("coding") or [{}])[0].get("display")
    klass = resource.get("class") or {}
    reasons = resource.get("reasonCode") or []
    reason = reasons[0].get("text") if reasons else None
    return {
        "patient_id": patient_id,
        "external_ehr_encounter_id": resource.get("id"),
        "encounter_type": enc_type,
        "encounter_status": resource.get("status"),
        "encounter_class": klass.get("code") or klass.get("display"),
        "start_date": _datetime(period.get("start")),
        "end_date": _datetime(period.get("end")),
        "reason": reason,
        "raw_fhir_resource": resource,
    }


def map_coverage(resource: dict[str, Any], patient_id, payer_id) -> dict[str, Any]:
    period = resource.get("period") or {}
    classes = resource.get("class") or []
    group = next((c.get("value") for c in classes if (c.get("type") or {}).get("text") == "group"), None)
    rel = ((resource.get("relationship") or {}).get("coding") or [{}])[0].get("code")
    status = resource.get("status") or "active"
    return {
        "patient_id": patient_id,
        "payer_id": payer_id,
        "member_id": resource.get("subscriberId") or "UNKNOWN",
        "group_number": group,
        "policy_number": resource.get("id"),
        "policy_type": "commercial",
        "relationship_to_subscriber": rel or "self",
        "coverage_status": status,
        "coverage_start_date": _date(period.get("start")),
        "coverage_end_date": _date(period.get("end")),
        "is_primary": (resource.get("order") or 1) == 1,
        "is_active": status == "active",
        "external_coverage_id": resource.get("id"),
        "raw_fhir_resource": resource,
    }


def patient_ref_id(resource: dict[str, Any]) -> str | None:
    ref = ((resource.get("subject") or resource.get("beneficiary") or {}).get("reference")) or ""
    if "/" in ref:
        return ref.split("/")[-1]
    return None


def coverage_payer_code(resource: dict[str, Any]) -> str:
    payors = resource.get("payor") or [{}]
    ident = (payors[0].get("identifier") or {}).get("value")
    return ident or "PAYER_UNKNOWN"


def coverage_payer_name(resource: dict[str, Any]) -> str:
    payors = resource.get("payor") or [{}]
    return payors[0].get("display") or "Unknown Payer"


def _date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
