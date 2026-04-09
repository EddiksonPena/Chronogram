import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from packages.core.settings import settings
from temporal.activities.ingest import parse_source_activity
from temporal.workflows.ingest import IngestSourceWorkflow


async def main() -> None:
    client = await Client.connect(settings.temporal_host, namespace=settings.temporal_namespace)
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[IngestSourceWorkflow],
        activities=[parse_source_activity],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
