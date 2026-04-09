from fastapi import APIRouter
from pydantic import BaseModel, Field

from packages.capabilities.service import CapabilityService

router = APIRouter(tags=["capabilities"])


class CapabilityRequest(BaseModel):
    workspace_id: str = "default"
    namespace: str = "project"
    task: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=25)


class OutcomeRequest(BaseModel):
    capability_id: str = Field(min_length=1)
    success: bool
    latency_ms: int = Field(ge=0)
    workspace_id: str = "default"
    namespace: str = "project"


@router.post("/capabilities/search")
async def search_capabilities(payload: CapabilityRequest) -> dict[str, object]:
    return CapabilityService().search(
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
        task=payload.task,
        limit=payload.limit,
    )


@router.post("/capabilities/recommend")
async def recommend_capabilities(payload: CapabilityRequest) -> dict[str, object]:
    return CapabilityService().recommend(
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
        task=payload.task,
        limit=payload.limit,
    )


@router.get("/capabilities/{capability_id}")
async def get_capability(capability_id: str) -> dict[str, object]:
    return CapabilityService().get(capability_id)


@router.post("/capabilities/outcomes")
async def report_capability_outcome(payload: OutcomeRequest) -> dict[str, object]:
    return CapabilityService().report_outcome(
        capability_id=payload.capability_id,
        success=payload.success,
        latency_ms=payload.latency_ms,
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
    )
