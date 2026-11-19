from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_integrations_status_has_no_availity() -> None:
    response = client.get("/api/integrations/status")
    assert response.status_code == 200
    body = response.json()
    assert body["availity"]["enabled"] is False
    assert body["eligibility_provider"]["active"] in {"mock", "MOCK_AVAILITY"}
    assert "hapi.fhir.org" in body["ehr"]["hapi_fhir"]["base_url"]


def test_health_endpoint_shape() -> None:
    """Health should always return JSON; DB may be degraded if Postgres is down."""
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "degraded"}
    assert "database" in body
    assert "connected" in body["database"]
    assert body["app"]
