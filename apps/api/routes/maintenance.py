from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from apps.api.deps import require_permission
from packages.core.auth import PrincipalContext
from packages.maintenance.service import MaintenanceService

router = APIRouter(tags=["maintenance"])


class JobRequest(BaseModel):
    workspace_id: str = "default"
    namespace: str = "project"
    job_name: str = Field(min_length=1)


@router.post("/maintenance/run")
async def run_maintenance(
    payload: JobRequest,
    _: PrincipalContext = Depends(
        require_permission("execute_maintenance", lambda principal: f"maintenance:{principal.namespace}")
    ),
) -> dict[str, object]:
    return await MaintenanceService().run(payload.workspace_id, payload.namespace, payload.job_name)


@router.post("/repair/run")
async def run_repair(
    payload: JobRequest,
    _: PrincipalContext = Depends(
        require_permission("execute_maintenance", lambda principal: f"repair:{principal.namespace}")
    ),
) -> dict[str, object]:
    return await MaintenanceService().repair(payload.workspace_id, payload.namespace, payload.job_name)


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    _: PrincipalContext = Depends(
        require_permission("read_memory", lambda principal: f"job:{principal.namespace}")
    ),
) -> dict[str, object]:
    return MaintenanceService().get_job(job_id)


@router.get("/jobs")
async def list_jobs(
    workspace_id: str = "default",
    namespace: str = "project",
    limit: int = 10,
    _: PrincipalContext = Depends(
        require_permission("read_memory", lambda principal: f"job:{principal.namespace}")
    ),
) -> dict[str, object]:
    return {
        "items": MaintenanceService().list_jobs(workspace_id=workspace_id, namespace=namespace, limit=limit)
    }
