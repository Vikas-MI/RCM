"""HAPI FHIR R4 adapter (public test server). Falls back to synthetic FHIR bundles."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.integrations.ehr.base import EHRAdapter
from app.integrations.ehr.mock_fhir_data import (
    MOCK_CAPABILITY,
    MOCK_COVERAGE_BUNDLE,
    MOCK_ENCOUNTER_BUNDLE,
    MOCK_PATIENT_BUNDLE,
)

logger = get_logger(__name__)


class HAPIFHIRAdapter(EHRAdapter):
    def __init__(self, base_url: str | None = None, timeout: float = 15.0) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.hapi_fhir_base_url).rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(url, params=params or {})
                res.raise_for_status()
                return res.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("HAPI request failed (%s) — using MOCK FHIR data", exc)
            raise

    def get_capability_statement(self) -> dict[str, Any]:
        try:
            return self._get("metadata")
        except Exception:
            return MOCK_CAPABILITY

    def search_patients(self, **params: Any) -> dict[str, Any]:
        try:
            return self._get("Patient", params={**params, "_count": params.get("_count", 20)})
        except Exception:
            return MOCK_PATIENT_BUNDLE

    def get_patient(self, external_id: str) -> dict[str, Any]:
        try:
            return self._get(f"Patient/{external_id}")
        except Exception:
            for entry in MOCK_PATIENT_BUNDLE.get("entry", []):
                res = entry.get("resource", {})
                if res.get("id") == external_id:
                    return res
            return MOCK_PATIENT_BUNDLE["entry"][0]["resource"]

    def search_encounters(self, **params: Any) -> dict[str, Any]:
        try:
            return self._get(
                "Encounter", params={**params, "_count": params.get("_count", 20)}
            )
        except Exception:
            return MOCK_ENCOUNTER_BUNDLE

    def search_coverage(self, **params: Any) -> dict[str, Any]:
        try:
            return self._get(
                "Coverage", params={**params, "_count": params.get("_count", 20)}
            )
        except Exception:
            return MOCK_COVERAGE_BUNDLE
