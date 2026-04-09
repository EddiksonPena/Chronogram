from packages.core.ids import make_id


class MaintenanceService:
    def run(self, workspace_id: str, namespace: str, job_name: str) -> dict[str, object]:
        return {
            "job_id": make_id("job"),
            "job_name": job_name,
            "workspace_id": workspace_id,
            "namespace": namespace,
            "status": "queued",
            "category": "maintenance",
        }

    def repair(self, workspace_id: str, namespace: str, job_name: str) -> dict[str, object]:
        return {
            "job_id": make_id("repair"),
            "job_name": job_name,
            "workspace_id": workspace_id,
            "namespace": namespace,
            "status": "queued",
            "category": "repair",
        }

    def get_job(self, job_id: str) -> dict[str, object]:
        return {
            "job_id": job_id,
            "status": "placeholder",
            "history": ["submitted", "awaiting_worker"],
        }
