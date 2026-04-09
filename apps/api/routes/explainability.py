from fastapi import APIRouter
from pydantic import BaseModel, Field

from packages.explainability.service import ExplainabilityService

router = APIRouter(tags=["explainability"])


class ExplainRecallRequest(BaseModel):
    query: str = Field(min_length=1)
    target_id: str = Field(min_length=1)


@router.post("/explain/recall")
async def explain_recall(payload: ExplainRecallRequest) -> dict[str, object]:
    return ExplainabilityService().explain_recall(payload.query, payload.target_id)


@router.get("/explain/trace/{trace_id}")
async def get_trace(trace_id: str) -> dict[str, object]:
    return ExplainabilityService().get_trace(trace_id)
