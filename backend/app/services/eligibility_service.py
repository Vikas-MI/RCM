from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.integrations.eligibility.availity_mock import (
    MOCK_SCENARIOS,
    MockAvailityProvider,
)
from app.models import (
    EligibilityHistory,
    EligibilityRequest,
    EligibilityResponse,
    InsurancePolicy,
    Patient,
    Payer,
    PayerMapping,
)


def verify_eligibility(
    db: Session,
    *,
    patient_id: UUID,
    insurance_policy_id: UUID,
    encounter_id: UUID | None,
    service_date,
    scenario: str,
) -> EligibilityRequest:
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(400, "Patient is required and must exist.")

    policy = db.get(InsurancePolicy, insurance_policy_id)
    if not policy or policy.patient_id != patient_id:
        raise HTTPException(400, "Valid insurance policy for this patient is required.")

    if not policy.member_id:
        raise HTTPException(400, "Member ID is required on the insurance policy.")

    payer = db.get(Payer, policy.payer_id)
    scenario = scenario.upper()
    if scenario not in MOCK_SCENARIOS:
        raise HTTPException(400, f"scenario must be one of {MOCK_SCENARIOS}")

    availity_payer_id = None
    if payer:
        mapping = db.scalar(
            select(PayerMapping).where(
                PayerMapping.internal_payer_id == payer.id,
                PayerMapping.mapping_source == "MOCK_AVAILITY",
                PayerMapping.is_active.is_(True),
            )
        )
        availity_payer_id = (
            mapping.external_payer_identifier if mapping else None
        )

    now = datetime.now(timezone.utc)
    # Requirement: eligibility via Availity — we use MOCK Availity only
    provider = MockAvailityProvider()
    payload = {
        "patient_id": str(patient_id),
        "member_id": policy.member_id,
        "payer_id": payer.payer_code if payer else str(policy.payer_id),
        "payer_name": payer.payer_name if payer else None,
        "availity_payer_id": availity_payer_id,
        "service_date": service_date.isoformat(),
        "scenario": scenario,
        "coverage_start_date": (
            policy.coverage_start_date.isoformat()
            if policy.coverage_start_date
            else None
        ),
        "coverage_end_date": (
            policy.coverage_end_date.isoformat() if policy.coverage_end_date else None
        ),
        "clearinghouse": "MOCK_AVAILITY",
    }
    result = provider.verify(payload)

    req = EligibilityRequest(
        patient_id=patient_id,
        encounter_id=encounter_id,
        insurance_policy_id=insurance_policy_id,
        payer_id=policy.payer_id,
        member_id=policy.member_id,
        service_date=service_date,
        request_status=result["status"],
        scenario=scenario,
        request_payload=payload,
        requested_at=now,
    )
    db.add(req)
    db.flush()

    resp = EligibilityResponse(
        eligibility_request_id=req.id,
        eligibility_status=result["status"],
        payer_name=result.get("payer_name"),
        member_id=result.get("member_id"),
        coverage_start_date=_d(result.get("coverage_start")),
        coverage_end_date=_d(result.get("coverage_end")),
        copay=_money(result.get("copay")),
        deductible=_money(result.get("deductible")),
        deductible_remaining=_money(result.get("deductible_remaining")),
        coinsurance=result.get("coinsurance"),
        benefits=result.get("benefits"),
        response_payload=result,
        source="MOCK_AVAILITY",
        response_message=result.get("message"),
        responded_at=now,
    )
    db.add(resp)
    db.add(
        EligibilityHistory(
            patient_id=patient_id,
            insurance_policy_id=insurance_policy_id,
            eligibility_request_id=req.id,
            previous_status=None,
            current_status=result["status"],
            action="VERIFY_MOCK_AVAILITY",
            details={
                "scenario": scenario,
                "source": "MOCK_AVAILITY",
                "availity_payer_id": availity_payer_id,
                "transaction_id": result.get("transaction_id"),
            },
        )
    )
    db.commit()
    db.refresh(req)
    return (
        db.scalar(
            select(EligibilityRequest)
            .options(joinedload(EligibilityRequest.response))
            .where(EligibilityRequest.id == req.id)
        )
        or req
    )


def retry_eligibility(db: Session, request_id: UUID) -> EligibilityRequest:
    old = db.scalar(
        select(EligibilityRequest)
        .options(joinedload(EligibilityRequest.response))
        .where(EligibilityRequest.id == request_id)
    )
    if not old:
        raise HTTPException(404, "Eligibility request not found")
    return verify_eligibility(
        db,
        patient_id=old.patient_id,
        insurance_policy_id=old.insurance_policy_id,
        encounter_id=old.encounter_id,
        service_date=old.service_date,
        scenario=old.scenario,
    )


def _money(value) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _d(value):
    if not value:
        return None
    from datetime import date

    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])
