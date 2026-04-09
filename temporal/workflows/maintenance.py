from datetime import timedelta

from temporalio import workflow


@workflow.defn
class MaintenanceWorkflow:
    @workflow.run
    async def run(self, job_id: str, workspace_id: str, namespace: str, job_name: str) -> dict[str, object]:
        steps: list[dict[str, object]] = []
        try:
            if job_name in {"semantic_promotion", "full_maintenance"}:
                steps.append(
                    await workflow.execute_activity(
                        "semantic_promotion_activity",
                        args=[job_id, workspace_id, namespace],
                        start_to_close_timeout=timedelta(seconds=30),
                    )
                )
            if job_name in {"procedural_promotion", "full_maintenance"}:
                steps.append(
                    await workflow.execute_activity(
                        "procedural_promotion_activity",
                        args=[job_id, workspace_id, namespace],
                        start_to_close_timeout=timedelta(seconds=30),
                    )
                )
            if job_name in {"summarization", "full_maintenance", "semantic_promotion"}:
                steps.append(
                    await workflow.execute_activity(
                        "summarization_activity",
                        args=[job_id, workspace_id, namespace],
                        start_to_close_timeout=timedelta(seconds=30),
                    )
                )
            await workflow.execute_activity(
                "complete_job_activity",
                args=[job_id, "completed", "workflow_completed"],
                start_to_close_timeout=timedelta(seconds=10),
            )
        except Exception:
            await workflow.execute_activity(
                "complete_job_activity",
                args=[job_id, "failed", "workflow_failed"],
                start_to_close_timeout=timedelta(seconds=10),
            )
            raise
        return {"job_id": job_id, "job_name": job_name, "status": "completed", "steps": steps}


@workflow.defn
class RepairWorkflow:
    @workflow.run
    async def run(self, job_id: str, workspace_id: str, namespace: str, job_name: str) -> dict[str, object]:
        try:
            result = await workflow.execute_activity(
                "repair_activity",
                args=[job_id, workspace_id, namespace],
                start_to_close_timeout=timedelta(seconds=30),
            )
            await workflow.execute_activity(
                "complete_job_activity",
                args=[job_id, "completed", "repair_completed"],
                start_to_close_timeout=timedelta(seconds=10),
            )
        except Exception:
            await workflow.execute_activity(
                "complete_job_activity",
                args=[job_id, "failed", "repair_failed"],
                start_to_close_timeout=timedelta(seconds=10),
            )
            raise
        return {"job_id": job_id, "job_name": job_name, "status": "completed", "steps": [result]}
