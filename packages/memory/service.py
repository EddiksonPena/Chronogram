from datetime import UTC, datetime

from packages.core.ids import make_id
from packages.core.models.contracts import Lineage, MemoryObject, TruthState


class MemoryService:
    def search(self, query: str, workspace_id: str, namespace: str, limit: int) -> dict[str, object]:
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
        return episode.model_dump(mode="json")

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
        return memory.model_dump(mode="json")

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
        return memory.model_dump(mode="json")

    def promote(self, memory_id: str) -> dict[str, object]:
        return {"memory_id": memory_id, "status": "promotion_queued"}

    def archive(self, memory_id: str) -> dict[str, object]:
        return {"memory_id": memory_id, "status": "archived"}

    def get(self, memory_id: str) -> dict[str, object]:
        return {
            "memory_id": memory_id,
            "type": "semantic",
            "title": "Memory placeholder",
            "content": "Detailed memory lookup scaffold",
            "truth_state": TruthState.EXTRACTED,
        }
