from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from apps.api.deps import require_permission
from packages.core.auth import PrincipalContext
from packages.retrieval.service import RetrievalService

router = APIRouter(tags=["context"])


class ResolveContextRequest(BaseModel):
    workspace_id: str = Field(min_length=1)
    task: str = Field(min_length=1)
    namespace: str = "project"
    principal_id: str = "local.operator"


@router.post("/context/resolve")
async def resolve_context(
    payload: ResolveContextRequest,
    principal: PrincipalContext = Depends(
        require_permission("read_memory", lambda principal: f"context:{principal.namespace}")
    ),
) -> dict[str, object]:
    service = RetrievalService()
    return service.resolve_context(
        workspace_id=payload.workspace_id,
        task=payload.task,
        namespace=payload.namespace,
        principal_id=principal.principal_id,
    )


@router.post("/context/packs/build")
async def build_context_pack(
    payload: ResolveContextRequest,
    principal: PrincipalContext = Depends(
        require_permission("read_memory", lambda principal: f"context_pack:{principal.namespace}")
    ),
) -> dict[str, object]:
    service = RetrievalService()
    return service.build_context_pack(
        workspace_id=payload.workspace_id,
        task=payload.task,
        namespace=payload.namespace,
        principal_id=principal.principal_id,
    )
