export type MemoryType =
  | "working"
  | "episodic"
  | "semantic"
  | "procedural"
  | "graph";

export type MemoryScope =
  | "session"
  | "agent"
  | "user"
  | "workspace"
  | "global";

export interface Provenance {
  source: string;
  sourceId?: string;
  observedAt: string;
  ingestedAt: string;
}

export interface MemoryArtifact {
  id: string;
  type: MemoryType;
  scope: MemoryScope;
  content: string;
  summary?: string;
  confidence: number;
  tags: string[];
  provenance: Provenance;
  linkedArtifactIds: string[];
  modelVersion?: string;
  createdAt: string;
  updatedAt: string;
  salience?: number;
  reinforcementCount?: number;
  lastAccessedAt?: string;
  metadata?: Record<string, string | number | boolean>;
}

export interface IngestMemoryRequest {
  scope: MemoryScope;
  content: string;
  source: string;
  sourceId?: string;
  observedAt?: string;
  tags?: string[];
  typeHint?: MemoryType;
  sessionId?: string;
}

export interface IngestMemoryResponse {
  memoryId: string;
  accepted: boolean;
  deduplicated: boolean;
  artifactsCreated: number;
  chunksCreated: number;
  entitiesExtracted: number;
  storedIn: string[];
}

export interface RecallMemoryRequest {
  query: string;
  scope?: MemoryScope;
  memoryTypes?: MemoryType[];
  limit?: number;
  includeDiagnostics?: boolean;
  sessionId?: string;
}

export interface RecallCandidate {
  artifactId: string;
  score: number;
  source: "vector" | "sparse" | "graph" | "working";
  reasoning: string;
}

export interface RecallMemoryResponse {
  query: string;
  context: MemoryArtifact[];
  candidates: RecallCandidate[];
  diagnostics?: {
    storesQueried: string[];
    reranked: boolean;
    totalCandidates?: number;
    queryEntities?: string[];
    appliedScope?: MemoryScope | "all";
    elapsedMs?: number;
  };
}

export interface ConversationTurn {
  role: "system" | "user" | "assistant" | "tool";
  content: string;
  createdAt?: string;
}

export interface CompactionCandidate {
  moduleId: "semantic" | "episodic" | "procedural";
  content: string;
  score: number;
  reason: string;
  tags: string[];
}

export interface CompactConversationRequest {
  scope: MemoryScope;
  messages: ConversationTurn[];
  sessionId?: string;
  conversationId?: string;
  currentWindowTokens?: number;
  maxWindowTokens?: number;
  occupancyRatio?: number;
  thresholdRatio?: number;
  force?: boolean;
}

export interface CompactConversationResponse {
  triggered: boolean;
  reason: string;
  occupancyRatio: number;
  workingSummary: string;
  openLoops: string[];
  discardedMessageCount: number;
  promoted: {
    episodic: string[];
    semantic: string[];
    procedural: string[];
  };
  candidates: CompactionCandidate[];
}

export interface FeedbackMemoryRequest {
  artifactId: string;
  useful: boolean;
  notes?: string;
}

export interface FeedbackMemoryResponse {
  artifactId: string;
  updated: boolean;
  reinforcementCount: number;
  salience: number;
}

export interface MemoryHealth {
  status: "ok";
  persistenceFile: string;
  artifactCount: number;
  chunkCount: number;
  graphNodeCount: number;
  graphEdgeCount: number;
}

export interface ReindexResponse {
  accepted: boolean;
  artifactsProcessed: number;
  chunksRecomputed: number;
  graphNodesRecomputed: number;
}

export interface ModuleObservabilitySnapshot {
  moduleId: "semantic" | "episodic" | "procedural";
  artifactCount: number;
  chunkCount: number;
  ingestCount: number;
  deduplicatedCount: number;
  artifactWriteCount: number;
  chunkWriteCount: number;
  recallQueryCount: number;
  recallHitCount: number;
  feedbackCount: number;
  positiveFeedbackCount: number;
  workflowScheduledCount: number;
  workflowCompletedCount: number;
  workflowFailedCount: number;
  averageIngestLatencyMs: number;
  averageRecallLatencyMs: number;
  lastActivityAt?: string;
}

export interface WorkerHeartbeat {
  service: "memory-api" | "worker";
  status: "ok";
  timestamp: string;
}
