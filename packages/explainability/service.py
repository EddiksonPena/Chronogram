from packages.core.ids import make_id
from packages.core.models.contracts import ExplainabilityReason


class ExplainabilityService:
    def explain_recall(self, query: str, target_id: str) -> dict[str, object]:
        reasons = [
            ExplainabilityReason(type="semantic_similarity", score=0.91),
            ExplainabilityReason(type="graph_relation", detail="connected to workspace graph"),
            ExplainabilityReason(type="recency", score=0.72),
        ]
        return {
            "trace_id": make_id("trace"),
            "target_id": target_id,
            "target_type": "memory",
            "query": query,
            "reasons": [reason.model_dump() for reason in reasons],
            "retrieval_path": ["query_classifier", "memory_search", "rerank", "context_pack"],
        }

    def get_trace(self, trace_id: str) -> dict[str, object]:
        return {
            "trace_id": trace_id,
            "target_id": "mem_demo_001",
            "target_type": "memory",
            "reasons": [
                {"type": "semantic_similarity", "score": 0.91},
                {"type": "salience", "score": 0.65},
            ],
            "retrieval_path": ["query_classifier", "vector_search", "graph_expand", "rerank"],
        }
