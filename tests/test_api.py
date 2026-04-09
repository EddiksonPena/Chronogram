from fastapi.testclient import TestClient

from apps.api.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "services" in body


def test_context_resolution() -> None:
    response = client.post(
        "/v1/context/resolve",
        json={"workspace_id": "proj_alpha", "task": "index the repository"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["workspace_id"] == "proj_alpha"
    assert body["recommended_capabilities"]


def test_policy_evaluation() -> None:
    response = client.post(
        "/v1/policies/evaluate",
        json={
            "principal_id": "guest.user",
            "resource": "memory:project",
            "action": "read",
        },
    )
    assert response.status_code == 200
    assert response.json()["allow"] is True
