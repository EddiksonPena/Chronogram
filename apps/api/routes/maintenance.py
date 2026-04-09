from fastapi import APIRouter
from pydantic import BaseModel, Field

from packages.maintenance.service import MaintenanceService

router = APIRouter(tags=["maintenance"])


class JobRequest(BaseModel):
    workspace_id: str = "default"
    namespace: str = "project"
    job_name: str = Field(min_length=1)


@router.post("/maintenance/run")
async def run_maintenance(payload: JobRequest) -> dict[str, object]:
    return MaintenanceService().run(payload.workspace_id, payload.namespace, payload.job_name)


@router.post("/repair/run")
async def run_repair(payload: JobRequest) -> dict[str, object]:
    return MaintenanceService().repair(payload.workspace_id, payload.namespace, payload.job_name)


@router.get("/jobs/{job_id}")
async def get_job(job_id: str) -> dict[str, object]:
    return MaintenanceService().get_job(job_id)
