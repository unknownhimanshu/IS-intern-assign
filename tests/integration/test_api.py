from fastapi.testclient import TestClient

from agentctl.api.main import app


def test_health_endpoints():
    client = TestClient(app)
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").json() == {"status": "ready"}
