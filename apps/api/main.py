from contextlib import asynccontextmanager

from fastapi import FastAPI

from apps.api.routes.admin import router as admin_router
from apps.api.routes.capabilities import router as capabilities_router
from apps.api.routes.context import router as context_router
from apps.api.routes.explainability import router as explainability_router
from apps.api.routes.health import router as health_router
from apps.api.routes.ingest import router as ingest_router
from apps.api.routes.maintenance import router as maintenance_router
from apps.api.routes.memory import router as memory_router
from packages.capabilities.service import CapabilityService
from packages.storage.db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    CapabilityService().seed_defaults()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="MemCortex API", version="0.1.0", lifespan=lifespan)
    app.include_router(health_router, prefix="/v1")
    app.include_router(context_router, prefix="/v1")
    app.include_router(memory_router, prefix="/v1")
    app.include_router(ingest_router, prefix="/v1")
    app.include_router(capabilities_router, prefix="/v1")
    app.include_router(explainability_router, prefix="/v1")
    app.include_router(maintenance_router, prefix="/v1")
    app.include_router(admin_router, prefix="/v1")
    return app


app = create_app()
