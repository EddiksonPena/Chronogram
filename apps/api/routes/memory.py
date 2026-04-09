from fastapi import APIRouter
from pydantic import BaseModel, Field

from packages.memory.service import MemoryService

router = APIRouter(tags=["memory"])


class MemorySearchRequest(BaseModel):
    query: str = Field(min_length=1)
    workspace_id: str = "default"
    namespace: str = "project"
    limit: int = Field(default=10, ge=1, le=50)


class EpisodeRequest(BaseModel):
    workspace_id: str = Field(min_length=1)
    namespace: str = "project"
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    principal_id: str = "local.operator"


class FactRequest(BaseModel):
    workspace_id: str = Field(min_length=1)
    namespace: str = "project"
    fact: str = Field(min_length=1)
    source_ids: list[str] = Field(default_factory=list)
    principal_id: str = "local.operator"


@router.post("/memory/search")
async def search_memory(payload: MemorySearchRequest) -> dict[str, object]:
    return MemoryService().search(
        query=payload.query,
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
        limit=payload.limit,
    )


@router.post("/memory/episodes")
async def remember_episode(payload: EpisodeRequest) -> dict[str, object]:
    return MemoryService().remember_episode(
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
        title=payload.title,
        content=payload.content,
        principal_id=payload.principal_id,
    )


@router.post("/memory/facts")
async def upsert_fact(payload: FactRequest) -> dict[str, object]:
    return MemoryService().upsert_fact(
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
        fact=payload.fact,
        source_ids=payload.source_ids,
        principal_id=payload.principal_id,
    )


@router.post("/memory/procedures")
async def store_procedure(payload: EpisodeRequest) -> dict[str, object]:
    return MemoryService().store_procedure(
        workspace_id=payload.workspace_id,
        namespace=payload.namespace,
        title=payload.title,
        content=payload.content,
        principal_id=payload.principal_id,
    )


@router.post("/memory/promote")
async def promote_memory(memory_id: str) -> dict[str, object]:
    return MemoryService().promote(memory_id)


@router.post("/memory/archive")
async def archive_memory(memory_id: str) -> dict[str, object]:
    return MemoryService().archive(memory_id)


@router.get("/memory/{memory_id}")
async def get_memory(memory_id: str) -> dict[str, object]:
    return MemoryService().get(memory_id)
