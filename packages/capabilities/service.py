from packages.core.ids import make_id
from packages.core.models.contracts import CapabilityObject, TruthState
from packages.storage.db import SessionLocal
from packages.storage.repositories import (
    capability_metrics,
    create_capability_outcome,
    get_capability,
    list_capabilities,
    seed_capabilities,
)


class CapabilityService:
    def _catalog(self, workspace_id: str, namespace: str) -> list[CapabilityObject]:
        return [
            CapabilityObject(
                capability_id="cap_resolve_context",
                workspace_id=workspace_id,
                namespace=namespace,
                type="workflow_template",
                name="Resolve context",
                version="0.1.0",
                description="Assemble a context pack before planning and execution.",
                dependencies=["search_memory", "recommend_capabilities"],
                trigger_conditions=["planning", "context", "recall"],
                reliability_score=0.91,
                success_rate=0.93,
                truth_state=TruthState.REINFORCED,
            ),
            CapabilityObject(
                capability_id="cap_ingest_repo",
                workspace_id=workspace_id,
                namespace=namespace,
                type="workflow_template",
                name="Ingest repository",
                version="0.1.0",
                description="Run deterministic parsing and provisional graph writes over a repo path.",
                dependencies=["ingest_source", "parse_python"],
                trigger_conditions=["ingest", "repo", "index"],
                reliability_score=0.84,
                success_rate=0.89,
                truth_state=TruthState.REINFORCED,
            ),
        ]

    def seed_defaults(self) -> None:
        with SessionLocal() as session:
            seed_capabilities(session, self._catalog("global", "global"))

    def search(self, workspace_id: str, namespace: str, task: str, limit: int) -> dict[str, object]:
        with SessionLocal() as session:
            catalog = list_capabilities(session, workspace_id, namespace)
            if not catalog:
                seed_capabilities(session, self._catalog("global", "global"))
                catalog = list_capabilities(session, workspace_id, namespace)
        matches = [
            item
            for item in catalog
            if any(
                token in f"{item['name']} {item['description']}".lower()
                for token in task.lower().split()
            )
        ] or catalog
        return {
            "query": task,
            "results": matches[:limit],
        }

    def recommend(
        self, workspace_id: str, namespace: str, task: str, limit: int
    ) -> dict[str, object]:
        with SessionLocal() as session:
            catalog = list_capabilities(session, workspace_id, namespace)
            if not catalog:
                seed_capabilities(session, self._catalog("global", "global"))
                catalog = list_capabilities(session, workspace_id, namespace)
            metrics = capability_metrics(session)
        recommendations = []
        for item in catalog[:limit]:
            metric = metrics.get(item["capability_id"], {})
            recommendations.append(
                {
                    "capability_id": item["capability_id"],
                    "name": item["name"],
                    "score": round(float(item["reliability_score"]), 2),
                    "reason": f"Recommended for task '{task}' based on trigger and reliability match.",
                    "success_rate": metric.get("success_rate", item["success_rate"]),
                }
            )
        return {"task": task, "recommendations": recommendations}

    def get(self, capability_id: str) -> dict[str, object]:
        with SessionLocal() as session:
            record = get_capability(session, capability_id)
        return record or {
            "capability_id": capability_id,
            "status": "known" if capability_id.startswith("cap_") else "placeholder",
            "description": "Capability lookup scaffold",
        }

    def report_outcome(
        self,
        capability_id: str,
        success: bool,
        latency_ms: int,
        workspace_id: str,
        namespace: str,
    ) -> dict[str, object]:
        outcome_id = make_id("outcome")
        with SessionLocal() as session:
            record = create_capability_outcome(
                session,
                outcome_id=outcome_id,
                capability_id=capability_id,
                workspace_id=workspace_id,
                namespace=namespace,
                success=success,
                latency_ms=latency_ms,
            )
        record["status"] = "recorded"
        return record
