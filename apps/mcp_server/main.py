from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from packages.capabilities.service import CapabilityService
from packages.core.auth import PrincipalContext, PrincipalType
from packages.core.auth_service import AuthService
from packages.core.ids import make_id
from packages.explainability.service import ExplainabilityService
from packages.governance.service import GovernanceService
from packages.maintenance.service import MaintenanceService
from packages.memory.service import MemoryService
from packages.retrieval.service import RetrievalService

app = FastAPI(title="MemCortex MCP Surface", version="0.1.0")


class MCPEnvelope(BaseModel):
    actor_id: str | None = None
    actor_type: PrincipalType = PrincipalType.AGENT_IDENTITY
    request_id: str = Field(default_factory=lambda: make_id("req"))
    workspace_id: str = "default"
    namespace: str = "project"
    roles: list[str] = Field(default_factory=lambda: ["agent"])
    bearer_token: str | None = None


class ContextPayload(MCPEnvelope):
    task: str = Field(min_length=1)


class MemoryPayload(MCPEnvelope):
    query: str = Field(min_length=1)
    limit: int = 10


class OutcomePayload(MCPEnvelope):
    capability_id: str
    success: bool
    latency_ms: int = 0


def wrap_response(result: dict[str, object], request_id: str, warnings: list[str] | None = None) -> dict[str, object]:
    trace_id = result.get("trace_id") if isinstance(result, dict) else None
    return {
        "status": "ok",
        "request_id": request_id,
        "trace_id": trace_id or make_id("trace"),
        "warnings": warnings or [],
        "result": result,
    }


def authorize(payload: MCPEnvelope, permission: str, resource: str) -> None:
    if payload.bearer_token:
        principal = AuthService().principal_from_token(
            token=payload.bearer_token,
            request_id=payload.request_id,
            workspace_id=payload.workspace_id,
            namespace=payload.namespace,
        )
    else:
        if not payload.actor_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="MCP payload must include actor_id or bearer_token",
            )
        principal = PrincipalContext(
            principal_id=payload.actor_id,
            principal_type=payload.actor_type,
            roles=payload.roles,
            request_id=payload.request_id,
            workspace_id=payload.workspace_id,
            namespace=payload.namespace,
            auth_source="mcp_envelope",
        )
    decision = GovernanceService().authorize(principal=principal, permission=permission, resource=resource)
    if not decision["allow"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Policy denied {permission} on {resource}",
        )


@app.get("/resources/project-summary")
async def project_summary() -> dict[str, object]:
    return {
        "name": "MemCortex",
        "status": "bootstrap",
        "summary": "Cognitive sidecar scaffold with API, MCP, CLI, worker, and dashboard.",
    }


@app.post("/tools/resolve_context")
async def resolve_context(payload: ContextPayload) -> dict[str, object]:
    authorize(payload, "read_memory", f"context:{payload.namespace}")
    result = RetrievalService().resolve_context(
        workspace_id=payload.workspace_id,
        task=payload.task,
        namespace=payload.namespace,
        principal_id=payload.actor_id or "token.principal",
    )
    return wrap_response(result, payload.request_id)


@app.post("/tools/build_context_pack")
async def build_context_pack(payload: ContextPayload) -> dict[str, object]:
    authorize(payload, "read_memory", f"context_pack:{payload.namespace}")
    result = RetrievalService().build_context_pack(
        workspace_id=payload.workspace_id,
        task=payload.task,
        namespace=payload.namespace,
        principal_id=payload.actor_id or "token.principal",
    )
    return wrap_response(result, payload.request_id)


@app.post("/tools/search_memory")
async def search_memory(payload: MemoryPayload) -> dict[str, object]:
    authorize(payload, "read_memory", f"memory:{payload.namespace}")
    result = MemoryService().search(
        query=payload.query,
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
        limit=payload.limit,
    )
    return wrap_response(result, payload.request_id)


@app.post("/tools/get_capabilities")
async def get_capabilities(payload: ContextPayload) -> dict[str, object]:
    authorize(payload, "read_memory", f"capability:{payload.namespace}")
    result = CapabilityService().search(
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
        task=payload.task,
        limit=5,
    )
    return wrap_response(result, payload.request_id)


@app.post("/tools/recommend_capabilities")
async def recommend_capabilities(payload: ContextPayload) -> dict[str, object]:
    authorize(payload, "read_memory", f"capability:{payload.namespace}")
    result = CapabilityService().recommend(
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
        task=payload.task,
        limit=5,
    )
    return wrap_response(result, payload.request_id)


@app.post("/tools/explain_recall")
async def explain_recall(payload: MemoryPayload) -> dict[str, object]:
    authorize(payload, "read_memory", f"explain:{payload.namespace}")
    result = ExplainabilityService().explain_recall(payload.query, "mem_demo_001")
    return wrap_response(result, payload.request_id)


@app.post("/tools/report_outcome")
async def report_outcome(payload: OutcomePayload) -> dict[str, object]:
    authorize(payload, "modify_memory", f"capability:{payload.namespace}")
    result = CapabilityService().report_outcome(
        capability_id=payload.capability_id,
        success=payload.success,
        latency_ms=payload.latency_ms,
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
    )
    return wrap_response(result, payload.request_id)


@app.post("/tools/run_maintenance_job")
async def run_maintenance_job(payload: ContextPayload) -> dict[str, object]:
    authorize(payload, "execute_maintenance", f"maintenance:{payload.namespace}")
    result = await MaintenanceService().run(payload.workspace_id, payload.namespace, "semantic_promotion")
    return wrap_response(result, payload.request_id)
