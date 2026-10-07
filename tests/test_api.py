from codestra_agentmail.config import get_settings
from codestra_agentmail.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def setup_function() -> None:
    get_settings.cache_clear()


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_send_is_denied_by_default() -> None:
    response = client.post(
        "/v1/inboxes/demo/messages:send",
        json={
            "tenant_id": "tenant-test",
            "actor_id": "actor-test",
            "to": ["qa@example.com"],
            "subject": "Test",
            "text": "Test",
            "idempotency_key": "test-key-0001",
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "effect_denied"
