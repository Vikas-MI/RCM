"""Epic FHIR adapter — MOCK mode for POC demos (no Epic credentials).

LIVE Epic OAuth / sandbox is NOT configured. All responses are synthetic and
labeled MOCK_EPIC so demos never look like real Epic traffic.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.integrations.ehr.base import EHRAdapter
from app.integrations.ehr import mock_fhir_data as mock


_DISCLAIMER = (
    "MOCK EPIC – Simulated Epic FHIR R4 responses for POC only. "
    "Not live Epic / MyChart / Epic sandbox. No Epic credentials used."
)


class EpicFHIRAdapter(EHRAdapter):
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock

    def get_capability_statement(self) -> dict[str, Any]:
        cap = deepcopy(mock.MOCK_CAPABILITY)
        cap["software"] = {"name": "Mock Epic FHIR", "version": "poc-mock"}
        cap["source"] = "MOCK_EPIC"
        cap["message"] = _DISCLAIMER
        return cap

    def search_patients(self, **params: Any) -> dict[str, Any]:
        return self._tag_bundle(deepcopy(mock.MOCK_PATIENT_BUNDLE), "Patient")

    def get_patient(self, external_id: str) -> dict[str, Any]:
        for entry in mock.MOCK_PATIENT_BUNDLE.get("entry", []):
            res = entry.get("resource") or {}
            if res.get("id") == external_id or res.get("id") == external_id.replace(
                "epic-", ""
            ):
                return self._tag_resource(deepcopy(res), "Patient")
        return {
            "resourceType": "OperationOutcome",
            "issue": [{"severity": "error", "diagnostics": f"Mock Epic patient {external_id} not found"}],
            "source": "MOCK_EPIC",
            "message": _DISCLAIMER,
        }

    def search_encounters(self, **params: Any) -> dict[str, Any]:
        return self._tag_bundle(deepcopy(mock.MOCK_ENCOUNTER_BUNDLE), "Encounter")

    def search_coverage(self, **params: Any) -> dict[str, Any]:
        return self._tag_bundle(deepcopy(mock.MOCK_COVERAGE_BUNDLE), "Coverage")

    def _tag_bundle(self, bundle: dict[str, Any], rtype: str) -> dict[str, Any]:
        bundle["source"] = "MOCK_EPIC"
        bundle["message"] = _DISCLAIMER
        for entry in bundle.get("entry", []):
            res = entry.get("resource") or {}
            if res.get("resourceType") == rtype:
                entry["resource"] = self._tag_resource(res, rtype)
            # Fix patient references after id rewrite
            if rtype in ("Encounter", "Coverage"):
                self._rewrite_patient_ref(entry.get("resource") or {})
        return bundle

    def _tag_resource(self, res: dict[str, Any], rtype: str) -> dict[str, Any]:
        rid = res.get("id") or "unknown"
        if not str(rid).startswith("epic-"):
            res["id"] = f"epic-{rid}"
        res["meta"] = {
            **(res.get("meta") or {}),
            "source": "MOCK_EPIC",
            "tag": [{"system": "https://smart-rcm.local/mock", "code": "MOCK_EPIC"}],
        }
        res["extension"] = (res.get("extension") or []) + [
            {
                "url": "https://smart-rcm.local/ehr-system",
                "valueString": "MOCK_EPIC",
            }
        ]
        if rtype == "Patient":
            # Keep identifiers for EHR reference requirement
            res["identifier"] = (res.get("identifier") or []) + [
                {
                    "system": "urn:oid:mock.epic.patient",
                    "value": res["id"],
                    "type": {"text": "Mock Epic Patient ID"},
                }
            ]
        return res

    def _rewrite_patient_ref(self, res: dict[str, Any]) -> None:
        for key in ("subject", "beneficiary", "patient"):
            ref_obj = res.get(key)
            if isinstance(ref_obj, dict) and "reference" in ref_obj:
                ref = ref_obj["reference"]
                if ref.startswith("Patient/") and not ref.startswith("Patient/epic-"):
                    ref_obj["reference"] = ref.replace("Patient/", "Patient/epic-", 1)
