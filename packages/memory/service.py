from datetime import UTC, datetime

from packages.core.ids import make_id
from packages.core.models.contracts import Lineage, MemoryObject, TruthState
from packages.storage.db import SessionLocal
from packages.storage.repositories import create_memory, get_memory, list_memories, update_memory_status


class MemoryService:
    def search(self, query: str, workspace_id: str, namespace: str, limit: int) -> dict[str, object]:
        with SessionLocal() as session:
            stored = list_memories(session, workspace_id, namespace, query, limit)
        results = [
            {
                "memory_id": item["memory_id"],
                "title": item["title"],
                "memory_type": item["type"],
                "score": round(item["importance_score"], 2),
                "truth_state": item["truth_state"],
            }
            for item in stored
        ]
        if not results:
            results = [
                {
                    "memory_id": "mem_demo_001",
                    "title": f"Placeholder memory for '{query}'",
                    "memory_type": "semantic",
                    "score": 0.91,
                    "truth_state": TruthState.EXTRACTED,
                }
            ]
        return {"query": query, "results": results[:limit]}

    def remember_episode(
        self, workspace_id: str, namespace: str, title: str, content: str, principal_id: str
    ) -> dict[str, object]:
        episode = MemoryObject(
            memory_id=make_id("mem"),
            workspace_id=workspace_id,
            namespace=namespace,
            principal_id=principal_id,
            type="episodic",
            title=title,
            content=content,
            truth_state=TruthState.DETERMINISTIC,
            confidence=1.0,
            importance_score=0.7,
            source_ids=[],
            valid_at=datetime.now(UTC),
            lineage=Lineage(workflow="remember_episode"),
        )
        with SessionLocal() as session:
            return create_memory(session, episode)

    def upsert_fact(
        self,
        workspace_id: str,
        namespace: str,
        fact: str,
        source_ids: list[str],
        principal_id: str,
    ) -> dict[str, object]:
        memory = MemoryObject(
            memory_id=make_id("fact"),
            workspace_id=workspace_id,
            namespace=namespace,
            principal_id=principal_id,
            type="semantic",
            title="Fact",
            content=fact,
            truth_state=TruthState.EXTRACTED,
            confidence=0.86,
            importance_score=0.8,
            source_ids=source_ids,
            lineage=Lineage(workflow="upsert_fact"),
        )
        with SessionLocal() as session:
            return create_memory(session, memory)

    def store_procedure(
        self, workspace_id: str, namespace: str, title: str, content: str, principal_id: str
    ) -> dict[str, object]:
        memory = MemoryObject(
            memory_id=make_id("proc"),
            workspace_id=workspace_id,
            namespace=namespace,
            principal_id=principal_id,
            type="procedural",
            title=title,
            content=content,
            truth_state=TruthState.REINFORCED,
            confidence=0.74,
            importance_score=0.78,
            source_ids=[],
            lineage=Lineage(workflow="store_procedure"),
        )
        with SessionLocal() as session:
            return create_memory(session, memory)

    def promote(self, memory_id: str) -> dict[str, object]:
        with SessionLocal() as session:
            updated = update_memory_status(session, memory_id, TruthState.REINFORCED.value)
        return {"memory_id": memory_id, "status": "promotion_queued", "memory": updated}

    def archive(self, memory_id: str) -> dict[str, object]:
        with SessionLocal() as session:
            updated = update_memory_status(session, memory_id, TruthState.DEPRECATED.value)
        return {"memory_id": memory_id, "status": "archived", "memory": updated}

    def get(self, memory_id: str) -> dict[str, object]:
        with SessionLocal() as session:
            record = get_memory(session, memory_id)
        return record or {
            "memory_id": memory_id,
            "type": "semantic",
            "title": "Memory placeholder",
            "content": "Detailed memory lookup scaffold",
            "truth_state": TruthState.EXTRACTED,
        }
