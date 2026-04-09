from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

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

    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "default"
    temporal_task_queue: str = "brain-runtime"

    keycloak_url: str = "http://localhost:8081"
    keycloak_realm: str = "brain-runtime"
    keycloak_client_id: str = "brain-api"
    keycloak_client_secret: str = "change-me"

    opa_url: str = "http://localhost:8181"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
