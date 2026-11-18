"""Oracle Health (Cerner) FHIR adapter — MOCK mode for POC demos.

LIVE Oracle Health credentials are NOT configured. Responses are synthetic and
labeled MOCK_ORACLE.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.integrations.ehr.base import EHRAdapter
from app.integrations.ehr import mock_fhir_data as mock


_DISCLAIMER = (
    "MOCK ORACLE HEALTH – Simulated Oracle Health / Cerner FHIR R4 for POC only. "
    "Not live Oracle Health. No Oracle credentials used."
)


class OracleFHIRAdapter(EHRAdapter):
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock

    def get_capability_statement(self) -> dict[str, Any]:
        cap = deepcopy(mock.MOCK_CAPABILITY)
        cap["software"] = {"name": "Mock Oracle Health FHIR", "version": "poc-mock"}
        cap["source"] = "MOCK_ORACLE"
        cap["message"] = _DISCLAIMER
        return cap

    def search_patients(self, **params: Any) -> dict[str, Any]:
        return self._tag_bundle(deepcopy(mock.MOCK_PATIENT_BUNDLE), "Patient")

    def get_patient(self, external_id: str) -> dict[str, Any]:
        for entry in mock.MOCK_PATIENT_BUNDLE.get("entry", []):
            res = entry.get("resource") or {}
            rid = res.get("id")
            if rid == external_id or f"oracle-{rid}" == external_id:
                return self._tag_resource(deepcopy(res), "Patient")
        return {
            "resourceType": "OperationOutcome",
            "issue": [{"severity": "error", "diagnostics": f"Mock Oracle patient {external_id} not found"}],
            "source": "MOCK_ORACLE",
            "message": _DISCLAIMER,
        }

    def search_encounters(self, **params: Any) -> dict[str, Any]:
        return self._tag_bundle(deepcopy(mock.MOCK_ENCOUNTER_BUNDLE), "Encounter")

    def search_coverage(self, **params: Any) -> dict[str, Any]:
        return self._tag_bundle(deepcopy(mock.MOCK_COVERAGE_BUNDLE), "Coverage")

    def _tag_bundle(self, bundle: dict[str, Any], rtype: str) -> dict[str, Any]:
        bundle["source"] = "MOCK_ORACLE"
        bundle["message"] = _DISCLAIMER
        for entry in bundle.get("entry", []):
            res = entry.get("resource") or {}
            if res.get("resourceType") == rtype:
                entry["resource"] = self._tag_resource(res, rtype)
            if rtype in ("Encounter", "Coverage"):
                self._rewrite_patient_ref(entry.get("resource") or {})
        return bundle

    def _tag_resource(self, res: dict[str, Any], rtype: str) -> dict[str, Any]:
        rid = res.get("id") or "unknown"
        if not str(rid).startswith("oracle-"):
            res["id"] = f"oracle-{rid}"
        res["meta"] = {
            **(res.get("meta") or {}),
            "source": "MOCK_ORACLE",
            "tag": [{"system": "https://smart-rcm.local/mock", "code": "MOCK_ORACLE"}],
        }
        res["extension"] = (res.get("extension") or []) + [
            {
                "url": "https://smart-rcm.local/ehr-system",
                "valueString": "MOCK_ORACLE",
            }
        ]
        if rtype == "Patient":
            res["identifier"] = (res.get("identifier") or []) + [
                {
                    "system": "urn:oid:mock.oracle.patient",
                    "value": res["id"],
                    "type": {"text": "Mock Oracle Health Patient ID"},
                }
            ]
        return res

    def _rewrite_patient_ref(self, res: dict[str, Any]) -> None:
        for key in ("subject", "beneficiary", "patient"):
            ref_obj = res.get(key)
            if isinstance(ref_obj, dict) and "reference" in ref_obj:
                ref = ref_obj["reference"]
                if ref.startswith("Patient/") and not ref.startswith("Patient/oracle-"):
                    ref_obj["reference"] = ref.replace("Patient/", "Patient/oracle-", 1)
