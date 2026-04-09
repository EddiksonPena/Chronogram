from enum import StrEnum

from pydantic import BaseModel, Field


class PrincipalType(StrEnum):
    HUMAN_USER = "human_user"
    AGENT_IDENTITY = "agent_identity"
    SERVICE_ACCOUNT = "service_account"


class PrincipalContext(BaseModel):
    principal_id: str
    principal_type: PrincipalType = PrincipalType.HUMAN_USER
    roles: list[str] = Field(default_factory=lambda: ["admin"])
    request_id: str
    workspace_id: str = "default"
    namespace: str = "project"
    auth_source: str = "header"
    token_subject: str | None = None
    issuer: str | None = None
