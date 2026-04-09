from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from apps.api.deps import require_permission
from packages.core.auth import PrincipalContext
from packages.governance.service import GovernanceService
from packages.harness.service import HarnessService

router = APIRouter(tags=["admin"])


class PolicyRequest(BaseModel):
    principal_id: str = Field(min_length=1)
    resource: str = Field(min_length=1)
    action: str = Field(min_length=1)
    workspace_id: str = "default"
    namespace: str = "project"


@router.get("/metrics/summary")
async def metrics_summary(
    _: PrincipalContext = Depends(
        require_permission("read_memory", lambda principal: f"metrics:{principal.namespace}")
    ),
) -> dict[str, object]:
    return GovernanceService().metrics_summary()


@router.get("/policies/decisions")
async def list_policy_decisions(
    workspace_id: str = "default",
    namespace: str = "project",
    limit: int = 10,
    _: PrincipalContext = Depends(
        require_permission("manage_policies", lambda principal: f"policy:{principal.namespace}")
    ),
) -> dict[str, object]:
    return {
        "items": GovernanceService().list_policy_decisions(
            workspace_id=workspace_id,
            namespace=namespace,
            limit=limit,
        )
    }


@router.post("/policies/evaluate")
async def evaluate_policy(
    payload: PolicyRequest,
    _: PrincipalContext = Depends(
        require_permission("manage_policies", lambda principal: f"policy:{principal.namespace}")
    ),
) -> dict[str, object]:
    return GovernanceService().evaluate(
        principal_id=payload.principal_id,
        resource=payload.resource,
        action=payload.action,
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
    )


@router.get("/harness/targets")
async def harness_targets(
    _: PrincipalContext = Depends(
        require_permission("read_memory", lambda principal: f"harness:{principal.namespace}")
    ),
) -> dict[str, object]:
    return HarnessService().list_targets()


@router.get("/harness/status")
async def harness_status(
    _: PrincipalContext = Depends(
        require_permission("read_memory", lambda principal: f"harness:{principal.namespace}")
    ),
) -> dict[str, object]:
    return HarnessService().status()
