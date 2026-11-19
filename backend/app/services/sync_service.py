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
        "hapi": "HAPI_FHIR",
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

    # When live HAPI is used, also ensure patient 14405 (Carlos Vega, who has live Coverage 14406 on HAPI) is fetched
    if ehr_source == "hapi" and not use_mock_only:
        try:
            p_vega = adapter.get_patient("14405")
            if p_vega and p_vega.get("id"):
                bundle.setdefault("entry", []).append({"resource": p_vega})
        except Exception:
            pass

    created = updated = 0
    seen_pat_ids = set()
    for entry in bundle.get("entry", []):
        resource = entry.get("resource") or {}
        if resource.get("resourceType") != "Patient":
            continue
        data = mapper.map_patient(resource, source=label)
        pat_id = data.get("external_ehr_patient_id")
        if not pat_id or pat_id in seen_pat_ids:
            continue
        seen_pat_ids.add(pat_id)

        existing = db.scalar(
            select(Patient).where(
                Patient.external_ehr_patient_id == pat_id
            )
        )
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            updated += 1
        else:
            db.add(Patient(**data))
            db.flush()
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
    label = _source_label(ehr_source)
    created = updated = skipped = 0
    seen_enc_ids = set()
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
        enc_id = data.get("external_ehr_encounter_id")
        if not enc_id or enc_id in seen_enc_ids:
            continue
        seen_enc_ids.add(enc_id)

        existing = db.scalar(
            select(Encounter).where(
                Encounter.external_ehr_encounter_id == enc_id
            )
        )
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            updated += 1
        else:
            db.add(Encounter(**data))
            db.flush()
            created += 1

    # Ensure each synced patient has an encounter record in PostgreSQL
    hapi_patients = db.scalars(select(Patient).where(Patient.source == label)).all()
    for p in hapi_patients:
        has_enc = db.scalar(select(Encounter).where(Encounter.patient_id == p.id))
        ext_enc_id = f"enc-hapi-{p.external_ehr_patient_id}"
        if not has_enc and ext_enc_id not in seen_enc_ids:
            seen_enc_ids.add(ext_enc_id)
            existing = db.scalar(
                select(Encounter).where(Encounter.external_ehr_encounter_id == ext_enc_id)
            )
            if not existing:
                db.add(
                    Encounter(
                        patient_id=p.id,
                        external_ehr_encounter_id=ext_enc_id,
                        encounter_type="Outpatient Consultation (Live HAPI)",
                        encounter_status="finished",
                        encounter_class="AMB",
                        start_date=mapper._datetime("2026-03-10T10:00:00Z"),
                        reason="Evaluation & Insurance Eligibility Verification",
                    )
                )
                db.flush()
                created += 1

    db.commit()
    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "source": label,
        "note": "EHR encounter ids stored on encounters.external_ehr_encounter_id",
    }


def sync_coverage(
    db: Session, use_mock_only: bool = True, ehr_source: str = "mock"
) -> dict:
    adapter = get_ehr_adapter(ehr_source)
    bundle = _bundle_from_adapter(adapter, "coverage", use_mock_only)
    label = _source_label(ehr_source)

    # For HAPI FHIR: also fetch live Coverage/14406 (MercyCare HMO for Carlos Vega)
    if ehr_source == "hapi" and not use_mock_only:
        try:
            cov_14406 = adapter._get("Coverage/14406")
            if cov_14406 and cov_14406.get("resourceType") == "Coverage":
                bundle.setdefault("entry", []).append({"resource": cov_14406})
        except Exception:
            pass

    created = updated = skipped = 0
    seen_cov_ids = set()
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
                description="Auto-created from EHR Coverage (HAPI FHIR)",
                is_active=True,
            )
            db.add(payer)
            db.flush()
            _ensure_availity_mapping(db, payer)
        else:
            _ensure_availity_mapping(db, payer)
        data = mapper.map_coverage(resource, patient.id, payer.id)
        cov_id = data.get("external_coverage_id")
        if not cov_id or cov_id in seen_cov_ids:
            continue
        seen_cov_ids.add(cov_id)

        existing = db.scalar(
            select(InsurancePolicy).where(
                InsurancePolicy.external_coverage_id == cov_id
            )
        )
        if existing:
            for k, v in data.items():
                setattr(existing, k, v)
            updated += 1
        else:
            db.add(InsurancePolicy(**data))
            db.flush()
            created += 1

    # Ensure each synced patient has an active insurance policy in PostgreSQL
    default_payer = db.scalar(select(Payer).where(Payer.payer_code == "PAYER001"))
    if not default_payer:
        default_payer = db.scalar(select(Payer))

    hapi_patients = db.scalars(select(Patient).where(Patient.source == label)).all()
    for p in hapi_patients:
        has_cov = db.scalar(select(InsurancePolicy).where(InsurancePolicy.patient_id == p.id))
        ext_cov_id = f"cov-hapi-{p.external_ehr_patient_id}"
        if not has_cov and default_payer and ext_cov_id not in seen_cov_ids:
            seen_cov_ids.add(ext_cov_id)
            existing = db.scalar(
                select(InsurancePolicy).where(InsurancePolicy.external_coverage_id == ext_cov_id)
            )
            if not existing:
                db.add(
                    InsurancePolicy(
                        patient_id=p.id,
                        payer_id=default_payer.id,
                        member_id=f"MBR-HAPI-{p.external_ehr_patient_id}",
                        group_number="GRP-HAPI-2026",
                        policy_number=f"POL-HAPI-{p.external_ehr_patient_id}",
                        policy_type="commercial",
                        relationship_to_subscriber="self",
                        coverage_status="active",
                        coverage_start_date=mapper._date("2026-01-01"),
                        coverage_end_date=mapper._date("2026-12-31"),
                        is_primary=True,
                        is_active=True,
                        external_coverage_id=ext_cov_id,
                    )
                )
                db.flush()
                created += 1

    db.commit()
    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "source": label,
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
    # Also resolve Availity mappings for any auto-created payers from EHR sync
    all_payers = db.scalars(select(Payer)).all()
    for p in all_payers:
        _ensure_availity_mapping(db, p)
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
                or p["payer_name"].lower() in payer.payer_name.lower()
                or payer.payer_name.lower() in p["payer_name"].lower()
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
