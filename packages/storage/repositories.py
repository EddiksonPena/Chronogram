from datetime import UTC, datetime

from sqlalchemy import Integer, func, select
from sqlalchemy.orm import Session

from packages.core.models.contracts import CapabilityObject, MemoryObject
from packages.storage.models import (
    CapabilityOutcomeRecord,
    CapabilityRecord,
    ChunkRecord,
    ExplainabilityTraceRecord,
    JobRecordModel,
    MemoryRecord,
    PolicyDecisionRecord,
    SourceRecord,
)


def upsert_source(session: Session, payload: dict[str, object]) -> dict[str, object]:
    record = session.get(SourceRecord, payload["source_id"])
    if record is None:
        session.add(SourceRecord(**payload))
    else:
        for key, value in payload.items():
            setattr(record, key, value)
        record.updated_at = datetime.now(UTC)
    session.commit()
    return payload


def replace_chunks(
    session: Session,
    source_id: str,
    workspace_id: str,
    namespace: str,
    content_class: str,
    chunks: list[dict[str, object]],
) -> list[dict[str, object]]:
    existing = session.scalars(select(ChunkRecord).where(ChunkRecord.source_id == source_id)).all()
    for record in existing:
        session.delete(record)
    for chunk in chunks:
        session.add(
            ChunkRecord(
                chunk_id=chunk["chunk_id"],
                source_id=source_id,
                workspace_id=workspace_id,
                namespace=namespace,
                content_class=content_class,
                chunk_kind=chunk.get("chunk_kind", "lexical"),
                text=chunk["text"],
                chunk_order=chunk["order"],
                chunk_metadata=chunk.get("metadata", {}),
            )
        )
    session.commit()
    return search_chunks(session, workspace_id, namespace, "", limit=len(chunks))


def create_memory(session: Session, memory: MemoryObject) -> dict[str, object]:
    session.add(MemoryRecord(**memory.model_dump()))
    session.commit()
    return memory.model_dump(mode="json")


def search_chunks(
    session: Session, workspace_id: str, namespace: str, query: str, limit: int
) -> list[dict[str, object]]:
    statement = select(ChunkRecord).where(
        ChunkRecord.workspace_id == workspace_id,
        ChunkRecord.namespace == namespace,
    )
    if query:
        statement = statement.where(ChunkRecord.text.ilike(f"%{query}%"))
    statement = statement.order_by(ChunkRecord.chunk_order.asc()).limit(limit)
    return [
        {
            "chunk_id": record.chunk_id,
            "source_id": record.source_id,
            "text": record.text,
            "content_class": record.content_class,
            "chunk_kind": record.chunk_kind,
            "order": record.chunk_order,
            "metadata": record.chunk_metadata,
        }
        for record in session.scalars(statement).all()
    ]


def graph_candidates(
    session: Session, workspace_id: str, namespace: str, query: str, limit: int
) -> list[dict[str, object]]:
    source_matches = session.scalars(
        select(SourceRecord)
        .where(SourceRecord.workspace_id == workspace_id, SourceRecord.namespace == namespace)
        .where(
            (SourceRecord.path.ilike(f"%{query}%"))
            | (SourceRecord.content_class.ilike(f"%{query}%"))
            | (SourceRecord.source_type.ilike(f"%{query}%"))
        )
        .limit(limit)
    ).all()
    return [
        {
            "node_id": record.source_id,
            "node_type": "source",
            "path": record.path,
            "content_class": record.content_class,
            "relationships": ["workspace", "namespace", "chunks"],
        }
        for record in source_matches
    ]


def list_memories(
    session: Session, workspace_id: str, namespace: str, query: str, limit: int
) -> list[dict[str, object]]:
    statement = (
        select(MemoryRecord)
        .where(MemoryRecord.workspace_id == workspace_id, MemoryRecord.namespace == namespace)
        .where((MemoryRecord.title.ilike(f"%{query}%")) | (MemoryRecord.content.ilike(f"%{query}%")))
        .order_by(MemoryRecord.updated_at.desc())
        .limit(limit)
    )
    return [_memory_record_to_dict(record) for record in session.scalars(statement).all()]


def get_memory(session: Session, memory_id: str) -> dict[str, object] | None:
    record = session.get(MemoryRecord, memory_id)
    return None if record is None else _memory_record_to_dict(record)


def update_memory_status(session: Session, memory_id: str, truth_state: str) -> dict[str, object] | None:
    record = session.get(MemoryRecord, memory_id)
    if record is None:
        return None
    record.truth_state = truth_state
    record.updated_at = datetime.now(UTC)
    session.commit()
    return _memory_record_to_dict(record)


def seed_capabilities(session: Session, capabilities: list[CapabilityObject]) -> None:
    for capability in capabilities:
        if session.get(CapabilityRecord, capability.capability_id) is None:
            session.add(CapabilityRecord(**capability.model_dump()))
    session.commit()


def list_capabilities(session: Session, workspace_id: str, namespace: str) -> list[dict[str, object]]:
    statement = (
        select(CapabilityRecord)
        .where(
            CapabilityRecord.workspace_id.in_([workspace_id, "global"]),
            CapabilityRecord.namespace.in_([namespace, "global"]),
        )
        .order_by(CapabilityRecord.reliability_score.desc(), CapabilityRecord.name.asc())
    )
    return [_capability_record_to_dict(record) for record in session.scalars(statement).all()]


def get_capability(session: Session, capability_id: str) -> dict[str, object] | None:
    record = session.get(CapabilityRecord, capability_id)
    return None if record is None else _capability_record_to_dict(record)


def create_capability_outcome(
    session: Session,
    outcome_id: str,
    capability_id: str,
    workspace_id: str,
    namespace: str,
    success: bool,
    latency_ms: int,
) -> dict[str, object]:
    session.add(
        CapabilityOutcomeRecord(
            outcome_id=outcome_id,
            capability_id=capability_id,
            workspace_id=workspace_id,
            namespace=namespace,
            success=success,
            latency_ms=latency_ms,
        )
    )
    session.commit()
    return {
        "outcome_id": outcome_id,
        "capability_id": capability_id,
        "workspace_id": workspace_id,
        "namespace": namespace,
        "success": success,
        "latency_ms": latency_ms,
    }


def capability_metrics(session: Session) -> dict[str, dict[str, float]]:
    statement = select(
        CapabilityOutcomeRecord.capability_id,
        func.count().label("total"),
        func.sum(func.cast(CapabilityOutcomeRecord.success, Integer)).label("successes"),
        func.avg(CapabilityOutcomeRecord.latency_ms).label("avg_latency"),
    ).group_by(CapabilityOutcomeRecord.capability_id)
    metrics: dict[str, dict[str, float]] = {}
    for row in session.execute(statement):
        total = row.total or 0
        successes = row.successes or 0
        metrics[row.capability_id] = {
            "success_rate": float(successes / total) if total else 0.0,
            "avg_latency_ms": float(row.avg_latency or 0.0),
            "total_runs": float(total),
        }
    return metrics


def create_job(
    session: Session, job_id: str, job_name: str, category: str, workspace_id: str, namespace: str
) -> dict[str, object]:
    record = JobRecordModel(
        job_id=job_id,
        job_name=job_name,
        category=category,
        workspace_id=workspace_id,
        namespace=namespace,
        status="queued",
        history=["queued"],
    )
    session.add(record)
    session.commit()
    return _job_record_to_dict(record)


def get_job(session: Session, job_id: str) -> dict[str, object] | None:
    record = session.get(JobRecordModel, job_id)
    return None if record is None else _job_record_to_dict(record)


def update_job(
    session: Session,
    job_id: str,
    *,
    status: str | None = None,
    history_entry: str | None = None,
) -> dict[str, object] | None:
    record = session.get(JobRecordModel, job_id)
    if record is None:
        return None
    if status is not None:
        record.status = status
    if history_entry is not None:
        record.history = [*record.history, history_entry]
    record.updated_at = datetime.now(UTC)
    session.commit()
    return _job_record_to_dict(record)


def list_jobs(session: Session, workspace_id: str, namespace: str, limit: int = 10) -> list[dict[str, object]]:
    statement = (
        select(JobRecordModel)
        .where(JobRecordModel.workspace_id == workspace_id, JobRecordModel.namespace == namespace)
        .order_by(JobRecordModel.submitted_at.desc())
        .limit(limit)
    )
    return [_job_record_to_dict(record) for record in session.scalars(statement).all()]


def store_trace(
    session: Session,
    trace_id: str,
    target_id: str,
    target_type: str,
    query: str | None,
    reasons: list[dict[str, object]],
    retrieval_path: list[str],
) -> dict[str, object]:
    session.merge(
        ExplainabilityTraceRecord(
            trace_id=trace_id,
            target_id=target_id,
            target_type=target_type,
            query=query,
            reasons=reasons,
            retrieval_path=retrieval_path,
        )
    )
    session.commit()
    return {
        "trace_id": trace_id,
        "target_id": target_id,
        "target_type": target_type,
        "query": query,
        "reasons": reasons,
        "retrieval_path": retrieval_path,
    }


def get_trace(session: Session, trace_id: str) -> dict[str, object] | None:
    record = session.get(ExplainabilityTraceRecord, trace_id)
    if record is None:
        return None
    return {
        "trace_id": record.trace_id,
        "target_id": record.target_id,
        "target_type": record.target_type,
        "query": record.query,
        "reasons": record.reasons,
        "retrieval_path": record.retrieval_path,
        "generated_at": record.generated_at.isoformat(),
    }


def store_policy_decision(
    session: Session,
    principal_id: str,
    resource: str,
    action: str,
    workspace_id: str,
    namespace: str,
    allow: bool,
    policy_source: str,
) -> dict[str, object]:
    record = PolicyDecisionRecord(
        principal_id=principal_id,
        resource=resource,
        action=action,
        workspace_id=workspace_id,
        namespace=namespace,
        allow=allow,
        policy_source=policy_source,
    )
    session.add(record)
    session.commit()
    return {
        "decision_id": record.decision_id,
        "principal_id": principal_id,
        "resource": resource,
        "action": action,
        "workspace_id": workspace_id,
        "namespace": namespace,
        "allow": allow,
        "policy_source": policy_source,
    }


def list_policy_decisions(
    session: Session, workspace_id: str, namespace: str, limit: int = 10
) -> list[dict[str, object]]:
    statement = (
        select(PolicyDecisionRecord)
        .where(PolicyDecisionRecord.workspace_id == workspace_id, PolicyDecisionRecord.namespace == namespace)
        .order_by(PolicyDecisionRecord.created_at.desc())
        .limit(limit)
    )
    return [
        {
            "decision_id": record.decision_id,
            "principal_id": record.principal_id,
            "resource": record.resource,
            "action": record.action,
            "workspace_id": record.workspace_id,
            "namespace": record.namespace,
            "allow": record.allow,
            "policy_source": record.policy_source,
            "created_at": record.created_at.isoformat(),
        }
        for record in session.scalars(statement).all()
    ]


def metrics_summary(session: Session) -> dict[str, object]:
    return {
        "memory_count": session.scalar(select(func.count()).select_from(MemoryRecord)) or 0,
        "chunk_count": session.scalar(select(func.count()).select_from(ChunkRecord)) or 0,
        "capability_count": session.scalar(select(func.count()).select_from(CapabilityRecord)) or 0,
        "maintenance_jobs": session.scalar(select(func.count()).select_from(JobRecordModel)) or 0,
        "policy_decisions": session.scalar(select(func.count()).select_from(PolicyDecisionRecord)) or 0,
        "source_count": session.scalar(select(func.count()).select_from(SourceRecord)) or 0,
    }


def _memory_record_to_dict(record: MemoryRecord) -> dict[str, object]:
    return {
        "memory_id": record.memory_id,
        "workspace_id": record.workspace_id,
        "namespace": record.namespace,
        "principal_id": record.principal_id,
        "type": record.type,
        "title": record.title,
        "content": record.content,
        "truth_state": record.truth_state,
        "confidence": record.confidence,
        "importance_score": record.importance_score,
        "source_ids": record.source_ids,
        "valid_at": record.valid_at.isoformat() if record.valid_at else None,
        "invalid_at": record.invalid_at.isoformat() if record.invalid_at else None,
        "lineage": record.lineage,
    }


def _capability_record_to_dict(record: CapabilityRecord) -> dict[str, object]:
    return {
        "capability_id": record.capability_id,
        "workspace_id": record.workspace_id,
        "namespace": record.namespace,
        "type": record.type,
        "name": record.name,
        "version": record.version,
        "description": record.description,
        "dependencies": record.dependencies,
        "trigger_conditions": record.trigger_conditions,
        "reliability_score": record.reliability_score,
        "success_rate": record.success_rate,
        "truth_state": record.truth_state,
        "source_ids": record.source_ids,
    }


def _job_record_to_dict(record: JobRecordModel) -> dict[str, object]:
    return {
        "job_id": record.job_id,
        "job_name": record.job_name,
        "category": record.category,
        "workspace_id": record.workspace_id,
        "namespace": record.namespace,
        "status": record.status,
        "history": record.history,
        "submitted_at": record.submitted_at.isoformat(),
    }
