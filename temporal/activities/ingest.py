from temporalio import activity

from packages.ingestion.service import IngestionService


@activity.defn(name="parse_source_activity")
async def parse_source_activity(
    workspace_id: str, path: str, namespace: str = "project"
) -> dict[str, object]:
    return IngestionService().ingest_path(workspace_id=workspace_id, path=path, namespace=namespace)
