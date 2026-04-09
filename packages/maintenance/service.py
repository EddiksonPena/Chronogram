from temporalio.client import Client

from packages.core.ids import make_id
from packages.core.settings import settings
from packages.storage.db import SessionLocal
from packages.storage.repositories import (
    create_job,
    get_job as repo_get_job,
    list_jobs as repo_list_jobs,
    update_job,
)
from temporal.workflows.maintenance import MaintenanceWorkflow, RepairWorkflow


class MaintenanceService:
    async def run(self, workspace_id: str, namespace: str, job_name: str) -> dict[str, object]:
        with SessionLocal() as session:
            job = create_job(session, make_id("job"), job_name, "maintenance", workspace_id, namespace)
            update_job(session, job["job_id"], status="scheduled", history_entry="temporal_submission_pending")
        return await self._start_workflow(
            workflow=MaintenanceWorkflow.run,
            workflow_id=f"maintenance-{job['job_id']}",
            job=job,
            workspace_id=workspace_id,
            namespace=namespace,
            job_name=job_name,
        )

    async def repair(self, workspace_id: str, namespace: str, job_name: str) -> dict[str, object]:
        with SessionLocal() as session:
            job = create_job(session, make_id("repair"), job_name, "repair", workspace_id, namespace)
            update_job(session, job["job_id"], status="scheduled", history_entry="temporal_submission_pending")
        return await self._start_workflow(
            workflow=RepairWorkflow.run,
            workflow_id=f"repair-{job['job_id']}",
            job=job,
            workspace_id=workspace_id,
            namespace=namespace,
            job_name=job_name,
        )

    def get_job(self, job_id: str) -> dict[str, object]:
        with SessionLocal() as session:
            record = repo_get_job(session, job_id)
        return record or {
            "job_id": job_id,
            "status": "placeholder",
            "history": ["submitted", "awaiting_worker"],
        }

    def list_jobs(self, workspace_id: str, namespace: str, limit: int = 10) -> list[dict[str, object]]:
        with SessionLocal() as session:
            return repo_list_jobs(session, workspace_id, namespace, limit)

    async def _start_workflow(
        self,
        *,
        workflow,
        workflow_id: str,
        job: dict[str, object],
        workspace_id: str,
        namespace: str,
        job_name: str,
    ) -> dict[str, object]:
        try:
            client = await Client.connect(settings.temporal_host, namespace=settings.temporal_namespace)
            handle = await client.start_workflow(
                workflow,
                args=[job["job_id"], workspace_id, namespace, job_name],
                id=workflow_id,
                task_queue=settings.temporal_task_queue,
            )
            with SessionLocal() as session:
                stored = update_job(session, job["job_id"], status="running", history_entry=f"workflow:{handle.id}")
            return {
                **(stored or job),
                "execution_mode": "temporal",
                "workflow_id": handle.id,
                "workflow_run_id": handle.result_run_id,
            }
        except Exception:
            with SessionLocal() as session:
                stored = update_job(
                    session,
                    job["job_id"],
                    status="queued",
                    history_entry="temporal_unavailable_fallback",
                )
            return {
                **(stored or job),
                "execution_mode": "degraded",
                "warning": "Temporal unavailable; job recorded but not executed by workflow",
            }
