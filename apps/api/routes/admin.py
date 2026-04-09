from fastapi import APIRouter
from pydantic import BaseModel, Field

from packages.governance.service import GovernanceService

router = APIRouter(tags=["admin"])


class PolicyRequest(BaseModel):
    principal_id: str = Field(min_length=1)
    resource: str = Field(min_length=1)
    action: str = Field(min_length=1)
    workspace_id: str = "default"
    namespace: str = "project"


@router.get("/metrics/summary")
async def metrics_summary() -> dict[str, object]:
    return GovernanceService().metrics_summary()


@router.post("/policies/evaluate")
async def evaluate_policy(payload: PolicyRequest) -> dict[str, object]:
    return GovernanceService().evaluate(
        principal_id=payload.principal_id,
        resource=payload.resource,
        action=payload.action,
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
    )
