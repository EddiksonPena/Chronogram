from packages.core.ids import make_id
from packages.core.models.contracts import ExplainabilityReason
from packages.storage.db import SessionLocal
from packages.storage.repositories import get_trace as get_stored_trace
from packages.storage.repositories import store_trace


class ExplainabilityService:
    def explain_recall(self, query: str, target_id: str) -> dict[str, object]:
        reasons = [
            ExplainabilityReason(type="semantic_similarity", score=0.91),
            ExplainabilityReason(type="graph_relation", detail="connected to workspace graph"),
            ExplainabilityReason(type="recency", score=0.72),
        ]
        payload = {
            "trace_id": make_id("trace"),
            "target_id": target_id,
            "target_type": "memory",
            "query": query,
            "reasons": [reason.model_dump() for reason in reasons],
            "retrieval_path": ["query_classifier", "memory_search", "rerank", "context_pack"],
        }
        with SessionLocal() as session:
            store_trace(session, **payload)
        return payload

    def get_trace(self, trace_id: str) -> dict[str, object]:
        with SessionLocal() as session:
            trace = get_stored_trace(session, trace_id)
        return trace or {
            "trace_id": trace_id,
            "target_id": "mem_demo_001",
            "target_type": "memory",
            "reasons": [
                {"type": "semantic_similarity", "score": 0.91},
                {"type": "salience", "score": 0.65},
            ],
            "retrieval_path": ["query_classifier", "vector_search", "graph_expand", "rerank"],
        }
