import asyncio

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.mcp_server.main import app as mcp_app
from packages.core.auth import PrincipalContext, PrincipalType
from packages.core.auth_service import AuthService
from packages.maintenance.service import MaintenanceService
from packages.storage.db import init_db


init_db()
client = TestClient(app)
mcp_client = TestClient(mcp_app)


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


def test_memory_round_trip() -> None:
    created = client.post(
        "/v1/memory/episodes",
        json={
            "workspace_id": "proj_alpha",
            "title": "Initial design choice",
            "content": "We selected Codex-first integration for v1.",
        },
    )
    assert created.status_code == 200
    memory_id = created.json()["memory_id"]

    fetched = client.get(f"/v1/memory/{memory_id}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Initial design choice"


def test_reader_cannot_write_memory() -> None:
    response = client.post(
        "/v1/memory/episodes",
        headers={
            "x-principal-id": "guest.reader",
            "x-principal-roles": "reader",
            "x-request-id": "req_test_1",
        },
        json={
            "workspace_id": "proj_alpha",
            "title": "Blocked write",
            "content": "A reader should not be able to write memory.",
        },
    )
    assert response.status_code == 403


def test_mcp_response_shape() -> None:
    response = mcp_client.post(
        "/tools/resolve_context",
        json={
            "actor_id": "agent.codex",
            "roles": ["agent"],
            "request_id": "req_mcp_1",
            "workspace_id": "proj_alpha",
            "namespace": "project",
            "task": "summarize repository state",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["request_id"] == "req_mcp_1"
    assert "result" in body


def test_bearer_token_authentication(monkeypatch) -> None:
    def fake_principal_from_token(
        self,
        token: str,
        request_id: str | None = None,
        workspace_id: str | None = None,
        namespace: str | None = None,
    ) -> PrincipalContext:
        assert token == "signed-token"
        return PrincipalContext(
            principal_id="kc.alice",
            principal_type=PrincipalType.HUMAN_USER,
            roles=["admin"],
            request_id=request_id or "req_token",
            workspace_id=workspace_id or "proj_alpha",
            namespace=namespace or "project",
            auth_source="bearer",
            token_subject="user-123",
            issuer="http://keycloak.test/realms/brain-runtime",
        )

    monkeypatch.setattr(AuthService, "_principal_from_token", fake_principal_from_token)

    response = client.post(
        "/v1/context/resolve",
        headers={"Authorization": "Bearer signed-token", "x-request-id": "req_bearer_1"},
        json={"workspace_id": "proj_alpha", "task": "resolve token-backed context"},
    )
    assert response.status_code == 200
    assert response.json()["workspace_id"] == "proj_alpha"


def test_mcp_bearer_token_authentication(monkeypatch) -> None:
    def fake_principal_from_token(
        self,
        token: str,
        request_id: str | None = None,
        workspace_id: str | None = None,
        namespace: str | None = None,
    ) -> PrincipalContext:
        assert token == "mcp-token"
        return PrincipalContext(
            principal_id="agent.keycloak",
            principal_type=PrincipalType.AGENT_IDENTITY,
            roles=["agent"],
            request_id=request_id or "req_mcp_token",
            workspace_id=workspace_id or "proj_alpha",
            namespace=namespace or "project",
            auth_source="bearer",
        )

    monkeypatch.setattr(AuthService, "_principal_from_token", fake_principal_from_token)

    response = mcp_client.post(
        "/tools/resolve_context",
        json={
            "bearer_token": "mcp-token",
            "request_id": "req_mcp_token_1",
            "workspace_id": "proj_alpha",
            "namespace": "project",
            "task": "summarize repository state",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_harness_admin_endpoints() -> None:
    targets = client.get("/v1/harness/targets")
    assert targets.status_code == 200
    assert any(item["target"] == "codex" for item in targets.json()["targets"])

    status = client.get("/v1/harness/status")
    assert status.status_code == 200
    assert "targets" in status.json()


class _FakeWorkflowHandle:
    id = "maintenance-job-123"
    result_run_id = "run-123"


class _FakeTemporalClient:
    async def start_workflow(self, *args, **kwargs):
        return _FakeWorkflowHandle()


async def _fake_connect_success(*args, **kwargs):
    return _FakeTemporalClient()


async def _fake_connect_failure(*args, **kwargs):
    raise RuntimeError("temporal offline")


def test_maintenance_run_uses_temporal_when_available(monkeypatch) -> None:
    monkeypatch.setattr("packages.maintenance.service.Client.connect", _fake_connect_success)

    result = asyncio.run(MaintenanceService().run("proj_alpha", "project", "semantic_promotion"))

    assert result["execution_mode"] == "temporal"
    assert result["status"] == "running"
    assert result["workflow_id"] == "maintenance-job-123"


def test_maintenance_run_degrades_when_temporal_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("packages.maintenance.service.Client.connect", _fake_connect_failure)

    result = asyncio.run(MaintenanceService().run("proj_alpha", "project", "semantic_promotion"))

    assert result["execution_mode"] == "degraded"
    assert result["status"] == "queued"
    assert "warning" in result
