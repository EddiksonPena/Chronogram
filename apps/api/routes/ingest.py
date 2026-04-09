from fastapi import APIRouter
from pydantic import BaseModel, Field

from packages.ingestion.service import IngestionService

router = APIRouter(tags=["ingest"])


class IngestSourceRequest(BaseModel):
    path: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    namespace: str = "project"
    principal_id: str = "local.operator"


class IngestDiffRequest(BaseModel):
    git_ref: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    namespace: str = "project"


@router.post("/ingest/source")
async def ingest_source(payload: IngestSourceRequest) -> dict[str, object]:
    return IngestionService().ingest_path(
        workspace_id=payload.workspace_id,
        path=payload.path,
        namespace=payload.namespace,
        principal_id=payload.principal_id,
    )


@router.post("/ingest/repo")
async def ingest_repo(payload: IngestSourceRequest) -> dict[str, object]:
    return IngestionService().ingest_repository(
        workspace_id=payload.workspace_id,
        path=payload.path,
        namespace=payload.namespace,
        principal_id=payload.principal_id,
    )


@router.post("/ingest/git-diff")
async def ingest_diff(payload: IngestDiffRequest) -> dict[str, object]:
    return {
        "workspace_id": payload.workspace_id,
        "namespace": payload.namespace,
        "git_ref": payload.git_ref,
        "status": "not_implemented",
    }


@router.post("/ingest/skill")
async def ingest_skill(payload: IngestSourceRequest) -> dict[str, object]:
    result = IngestionService().ingest_path(
        workspace_id=payload.workspace_id,
        path=payload.path,
        namespace=payload.namespace,
        principal_id=payload.principal_id,
    )
    result["source"]["source_type"] = "skill"
    return result


@router.post("/ingest/mcp")
async def ingest_mcp(payload: IngestSourceRequest) -> dict[str, object]:
    result = IngestionService().ingest_path(
        workspace_id=payload.workspace_id,
        path=payload.path,
        namespace=payload.namespace,
        principal_id=payload.principal_id,
    )
    result["source"]["source_type"] = "mcp_definition"
    return result
