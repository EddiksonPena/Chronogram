from datetime import timedelta

from temporalio import workflow


@workflow.defn
class IngestSourceWorkflow:
    @workflow.run
    async def run(self, workspace_id: str, path: str, namespace: str = "project") -> dict[str, object]:
        return await workflow.execute_activity(
            "parse_source_activity",
            args=[workspace_id, path, namespace],
            start_to_close_timeout=timedelta(seconds=30),
        )
