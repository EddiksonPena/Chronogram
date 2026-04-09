from packages.capabilities.service import CapabilityService
from packages.explainability.service import ExplainabilityService
from packages.graph.service import GraphService
from packages.memory.service import MemoryService
from packages.retrieval.classifier import classify_query
from packages.vector.service import VectorService


class RetrievalService:
    def resolve_context(
        self, workspace_id: str, task: str, namespace: str, principal_id: str
    ) -> dict[str, object]:
        classification = classify_query(task)
        memory = MemoryService().search(query=task, workspace_id=workspace_id, namespace=namespace, limit=5)
        chunks = VectorService().search(workspace_id=workspace_id, namespace=namespace, query=task, limit=5)
        graph = GraphService().neighborhood(
            workspace_id=workspace_id, namespace=namespace, query=task, limit=5
        )
        capabilities = CapabilityService().recommend(
            workspace_id=workspace_id, namespace=namespace, task=task, limit=3
        )
        target_id = memory["results"][0]["memory_id"] if memory["results"] else "mem_demo_001"
        trace = ExplainabilityService().explain_recall(task, target_id)
        warnings = []
        if not chunks:
            warnings.append("Vector adapter is running in lexical fallback mode with no chunk hits.")
        if not graph:
            warnings.append("Graph neighborhood is currently sourced from control-plane metadata, not Neo4j.")
        return {
            "workspace_id": workspace_id,
            "namespace": namespace,
            "principal_id": principal_id,
            "summary": self._build_summary(task, memory["results"], chunks, graph),
            "query_classification": classification,
            "memory": memory["results"],
            "chunks": chunks,
            "graph": graph,
            "recommended_capabilities": capabilities["recommendations"],
            "warnings": warnings,
            "trace_id": trace["trace_id"],
        }

    def build_context_pack(
        self, workspace_id: str, task: str, namespace: str, principal_id: str
    ) -> dict[str, object]:
        resolved = self.resolve_context(workspace_id, task, namespace, principal_id)
        return {
            "workspace_id": workspace_id,
            "namespace": namespace,
            "principal_id": principal_id,
            "task": task,
            "summary": resolved["summary"],
            "context_pack": {
                "facts": [item for item in resolved["memory"] if item["memory_type"] == "semantic"],
                "recent_events": [item for item in resolved["memory"] if item["memory_type"] == "episodic"],
                "procedures": [item for item in resolved["memory"] if item["memory_type"] == "procedural"],
                "memories": resolved["memory"],
                "documents": resolved["chunks"],
                "graph_relationships": resolved["graph"],
                "capabilities": resolved["recommended_capabilities"],
                "confidence_summary": {
                    "memory_hits": len(resolved["memory"]),
                    "document_hits": len(resolved["chunks"]),
                    "graph_hits": len(resolved["graph"]),
                    "modes": resolved["query_classification"]["modes"],
                },
                "warnings": resolved["warnings"],
            },
            "trace_id": resolved["trace_id"],
        }

    def _build_summary(
        self,
        task: str,
        memory_results: list[dict[str, object]],
        chunk_results: list[dict[str, object]],
        graph_results: list[dict[str, object]],
    ) -> str:
        return (
            f"Context resolved for task '{task}' with "
            f"{len(memory_results)} memory hits, {len(chunk_results)} document hits, "
            f"and {len(graph_results)} graph candidates."
        )
