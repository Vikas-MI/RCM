from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_capstone_ehr_sources():
    """Task 1: Verify EHR Sources list HAPI FHIR as active live API."""
    res = client.get("/api/ehr/sources")
    assert res.status_code == 200
    data = res.json()
    hapi = next((s for s in data["sources"] if s["id"] == "hapi"), None)
    assert hapi is not None
    assert hapi["live"] is True
    assert "hapi.fhir.org" in hapi["note"]


def test_capstone_availity_payers():
    """Task 3: Retrieve supported payer information and Availity payer identifiers."""
    res = client.get("/api/availity/payers")
    assert res.status_code == 200
    data = res.json()
    assert "payers" in data
    assert len(data["payers"]) >= 5
    payer_ids = [p["availity_payer_id"] for p in data["payers"]]
    assert "AVAIL-ACME-001" in payer_ids
    assert "AVAIL-MERCYCARE-001" in payer_ids


def test_capstone_payer_mappings_sync():
    """Task 2 & 3: Map insurance providers to Availity Payer IDs in PostgreSQL."""
    sync_res = client.post("/api/availity/payers/sync-mappings")
    assert sync_res.status_code == 200

    list_res = client.get("/api/payer-mappings")
    assert list_res.status_code == 200
    mappings = list_res.json()
    assert len(mappings) > 0
    availity_ids = [m["external_payer_identifier"] for m in mappings if m["mapping_source"] == "MOCK_AVAILITY"]
    assert "AVAIL-ACME-001" in availity_ids
    assert "AVAIL-MERCYCARE-001" in availity_ids


def test_capstone_patient_and_encounter_external_ids():
    """Task 1 & 2: Patient and encounter records maintain external EHR IDs."""
    patients_res = client.get("/api/patients?limit=5")
    assert patients_res.status_code == 200
    patients_data = patients_res.json()
    assert patients_data["total"] > 0
    sample_patient = patients_data["items"][0]
    assert sample_patient["external_ehr_patient_id"] is not None

    encounters_res = client.get("/api/encounters?limit=5")
    assert encounters_res.status_code == 200
    encounters_data = encounters_res.json()
    assert encounters_data["total"] > 0
    sample_enc = encounters_data["items"][0]
    assert sample_enc["external_ehr_encounter_id"] is not None


def test_capstone_eligibility_verification_and_history():
    """Task 2, 4, 5: Initiate verification, receive benefits, store response and history."""
    # Retrieve a patient with insurance
    patients_res = client.get("/api/patients?limit=20")
    patients = patients_res.json()["items"]
    
    target_patient = None
    target_policy = None
    for p in patients:
        ins_res = client.get(f"/api/patients/{p['id']}/insurance")
        ins_data = ins_res.json()
        if ins_data.get("items"):
            target_patient = p
            target_policy = ins_data["items"][0]
            break

    assert target_patient is not None
    assert target_policy is not None

    enc_res = client.get(f"/api/patients/{target_patient['id']}/encounters")
    enc_items = enc_res.json().get("items", [])
    enc_id = enc_items[0]["id"] if enc_items else None

    # Verify eligibility via Availity endpoint
    verify_payload = {
        "patient_id": target_patient["id"],
        "insurance_policy_id": target_policy["id"],
        "encounter_id": enc_id,
        "service_date": "2026-03-15",
        "scenario": "ACTIVE",
    }
    verify_res = client.post("/api/availity/eligibility/verify", json=verify_payload)
    assert verify_res.status_code == 200
    resp_data = verify_res.json()
    assert resp_data["request_status"] == "ACTIVE"
    assert resp_data["response"] is not None
    resp = resp_data["response"]
    assert resp["eligibility_status"] == "ACTIVE"
    assert resp["copay"] is not None
    assert resp["deductible"] is not None
    assert resp["deductible_remaining"] is not None
    assert resp["coinsurance"] is not None

    # Check that verification history record was written
    hist_res = client.get(f"/api/patients/{target_patient['id']}/eligibility-history")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) > 0
    assert history[0]["current_status"] == "ACTIVE"
