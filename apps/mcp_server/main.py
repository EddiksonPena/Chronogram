from fastapi import FastAPI
from pydantic import BaseModel, Field

from packages.capabilities.service import CapabilityService
from packages.explainability.service import ExplainabilityService
from packages.maintenance.service import MaintenanceService
from packages.memory.service import MemoryService
from packages.retrieval.service import RetrievalService

app = FastAPI(title="MemCortex MCP Surface", version="0.1.0")


class ContextPayload(BaseModel):
    workspace_id: str = Field(min_length=1)
    task: str = Field(min_length=1)
    namespace: str = "project"
    principal_id: str = "local.operator"


class MemoryPayload(BaseModel):
    query: str = Field(min_length=1)
    workspace_id: str = "default"
    namespace: str = "project"
    limit: int = 10


class OutcomePayload(BaseModel):
    capability_id: str
    success: bool
    latency_ms: int = 0
    workspace_id: str = "default"
    namespace: str = "project"


@app.get("/resources/project-summary")
async def project_summary() -> dict[str, object]:
    return {
        "name": "MemCortex",
        "status": "bootstrap",
        "summary": "Cognitive sidecar scaffold with API, MCP, CLI, worker, and dashboard.",
    }


@app.post("/tools/resolve_context")
async def resolve_context(payload: ContextPayload) -> dict[str, object]:
    return RetrievalService().resolve_context(
        workspace_id=payload.workspace_id,
        task=payload.task,
        namespace=payload.namespace,
        principal_id=payload.principal_id,
    )


@app.post("/tools/build_context_pack")
async def build_context_pack(payload: ContextPayload) -> dict[str, object]:
    return RetrievalService().build_context_pack(
        workspace_id=payload.workspace_id,
        task=payload.task,
        namespace=payload.namespace,
        principal_id=payload.principal_id,
    )


@app.post("/tools/search_memory")
async def search_memory(payload: MemoryPayload) -> dict[str, object]:
    return MemoryService().search(
        query=payload.query,
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
        limit=payload.limit,
    )


@app.post("/tools/get_capabilities")
async def get_capabilities(payload: ContextPayload) -> dict[str, object]:
    return CapabilityService().search(
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
        task=payload.task,
        limit=5,
    )


@app.post("/tools/recommend_capabilities")
async def recommend_capabilities(payload: ContextPayload) -> dict[str, object]:
    return CapabilityService().recommend(
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
        task=payload.task,
        limit=5,
    )


@app.post("/tools/explain_recall")
async def explain_recall(payload: MemoryPayload) -> dict[str, object]:
    return ExplainabilityService().explain_recall(payload.query, "mem_demo_001")


@app.post("/tools/report_outcome")
async def report_outcome(payload: OutcomePayload) -> dict[str, object]:
    return CapabilityService().report_outcome(
        capability_id=payload.capability_id,
        success=payload.success,
        latency_ms=payload.latency_ms,
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
    )


@app.post("/tools/run_maintenance_job")
async def run_maintenance_job(payload: ContextPayload) -> dict[str, object]:
    return MaintenanceService().run(payload.workspace_id, payload.namespace, "semantic_promotion")
