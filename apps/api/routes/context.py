from fastapi import APIRouter
from pydantic import BaseModel, Field

from packages.retrieval.service import RetrievalService

router = APIRouter(tags=["context"])


class ResolveContextRequest(BaseModel):
    workspace_id: str = Field(min_length=1)
    task: str = Field(min_length=1)
    namespace: str = "project"
    principal_id: str = "local.operator"


@router.post("/context/resolve")
async def resolve_context(payload: ResolveContextRequest) -> dict[str, object]:
    service = RetrievalService()
    return service.resolve_context(
        workspace_id=payload.workspace_id,
        task=payload.task,
        namespace=payload.namespace,
        principal_id=payload.principal_id,
    )


@router.post("/context/packs/build")
async def build_context_pack(payload: ResolveContextRequest) -> dict[str, object]:
    service = RetrievalService()
    return service.build_context_pack(
        workspace_id=payload.workspace_id,
        task=payload.task,
        namespace=payload.namespace,
        principal_id=payload.principal_id,
    )
