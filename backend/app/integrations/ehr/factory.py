"""Pick an EHR adapter. Live Epic/Oracle need credentials — we use MOCK adapters."""

from __future__ import annotations

from app.integrations.ehr.base import EHRAdapter
from app.integrations.ehr.epic_adapter import EpicFHIRAdapter
from app.integrations.ehr.hapi_adapter import HAPIFHIRAdapter
from app.integrations.ehr.oracle_adapter import OracleFHIRAdapter

VALID_SOURCES = ("mock", "hapi", "epic", "oracle")


def get_ehr_adapter(source: str = "mock") -> EHRAdapter:
    key = (source or "mock").lower().strip()
    if key in ("mock", "hapi"):
        # HAPI adapter falls back to mock bundles when offline / mock mode
        return HAPIFHIRAdapter()
    if key == "epic":
        return EpicFHIRAdapter(use_mock=True)
    if key == "oracle":
        return OracleFHIRAdapter(use_mock=True)
    raise ValueError(f"Unknown EHR source '{source}'. Use one of {VALID_SOURCES}")
