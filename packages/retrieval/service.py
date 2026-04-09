from packages.capabilities.service import CapabilityService
from packages.explainability.service import ExplainabilityService
from packages.memory.service import MemoryService


class RetrievalService:
    def resolve_context(
        self, workspace_id: str, task: str, namespace: str, principal_id: str
    ) -> dict[str, object]:
        memory = MemoryService().search(query=task, workspace_id=workspace_id, namespace=namespace, limit=5)
        capabilities = CapabilityService().recommend(
            workspace_id=workspace_id, namespace=namespace, task=task, limit=3
        )
        trace = ExplainabilityService().explain_recall(task, "mem_demo_001")
        return {
            "workspace_id": workspace_id,
            "namespace": namespace,
            "principal_id": principal_id,
            "summary": f"Context resolved for task: {task}",
            "memory": memory["results"],
            "recommended_capabilities": capabilities["recommendations"],
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
                "memories": resolved["memory"],
                "capabilities": resolved["recommended_capabilities"],
                "warnings": ["Policy and persistence layers are scaffolded but not yet connected to backing stores."],
            },
            "trace_id": resolved["trace_id"],
        }
