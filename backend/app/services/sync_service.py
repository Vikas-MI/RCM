"""Sync EHR (mock Epic / Oracle / HAPI) → Postgres (upsert by external IDs)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.ehr.factory import get_ehr_adapter
from app.integrations.eligibility.availity_mock import MOCK_AVAILITY_PAYERS
from app.models import Encounter, InsurancePolicy, Patient, Payer, PayerMapping
from app.services import fhir_mapper as mapper


def _source_label(ehr_source: str) -> str:
    key = (ehr_source or "mock").lower()
    return {
        "epic": "MOCK_EPIC",
        "oracle": "MOCK_ORACLE",
        "hapi": "HAPI_OR_MOCK",
        "mock": "MOCK_FHIR",
    }.get(key, "MOCK_FHIR")


def _bundle_from_adapter(adapter, kind: str, use_mock_only: bool):
    # For HAPI: when mock_only, use embedded bundles; Epic/Oracle always mock
    from app.integrations.ehr import mock_fhir_data as mock
    from app.integrations.ehr.hapi_adapter import HAPIFHIRAdapter

    if isinstance(adapter, HAPIFHIRAdapter) and use_mock_only:
        return {
            "patients": mock.MOCK_PATIENT_BUNDLE,
            "encounters": mock.MOCK_ENCOUNTER_BUNDLE,
            "coverage": mock.MOCK_COVERAGE_BUNDLE,
        }[kind]
    if kind == "patients":
        return adapter.search_patients()
    if kind == "encounters":
        return adapter.search_encounters()
    return adapter.search_coverage()


def sync_patients(
    db: Session, use_mock_only: bool = True, ehr_source: str = "mock"
) -> dict:
    adapter = get_ehr_adapter(ehr_source)
    bundle = _bundle_from_adapter(adapter, "patients", use_mock_only)
    label = _source_label(ehr_source)
    created = updated = 0
    for entry in bundle.get("entry", []):
        resource = entry.get("resource") or {}
        if resource.get("resourceType") != "Patient":
            continue
        data = mapper.map_patient(resource, source=label)
        existing = db.scalar(
            select(Patient).where(
                Patient.external_ehr_patient_id == data["external_ehr_patient_id"]
            )
        )
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            updated += 1
        else:
            db.add(Patient(**data))
            created += 1
    db.commit()
    return {
        "created": created,
        "updated": updated,
        "source": label,
        "note": "EHR identifiers stored on patients.external_ehr_patient_id",
    }


def sync_encounters(
    db: Session, use_mock_only: bool = True, ehr_source: str = "mock"
) -> dict:
    adapter = get_ehr_adapter(ehr_source)
    bundle = _bundle_from_adapter(adapter, "encounters", use_mock_only)
    created = updated = skipped = 0
    for entry in bundle.get("entry", []):
        resource = entry.get("resource") or {}
        if resource.get("resourceType") != "Encounter":
            continue
        ext_pat = mapper.patient_ref_id(resource)
        patient = db.scalar(
            select(Patient).where(Patient.external_ehr_patient_id == ext_pat)
        )
        if not patient:
            skipped += 1
            continue
        data = mapper.map_encounter(resource, patient.id)
        existing = db.scalar(
            select(Encounter).where(
                Encounter.external_ehr_encounter_id == data["external_ehr_encounter_id"]
            )
        )
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            updated += 1
        else:
            db.add(Encounter(**data))
            created += 1
    db.commit()
    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "source": _source_label(ehr_source),
        "note": "EHR encounter ids stored on encounters.external_ehr_encounter_id",
    }


def sync_coverage(
    db: Session, use_mock_only: bool = True, ehr_source: str = "mock"
) -> dict:
    adapter = get_ehr_adapter(ehr_source)
    bundle = _bundle_from_adapter(adapter, "coverage", use_mock_only)
    created = updated = skipped = 0
    for entry in bundle.get("entry", []):
        resource = entry.get("resource") or {}
        if resource.get("resourceType") != "Coverage":
            continue
        ext_pat = mapper.patient_ref_id(resource)
        patient = db.scalar(
            select(Patient).where(Patient.external_ehr_patient_id == ext_pat)
        )
        if not patient:
            skipped += 1
            continue
        code = mapper.coverage_payer_code(resource)
        name = mapper.coverage_payer_name(resource)
        payer = db.scalar(select(Payer).where(Payer.payer_code == code))
        if not payer:
            payer = Payer(
                payer_name=name,
                payer_code=code,
                description="Auto-created from EHR Coverage (synthetic)",
                is_active=True,
            )
            db.add(payer)
            db.flush()
            _ensure_availity_mapping(db, payer)
        else:
            _ensure_availity_mapping(db, payer)
        data = mapper.map_coverage(resource, patient.id, payer.id)
        existing = db.scalar(
            select(InsurancePolicy).where(
                InsurancePolicy.external_coverage_id == data["external_coverage_id"]
            )
        )
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            updated += 1
        else:
            db.add(InsurancePolicy(**data))
            created += 1
    db.commit()
    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "source": _source_label(ehr_source),
    }


def sync_all(
    db: Session, use_mock_only: bool = True, ehr_source: str = "epic"
) -> dict:
    return {
        "ehr_source": ehr_source,
        "mode": "MOCK" if use_mock_only or ehr_source in ("epic", "oracle", "mock") else "LIVE_ATTEMPT",
        "disclaimer": (
            "Simulated EHR sync — not live Epic, Oracle Health, or production HAPI credentials."
        ),
        "patients": sync_patients(db, use_mock_only=use_mock_only, ehr_source=ehr_source),
        "encounters": sync_encounters(
            db, use_mock_only=use_mock_only, ehr_source=ehr_source
        ),
        "coverage": sync_coverage(db, use_mock_only=use_mock_only, ehr_source=ehr_source),
    }


def ensure_availity_payer_mappings(db: Session) -> dict:
    """Map internal payers → Mock Availity payer IDs (requirement #2/#3)."""
    created = 0
    for row in MOCK_AVAILITY_PAYERS:
        payer = db.scalar(select(Payer).where(Payer.payer_code == row["internal_payer_code"]))
        if not payer:
            payer = Payer(
                payer_name=row["payer_name"],
                payer_code=row["internal_payer_code"],
                description="Seeded for Mock Availity mapping",
                is_active=True,
            )
            db.add(payer)
            db.flush()
        if _ensure_availity_mapping(db, payer, row["availity_payer_id"]):
            created += 1
    db.commit()
    return {
        "mappings_upserted": created,
        "source": "MOCK_AVAILITY",
        "note": "external_payer_identifier holds Availity Payer ID (mock).",
    }


def _ensure_availity_mapping(
    db: Session, payer: Payer, availity_id: str | None = None
) -> bool:
    if not availity_id:
        match = next(
            (
                p
                for p in MOCK_AVAILITY_PAYERS
                if p["internal_payer_code"] == payer.payer_code
            ),
            None,
        )
        if not match:
            availity_id = f"AVAIL-{payer.payer_code}"
        else:
            availity_id = match["availity_payer_id"]
    existing = db.scalar(
        select(PayerMapping).where(
            PayerMapping.internal_payer_id == payer.id,
            PayerMapping.mapping_source == "MOCK_AVAILITY",
        )
    )
    if existing:
        existing.external_payer_identifier = availity_id
        existing.is_active = True
        return False
    db.add(
        PayerMapping(
            internal_payer_id=payer.id,
            external_payer_identifier=availity_id,
            mapping_source="MOCK_AVAILITY",
            is_active=True,
        )
    )
    return True
