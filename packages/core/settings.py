import os
import sys

from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_file() -> str | None:
    if "DATABASE_URL" in os.environ:
        return ".env"
    if any("pytest" in arg for arg in sys.argv[:2]):
        return None
    return ".env"


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    database_url: str = "sqlite:///./memcortex.db"
    api_url: str = "http://localhost:8000"
    mcp_server_url: str = "http://localhost:8100"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "brain_runtime"
    postgres_user: str = "brain"
    postgres_password: str = "brain"

    redis_host: str = "localhost"
    redis_port: int = 6379

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password12345"

    weaviate_url: str = "http://localhost:8080"
    weaviate_collection_name: str = "MemCortexChunk"

    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "default"
    temporal_task_queue: str = "brain-runtime"

    keycloak_url: str = "http://localhost:8081"
    keycloak_realm: str = "brain-runtime"
    keycloak_client_id: str = "brain-api"
    keycloak_client_secret: str = "change-me"
    keycloak_audience: str | None = None
    keycloak_jwks_url: str | None = None
    auth_allow_header_fallback: bool = True

    opa_url: str = "http://localhost:8181"
    opa_policy_package: str = "memcortex/authz"
    opa_timeout_seconds: float = 2.0
    enable_opa_authorization: bool = True

    model_config = SettingsConfigDict(env_file=_env_file(), extra="ignore")


settings = Settings()
