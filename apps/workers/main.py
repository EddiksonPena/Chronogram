import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from packages.core.settings import settings
from temporal.activities.ingest import parse_source_activity
from temporal.activities.maintenance import (
    complete_job_activity,
    procedural_promotion_activity,
    repair_activity,
    semantic_promotion_activity,
    summarization_activity,
)
from temporal.workflows.ingest import IngestSourceWorkflow
from temporal.workflows.maintenance import MaintenanceWorkflow, RepairWorkflow


async def main() -> None:
    client = await Client.connect(settings.temporal_host, namespace=settings.temporal_namespace)
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[IngestSourceWorkflow, MaintenanceWorkflow, RepairWorkflow],
        activities=[
            parse_source_activity,
            semantic_promotion_activity,
            procedural_promotion_activity,
            summarization_activity,
            repair_activity,
            complete_job_activity,
        ],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
