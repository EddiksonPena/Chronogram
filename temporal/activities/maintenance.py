from temporalio import activity

from packages.capabilities.service import CapabilityService
from packages.core.models.contracts import TruthState
from packages.memory.service import MemoryService
from packages.storage.db import SessionLocal
from packages.storage.repositories import capability_metrics, list_memories, update_job


def _mark_job(job_id: str, status: str, history_entry: str) -> dict[str, object] | None:
    with SessionLocal() as session:
        return update_job(session, job_id, status=status, history_entry=history_entry)


@activity.defn(name="semantic_promotion_activity")
async def semantic_promotion_activity(job_id: str, workspace_id: str, namespace: str) -> dict[str, object]:
    _mark_job(job_id, "running", "semantic_promotion_started")
    promoted = 0
    with SessionLocal() as session:
        memories = list_memories(session, workspace_id=workspace_id, namespace=namespace, query="", limit=100)
    for memory in memories:
        if memory["truth_state"] in {TruthState.EXTRACTED.value, TruthState.INFERRED.value}:
            MemoryService().promote(memory["memory_id"])
            promoted += 1
    _mark_job(job_id, "running", f"semantic_promotion_promoted:{promoted}")
    return {"step": "semantic_promotion", "promoted": promoted}


@activity.defn(name="procedural_promotion_activity")
async def procedural_promotion_activity(job_id: str, workspace_id: str, namespace: str) -> dict[str, object]:
    _mark_job(job_id, "running", "procedural_promotion_started")
    recommendations = CapabilityService().recommend(
        workspace_id=workspace_id,
        namespace=namespace,
        task="maintenance procedural promotion",
        limit=5,
    )
    promoted = len(recommendations)
    _mark_job(job_id, "running", f"procedural_promotion_candidates:{promoted}")
    return {
        "step": "procedural_promotion",
        "recommended_capabilities": [cap["capability_id"] for cap in recommendations],
    }


@activity.defn(name="summarization_activity")
async def summarization_activity(job_id: str, workspace_id: str, namespace: str) -> dict[str, object]:
    _mark_job(job_id, "running", "summarization_started")
    search = MemoryService().search(query="", workspace_id=workspace_id, namespace=namespace, limit=20)
    episode_count = len(search.get("results", []))
    summary = f"Maintenance summarized {episode_count} memory items for {workspace_id}/{namespace}."
    created = MemoryService().remember_episode(
        workspace_id=workspace_id,
        namespace=namespace,
        title="Maintenance summary",
        content=summary,
        principal_id="system.maintenance",
    )
    _mark_job(job_id, "running", f"summarization_created:{created['memory_id']}")
    return {"step": "summarization", "summary_memory_id": created["memory_id"], "episode_count": episode_count}


@activity.defn(name="repair_activity")
async def repair_activity(job_id: str, workspace_id: str, namespace: str) -> dict[str, object]:
    _mark_job(job_id, "running", "repair_started")
    with SessionLocal() as session:
        metrics = capability_metrics(session)
    degraded = [
        capability_id
        for capability_id, values in metrics.items()
        if values.get("success_rate", 0.0) < 0.5 and values.get("total_runs", 0.0) >= 1.0
    ]
    _mark_job(job_id, "running", f"repair_degraded_capabilities:{len(degraded)}")
    return {"step": "repair", "degraded_capabilities": degraded}


@activity.defn(name="complete_job_activity")
async def complete_job_activity(job_id: str, status: str, history_entry: str) -> dict[str, object] | None:
    return _mark_job(job_id, status, history_entry)
