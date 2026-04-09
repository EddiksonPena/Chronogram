from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TruthState(StrEnum):
    DETERMINISTIC = "deterministic"
    EXTRACTED = "extracted"
    INFERRED = "inferred"
    AMBIGUOUS = "ambiguous"
    REINFORCED = "reinforced"
    VERIFIED = "verified"
    CONFLICTING = "conflicting"
    DEPRECATED = "deprecated"


class Lineage(BaseModel):
    model: str | None = None
    workflow: str | None = None
    version: str | None = None


class BaseContract(BaseModel):
    namespace: str
    workspace_id: str
    principal_id: str = "local.operator"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SourceEnvelope(BaseContract):
    source_id: str
    source_type: str
    content_class: str
    path: str | None = None
    raw_content_ref: str | None = None
    content_hash: str | None = None
    mime_type: str | None = None
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MemoryObject(BaseContract):
    memory_id: str
    type: str
    title: str
    content: str
    truth_state: TruthState
    confidence: float
    importance_score: float
    source_ids: list[str] = Field(default_factory=list)
    valid_at: datetime | None = None
    invalid_at: datetime | None = None
    lineage: Lineage = Field(default_factory=Lineage)


class CapabilityObject(BaseContract):
    capability_id: str
    type: str
    name: str
    version: str
    description: str
    dependencies: list[str] = Field(default_factory=list)
    trigger_conditions: list[str] = Field(default_factory=list)
    reliability_score: float = 0.0
    success_rate: float = 0.0
    truth_state: TruthState = TruthState.REINFORCED
    source_ids: list[str] = Field(default_factory=list)


class ExplainabilityReason(BaseModel):
    type: str
    score: float | None = None
    detail: str | None = None


class ExplainabilityRecord(BaseModel):
    trace_id: str
    target_id: str
    target_type: str
    reasons: list[ExplainabilityReason]
    retrieval_path: list[str]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class JobRecord(BaseModel):
    job_id: str
    job_name: str
    status: str
    workspace_id: str
    namespace: str
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PolicyDecision(BaseModel):
    principal_id: str
    resource: str
    action: str
    workspace_id: str
    namespace: str
    allow: bool
    policy_source: str
