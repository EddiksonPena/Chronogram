from fastapi import APIRouter

from packages.core.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "app_env": settings.app_env,
        "services": {
            "postgres": settings.postgres_host,
            "redis": settings.redis_host,
            "neo4j": settings.neo4j_uri,
            "weaviate": settings.weaviate_url,
            "temporal": settings.temporal_host,
            "opa": settings.opa_url,
            "keycloak": settings.keycloak_url,
        },
    }
