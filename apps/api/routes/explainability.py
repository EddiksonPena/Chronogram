from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from apps.api.deps import require_permission
from packages.core.auth import PrincipalContext
from packages.explainability.service import ExplainabilityService

router = APIRouter(tags=["explainability"])


class ExplainRecallRequest(BaseModel):
    query: str = Field(min_length=1)
    target_id: str = Field(min_length=1)


@router.post("/explain/recall")
async def explain_recall(
    payload: ExplainRecallRequest,
    _: PrincipalContext = Depends(
        require_permission("read_memory", lambda principal: f"explain:{principal.namespace}")
    ),
) -> dict[str, object]:
    return ExplainabilityService().explain_recall(payload.query, payload.target_id)


@router.get("/explain/trace/{trace_id}")
async def get_trace(
    trace_id: str,
    _: PrincipalContext = Depends(
        require_permission("read_memory", lambda principal: f"explain:{principal.namespace}")
    ),
) -> dict[str, object]:
    return ExplainabilityService().get_trace(trace_id)
