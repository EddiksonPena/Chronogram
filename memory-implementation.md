Brain Runtime Build Kit

Purpose

A complete build package for creating a local-first, open-source, plug-and-play cognitive brain for coding agent harnesses such as Codex and Claude Code.

Product definition

Brain Runtime is a sidecar cognition system for agent harnesses. It provides:
	•	hybrid memory: episodic, semantic, procedural, working, emotional, implicit, spatial/temporal
	•	capability intelligence: skills, tools, MCP servers, registries, workflows, prompts
	•	context orchestration: global, project, session, agent, team
	•	control plane: identity, governance, observability, explainability, repair, operator UX
	•	progressive intelligence: background consolidation, compression, repair, reranking, promotion

Core design principles
	1.	Local-first and self-hostable
	2.	Harness-agnostic integration via API + CLI + MCP + SDK
	3.	Graph-first ingestion before semantic enrichment
	4.	Deterministic extraction before LLM extraction
	5.	Multi-strategy chunking as a first-class subsystem
	6.	Temporal graph memory for evolving truth
	7.	Raw memory preserved; derived memory versioned
	8.	Context packs instead of raw dump retrieval
	9.	Explainability and policy built in, not bolted on
	10.	Continuous cognitive maintenance loop

⸻

1. System architecture

1.1 High-level architecture

Coding Harness (Codex / Claude Code / custom)
  ├─ prompts
  ├─ tools
  ├─ subagents
  ├─ file edits
  └─ runtime execution
          │
          ▼
Brain Runtime Sidecar
  ├─ API Gateway
  ├─ MCP Server
  ├─ CLI
  ├─ SDK
  ├─ Context Service
  ├─ Memory Service
  ├─ Capability Service
  ├─ Retrieval Router
  ├─ Ingestion Engine
  ├─ Consolidation Engine
  ├─ Governance Service
  ├─ Explainability Service
  ├─ Observability Service
  ├─ Repair Service
  └─ Operator UI
          │
          ▼
Storage Layer
  ├─ Neo4j + Graphiti
  ├─ Vector DB
  ├─ Redis / LangCache
  ├─ Postgres
  └─ Blob store / filesystem

1.2 Core planes

Cognitive plane
	•	working memory
	•	episodic memory
	•	semantic memory
	•	procedural memory
	•	emotional memory
	•	implicit pattern memory
	•	spatial/temporal graph memory

Control plane
	•	identity
	•	governance
	•	observability
	•	explainability
	•	repair
	•	audit

Experience plane
	•	CLI
	•	REST API
	•	MCP tools/resources
	•	Python/TypeScript SDK
	•	operator dashboard

⸻

2. Recommended stack

2.1 Required core stack
	•	API backend: FastAPI
	•	Workflow orchestration: Temporal
	•	Graph DB: Neo4j
	•	Temporal graph layer: Graphiti
	•	Vector DB: Weaviate or Chroma
	•	Cache / hot memory: Redis
	•	Relational control DB: Postgres
	•	Identity: Keycloak
	•	Policy engine: OPA
	•	Observability: OpenTelemetry + Grafana OSS
	•	Queue / events: Temporal-native first; optional NATS later
	•	Frontend: Next.js + React + Tailwind + shadcn/ui
	•	Container orchestration: Docker Compose for MVP, Kubernetes later
	•	Blob/doc storage: local filesystem or MinIO

2.2 Language choices
	•	Primary backend language: Python
	•	SDKs: Python first, TypeScript second
	•	Frontend: TypeScript

2.3 Models

Default local model roles
	•	embedding model
	•	reranker model
	•	extractor/summarizer model
	•	sentiment/salience model

Model abstraction contract

Every model adapter should expose:
	•	embed(texts)
	•	rerank(query, candidates)
	•	extract_facts(text)
	•	extract_relations(text)
	•	summarize(text)
	•	score_salience(text, metadata)

⸻

3. Memory model

3.1 Memory types

Working memory
	•	active task state
	•	recent tool outputs
	•	current repo context
	•	TTL-based
	•	stored in Redis + ephemeral DB tables

Episodic memory
	•	conversations
	•	execution traces
	•	task outcomes
	•	decisions
	•	corrections
	•	timestamps, actors, outcomes

Semantic memory
	•	normalized facts
	•	preferences
	•	glossary
	•	architecture truths
	•	extracted stable knowledge

Procedural memory
	•	steps
	•	runbooks
	•	workflows
	•	skill instructions
	•	MCP/tool usage patterns

Emotional memory
	•	salience
	•	criticality
	•	frustration/success markers
	•	recurrence intensity
	•	user emphasis signals

Implicit memory
	•	latent patterns
	•	repeated query-task mappings
	•	successful tool combinations
	•	recurring repo behaviors

Spatial / temporal memory
	•	graph relationships
	•	evolving facts over time
	•	provenance chains
	•	entity neighborhoods
	•	event transitions

3.2 Memory lifecycle

captured → enriched → active → reinforced → stale → compressed → archived → deleted

3.3 Truth states

deterministic
extracted
inferred
ambiguous
reinforced
verified
conflicting
deprecated


⸻

4. Capability model

4.1 Capability object types
	•	skill
	•	tool
	•	MCP server
	•	registry entry
	•	workflow template
	•	command recipe
	•	prompt template
	•	rule pack
	•	agent profile
	•	context pack

4.2 Capability schema

Each capability object should include:
	•	id
	•	type
	•	name
	•	description
	•	version
	•	source
	•	namespace
	•	tags
	•	dependencies
	•	trigger conditions
	•	required permissions
	•	recommended contexts
	•	reliability score
	•	success history
	•	cost/latency hints
	•	confidence
	•	provenance
	•	model lineage

4.3 Namespaces
	•	global
	•	project
	•	session
	•	agent
	•	team
	•	system

⸻

5. Graphify-inspired ingestion engine

5.1 Mission

Perform deterministic extraction first, build a provisional graph second, apply selective semantic enrichment third, then route enriched outputs into graph, vector, and memory stores.

5.2 Pipeline stages

Stage 0: source capture

Normalize raw source into canonical envelope.

Stage 1: source classification

Classify input as code, doc, transcript, config, skill, MCP manifest, tool schema, log, image metadata, etc.

Stage 2: deterministic extraction

Extract structure without LLMs:
	•	AST
	•	imports
	•	functions
	•	classes
	•	markdown headings
	•	YAML/JSON keys
	•	speaker turns
	•	timestamps
	•	links
	•	config refs
	•	schemas

Stage 3: provisional graph build

Create graph skeleton with certainty=deterministic.

Stage 4: ambiguity detection

Identify what actually needs semantic enrichment.

Stage 5: selective enrichment

Run models only where ambiguity or semantic value exists:
	•	facts
	•	relationships
	•	procedures
	•	events
	•	salience
	•	contradictions

Stage 6: chunking policy engine

Apply one or more chunking strategies based on source type and memory goal.

Stage 7: storage routing

Write to graph / vector / episodic / semantic / procedural / cache.

Stage 8: workflow emission

Trigger downstream Temporal workflows.

5.3 Chunking strategies
	•	semantic boundary
	•	structural
	•	sliding window
	•	hierarchical
	•	topic-based
	•	event-based
	•	entity-centric
	•	temporal
	•	intent-based
	•	procedural
	•	graph-aware
	•	multiview

5.4 Source-specific policies

Code
	•	AST extraction
	•	symbol chunking
	•	dependency graphing
	•	procedure extraction for commands/test flows

Docs
	•	structural + semantic chunking
	•	section summaries
	•	entity extraction

Conversations
	•	speaker-turn chunking
	•	event chunking
	•	temporal graph update
	•	preference/fact extraction

Skills / MCPs / tools
	•	schema extraction
	•	dependency graphing
	•	procedural chunking
	•	capability scoring

⸻

6. Retrieval architecture

6.1 Retrieval router

Classify each query into one or more retrieval modes:
	•	working/contextual
	•	episodic
	•	semantic
	•	procedural
	•	graph
	•	temporal
	•	capability recommendation
	•	explainability

6.2 Retrieval flow

Query
 → classify intent
 → fetch context pack candidates
 → route across cache / vector / graph / procedural / semantic
 → fuse results
 → rerank
 → build explainability trace
 → return context pack

6.3 Context packs

A context pack is a curated bundle for a task or workspace.
It may contain:
	•	task summary
	•	relevant facts
	•	recent episodes
	•	procedures
	•	recommended tools
	•	recommended MCPs
	•	rules/policies
	•	warnings
	•	graph neighborhood
	•	confidence summary

⸻

7. Cognitive maintenance loop

7.1 Mission

Continuously improve robustness, conciseness, and quality of the brain.

7.2 Always-on jobs

Fast cadence
	•	working memory cleanup
	•	cache expiry and warmup
	•	salience refresh
	•	duplicate collapse

Medium cadence
	•	episodic→semantic promotion
	•	episodic→procedural promotion
	•	hierarchical summarization
	•	capability reranking

Deep cadence
	•	contradiction analysis
	•	graph repair
	•	re-embedding
	•	chunk regeneration after policy/model change
	•	entity merge repair
	•	procedure quality review

7.3 Safety rules
	•	raw memory preserved by default
	•	all derived artifacts versioned
	•	high-impact rewrites require approval threshold
	•	dry-run mode for destructive changes
	•	full lineage retained

⸻

8. Identity, governance, observability, explainability, repair, operator UX

8.1 Identity

Goals
	•	authenticate humans, agents, and services
	•	isolate namespaces
	•	attach ownership and audit to memory operations

Principals
	•	human_user
	•	agent_identity
	•	service_account
	•	workspace
	•	namespace

Minimum permissions
	•	read_memory
	•	write_memory
	•	write_semantic
	•	write_procedural
	•	approve_changes
	•	delete_archive
	•	view_sensitive
	•	manage_policies
	•	run_repairs

8.2 Governance

Policies
	•	retention
	•	sensitivity tagging
	•	long-term promotion rules
	•	overwrite rules
	•	summarization eligibility
	•	archive rules
	•	tenant isolation
	•	capability usage policies

Memory flags
	•	active
	•	stale
	•	conflicting
	•	protected
	•	pinned
	•	low_confidence
	•	superseded
	•	sensitive

8.3 Observability

Telemetry to collect
	•	ingestion latency
	•	workflow durations
	•	graph write failures
	•	cache hit rate
	•	retrieval latency
	•	contradiction rate
	•	summary fidelity score
	•	chunk counts by strategy
	•	memory growth by namespace
	•	capability recommendation success

8.4 Explainability

For every retrieved memory or recommended capability expose:
	•	why selected
	•	source/provenance
	•	confidence
	•	truth state
	•	recency
	•	salience
	•	retrieval path
	•	graph relation trace
	•	model lineage

8.5 Repair tooling

Repair jobs
	•	duplicate merge
	•	orphan cleanup
	•	graph reconciliation
	•	stale fact review
	•	summary regeneration
	•	re-embedding
	•	provenance repair
	•	chunk regeneration
	•	capability metadata repair

8.6 Operator UX

Dashboard views
	•	Overview
	•	Memory Explorer
	•	Graph View
	•	Timelines
	•	Jobs
	•	Policies
	•	Models
	•	Sources
	•	Explainability
	•	Admin

Key actions
	•	re-run ingestion
	•	trigger summarization
	•	re-embed namespace
	•	repair graph
	•	archive candidates preview
	•	restore archived memory
	•	merge entities
	•	pin/promote/demote memory

⸻

9. Harness integration design

9.1 Integration stance

The brain is a sidecar cognition runtime, not the harness itself.

9.2 Integration surfaces

API

For structured system-to-system access.

CLI

For operators and harness bootstrapping.

MCP server

For harness-native tool access.

SDK

For custom deep integrations.

9.3 Brain contract

Required primitives
	•	resolve_context()
	•	search_memory()
	•	remember_episode()
	•	upsert_fact()
	•	get_capabilities()
	•	recommend_capabilities()
	•	get_procedure()
	•	build_context_pack()
	•	explain_recall()
	•	report_outcome()
	•	list_policies()
	•	run_maintenance_job()

9.4 Harness lifecycle

Boot
	•	identify project
	•	authenticate principal
	•	load global + project context
	•	return recommended capabilities

Plan
	•	retrieve similar episodes
	•	fetch procedures
	•	recommend tools/MCPs/skills
	•	assemble task context pack

Execute
	•	stream important events
	•	attach memory on demand
	•	score capability usage
	•	update working memory

Consolidate
	•	store episode
	•	extract facts/procedures
	•	update graph
	•	schedule maintenance

Maintain
	•	background jobs optimize memory and capability quality

9.5 Codex / Claude alignment
	•	Codex is suited for long-horizon engineering work and its CLI/app server model supports external orchestration and harness-level controls. Official docs also describe sandbox defaults like limited write scope and no network by default in some environments. These constraints mean Brain Runtime should behave as an external sidecar service with explicit APIs rather than assuming unrestricted in-process access. (openai.com￼)
	•	Claude Code supports hooks and MCP integrations, which aligns directly with exposing Brain Runtime as an MCP server plus deterministic pre/post action hooks for context resolution and writeback. Anthropic also documents plugin configuration across skills, agents, hooks, and MCP servers. (docs.anthropic.com￼)

⸻

10. Repository layout

brain-runtime/
├─ apps/
│  ├─ api/                         # FastAPI app
│  ├─ mcp-server/                  # MCP server surface
│  ├─ cli/                         # Typer-based CLI
│  ├─ dashboard/                   # Next.js operator UI
│  └─ workers/                     # Temporal workers
├─ packages/
│  ├─ core/                        # domain models, contracts, utilities
│  ├─ memory/                      # memory services
│  ├─ capabilities/                # skills/tools/MCP registries
│  ├─ ingestion/                   # graph-first ingestion engine
│  ├─ retrieval/                   # routing, reranking, fusion
│  ├─ governance/                  # policy adapters, access checks
│  ├─ identity/                    # auth adapters, principal models
│  ├─ explainability/              # provenance and recall traces
│  ├─ observability/               # tracing, metrics, logging
│  ├─ repair/                      # repair jobs
│  ├─ maintenance/                 # consolidation engine
│  ├─ graph/                       # Neo4j / Graphiti adapters
│  ├─ vector/                      # Weaviate/Chroma adapters
│  ├─ cache/                       # Redis adapters
│  ├─ models/                      # embedding/reranker/extractor adapters
│  ├─ sdk-python/
│  └─ sdk-ts/
├─ temporal/
│  ├─ workflows/
│  ├─ activities/
│  └─ schedules/
├─ configs/
│  ├─ app/
│  ├─ policies/
│  ├─ chunking/
│  ├─ prompts/
│  ├─ models/
│  └─ dashboards/
├─ infra/
│  ├─ docker/
│  ├─ compose/
│  ├─ k8s/
│  ├─ keycloak/
│  ├─ opa/
│  └─ grafana/
├─ docs/
│  ├─ architecture/
│  ├─ api/
│  ├─ mcp/
│  ├─ sdk/
│  ├─ runbooks/
│  └─ decisions/
├─ examples/
│  ├─ codex/
│  ├─ claude-code/
│  ├─ repo-ingestion/
│  └─ memory-recall/
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  ├─ e2e/
│  └─ evals/
├─ scripts/
├─ .env.example
├─ docker-compose.yml
├─ Makefile
├─ pyproject.toml
├─ package.json
└─ README.md


⸻

11. Domain schemas

11.1 Source envelope

{
  "source_id": "src_001",
  "workspace_id": "proj_alpha",
  "namespace": "project",
  "source_type": "repository_file",
  "content_class": "source_code",
  "path": "src/router.py",
  "raw_content_ref": "blob://...",
  "content_hash": "sha256:...",
  "mime_type": "text/x-python",
  "ingested_at": "2026-04-08T12:00:00Z"
}

11.2 Memory object

{
  "memory_id": "mem_001",
  "type": "episodic",
  "namespace": "project",
  "title": "Embedding backend changed",
  "content": "Team switched from Chroma to Weaviate for multimodal retrieval.",
  "truth_state": "extracted",
  "confidence": 0.88,
  "importance_score": 0.83,
  "source_ids": ["src_104"],
  "valid_at": "2026-04-08T12:30:00Z",
  "invalid_at": null,
  "created_by": "agent.codex",
  "lineage": {
    "model": "extractor-v2",
    "workflow": "semantic_promotion_workflow"
  }
}

11.3 Capability object

{
  "capability_id": "skill_debug_mcp",
  "type": "skill",
  "name": "Debug MCP connectivity",
  "namespace": "global",
  "version": "0.1.0",
  "description": "Diagnose and repair MCP registration/auth issues.",
  "dependencies": ["tool_shell", "mcp_runtime"],
  "trigger_conditions": ["mcp", "connection error", "tool unavailable"],
  "success_rate": 0.92,
  "reliability_score": 0.87,
  "truth_state": "reinforced",
  "source_ids": ["src_skill_01"]
}

11.4 Explainability record

{
  "trace_id": "trace_123",
  "target_id": "mem_001",
  "target_type": "memory",
  "reasons": [
    {"type": "semantic_similarity", "score": 0.91},
    {"type": "graph_relation", "detail": "connected to project memory graph"},
    {"type": "recency", "score": 0.72},
    {"type": "salience", "score": 0.84}
  ],
  "retrieval_path": ["cache_miss", "vector_search", "graph_expand", "rerank"],
  "generated_at": "2026-04-08T12:45:00Z"
}


⸻

12. API design

12.1 Core endpoints

Context
	•	POST /v1/context/resolve
	•	POST /v1/context/packs/build

Memory
	•	POST /v1/memory/search
	•	POST /v1/memory/episodes
	•	POST /v1/memory/facts
	•	POST /v1/memory/procedures
	•	POST /v1/memory/promote
	•	POST /v1/memory/archive
	•	GET /v1/memory/{id}

Capability
	•	POST /v1/capabilities/search
	•	POST /v1/capabilities/recommend
	•	GET /v1/capabilities/{id}
	•	POST /v1/capabilities/outcomes

Ingestion
	•	POST /v1/ingest/source
	•	POST /v1/ingest/repo
	•	POST /v1/ingest/git-diff
	•	POST /v1/ingest/skill
	•	POST /v1/ingest/mcp

Explainability
	•	GET /v1/explain/trace/{trace_id}
	•	POST /v1/explain/recall

Maintenance / repair
	•	POST /v1/maintenance/run
	•	POST /v1/repair/run
	•	GET /v1/jobs/{job_id}

Admin
	•	GET /v1/health
	•	GET /v1/metrics/summary
	•	POST /v1/policies/evaluate

⸻

13. MCP surface design

13.1 MCP tools to expose
	•	resolve_context
	•	search_memory
	•	remember_episode
	•	upsert_fact
	•	get_capabilities
	•	recommend_capabilities
	•	get_procedure
	•	build_context_pack
	•	explain_recall
	•	report_outcome
	•	run_maintenance_job

13.2 MCP resources to expose
	•	project summaries
	•	global context
	•	capability registry snapshots
	•	memory health reports
	•	architecture map
	•	decision map
	•	policy summaries

13.3 Harness usage pattern

Before search/build/edit cycles, harness invokes resolve_context or build_context_pack, then uses returned recommended tools/MCPs/skills and writes back outcomes at task completion.

⸻

14. CLI design

14.1 Commands

brain init
brain doctor
brain ingest path <path>
brain ingest diff <git-ref>
brain context resolve --project <name> --task <text>
brain memory search <query>
brain memory promote <id>
brain capability recommend <task>
brain explain <trace-id>
brain maintenance run <job>
brain repair run <job>
brain graph open
brain dashboard

14.2 Harness bootstrap commands

brain harness install codex
brain harness install claude-code
brain harness status
brain harness hooks sync
brain harness mcp print-config


⸻

15. Dashboard information architecture

15.1 Pages
	•	Overview
	•	Search
	•	Memories
	•	Episodic
	•	Semantic
	•	Procedural
	•	Emotional
	•	Archived
	•	Capabilities
	•	Skills
	•	Tools
	•	MCP Servers
	•	Workflows
	•	Graph
	•	Timelines
	•	Jobs
	•	Policies
	•	Models
	•	Sources
	•	Explainability
	•	Admin

15.2 Key widgets

Overview
	•	memory counts by type
	•	recent important memories
	•	contradiction count
	•	retrieval latency
	•	cache hit rate
	•	workflow queue depth
	•	top entities
	•	top capabilities
	•	storage growth

Graph page
	•	entity neighborhood
	•	project architecture map
	•	temporal playback
	•	contradiction overlays

Explainability page
	•	selected memory
	•	why retrieved
	•	truth state
	•	confidence history
	•	raw vs summary vs fact
	•	graph neighborhood

⸻

16. Temporal workflows

16.1 Required workflows
	•	ingest_source_workflow
	•	ingest_repo_change_workflow
	•	build_provisional_graph_workflow
	•	semantic_enrichment_workflow
	•	chunk_and_route_workflow
	•	resolve_context_pack_workflow
	•	remember_episode_workflow
	•	semantic_promotion_workflow
	•	procedural_promotion_workflow
	•	summarization_workflow
	•	contradiction_analysis_workflow
	•	graph_repair_workflow
	•	reembedding_workflow
	•	capability_rerank_workflow
	•	memory_quality_audit_workflow

16.2 Scheduled jobs
	•	fast cleanup every 5 minutes
	•	consolidation every hour
	•	summarization every 6 hours
	•	deep repair nightly
	•	quality audit daily
	•	re-embedding on model/policy change

⸻

17. Evaluation framework

17.1 Metrics
	•	recall@k
	•	precision@k
	•	retrieval latency
	•	summary fidelity
	•	contradiction rate
	•	fact freshness
	•	graph coverage
	•	chunk utility by strategy
	•	context pack success rate
	•	capability recommendation success rate
	•	user correction rate
	•	maintenance compression ratio

17.2 Eval datasets

Create eval corpora for:
	•	code repo understanding
	•	project decision recall
	•	skill/tool recommendation
	•	episodic timeline questions
	•	procedural retrieval
	•	conflict resolution

17.3 Regression gates

Every release should validate:
	•	no significant drop in recall quality
	•	no significant increase in contradiction rate
	•	no major latency regressions

⸻

18. Security and tenancy

18.1 Tenancy levels
	•	single-user local
	•	team workspace
	•	multi-project
	•	future multi-tenant enterprise

18.2 Controls
	•	per-namespace isolation
	•	RBAC / ABAC
	•	encrypted secrets via external secret manager
	•	audit logs
	•	export/delete support
	•	sensitivity classification

18.3 Sensitive data handling

Sensitive memories should be flagged and policy-protected from routine summarization or broad retrieval.

⸻

19. Coding harness implementation kit

19.1 What to hand to Codex or Claude Code

A coding agent needs:
	1.	product brief
	2.	architecture spec
	3.	file tree
	4.	API contracts
	5.	workflows list
	6.	prioritized milestones
	7.	coding rules
	8.	acceptance criteria
	9.	integration tasks
	10.	test plan

19.2 Coding agent execution strategy

Phase 0: foundation
	•	repo bootstrap
	•	Docker Compose
	•	FastAPI app
	•	Postgres/Redis/Neo4j boot
	•	config system
	•	base domain models

Phase 1: ingestion MVP
	•	source envelopes
	•	source classification
	•	deterministic extractors
	•	provisional graph builder
	•	basic chunking + vector routing

Phase 2: retrieval + context packs
	•	memory search
	•	capability search
	•	query classifier
	•	context pack assembly
	•	explainability traces

Phase 3: harness integration
	•	MCP server
	•	CLI
	•	Codex bootstrap package
	•	Claude Code bootstrap package
	•	writeback paths

Phase 4: consolidation + maintenance
	•	episode recording
	•	semantic/procedural promotion
	•	summarization
	•	duplicate detection
	•	salience scoring

Phase 5: governance + dashboard
	•	Keycloak integration
	•	OPA integration
	•	audit log
	•	operator dashboard
	•	repair controls

Phase 6: production hardening
	•	eval suite
	•	telemetry dashboards
	•	load testing
	•	backup/restore
	•	advanced policy controls

19.3 Acceptance criteria by phase

Phase 1
	•	repo file can be ingested
	•	AST/doc structure extracted
	•	graph nodes/edges created
	•	vector chunks stored
	•	provenance viewable

Phase 2
	•	query returns mixed memory results
	•	context pack includes facts + procedures + capabilities
	•	explainability trace available

Phase 3
	•	harness can call MCP tools
	•	CLI can resolve project context
	•	task outcome can be written back as episode

Phase 4
	•	repeated episodes promote to semantic/procedural memory
	•	maintenance can summarize/archive low-value memory
	•	capability rankings update after outcomes

Phase 5
	•	user/agent identities enforced
	•	policies can block unauthorized writes
	•	dashboard shows jobs, graphs, memory health

⸻

20. Default coding rules for the agent harness

20.1 Engineering rules
	•	preserve raw inputs; never mutate source artifacts in place
	•	all derived artifacts versioned
	•	every stored object must carry provenance and namespace
	•	every major service must emit telemetry
	•	all writes must be auditable
	•	prefer deterministic extraction before semantic extraction
	•	use interfaces for pluggable models and stores
	•	keep storage adapters isolated from domain logic
	•	write unit tests for contracts and integration tests for workflows

20.2 Prompt rules for coding agent

Use this as the system/developer instruction seed for Codex or Claude Code when building the repo:

You are building Brain Runtime, a local-first cognitive sidecar for coding agent harnesses.
Primary goals:
1. Build clean, modular, production-ready code.
2. Preserve strict domain boundaries.
3. Prefer deterministic extraction before model-based enrichment.
4. Every memory/capability object must include provenance, namespace, truth_state, and timestamps.
5. All workflows must be idempotent and retry-safe.
6. Expose stable interfaces for API, MCP, CLI, and SDK.
7. Favor implementation that is observable, auditable, and explainable.
8. Never hardcode one model or one storage backend when an adapter can be used.
9. Write tests with each feature.
10. Update docs and examples as you go.


⸻

21. Codex and Claude Code bootstrap notes

21.1 Codex

Use Brain Runtime as an external sidecar service. Provide:
	•	workspace bootstrap script
	•	project summary endpoint
	•	MCP server or API adapter
	•	hooks for pre-task context resolution and post-task episode writeback

Codex guidance from OpenAI emphasizes harness prompting, autonomy/persistence, and long-horizon reliability, which fits a sidecar architecture where the brain injects context and receives outcomes rather than trying to live inside the model prompt alone. (developers.openai.com￼)

21.2 Claude Code

Use:
	•	MCP integration for direct brain access
	•	hooks for deterministic pre/post actions
	•	repo-level plugin config for project-local context

Anthropic’s docs explicitly support hooks, MCP integration, and plugin configuration with skills, agents, hooks, and MCP servers, which makes Claude Code a strong first target for Brain Runtime integration. (docs.anthropic.com￼)

⸻

22. MVP recommendation

Best MVP scope

Build only this first:
	•	FastAPI API
	•	Neo4j + Redis + Postgres + one vector backend
	•	graph-first ingestion for code/docs/chats/skills
	•	memory search + context packs
	•	MCP server with 6 core tools
	•	CLI with init/ingest/search/context/explain
	•	minimal dashboard: Overview, Search, Graph, Jobs
	•	one maintenance workflow: semantic/procedural promotion + summarization

This is enough to prove the architecture without overbuilding.

⸻

23. Deliverables checklist

Architecture
	•	architecture decision record set
	•	service boundary map
	•	domain model glossary
	•	data lineage design

Backend
	•	API scaffold
	•	adapters for stores
	•	domain contracts
	•	workflows
	•	telemetry

Ingestion
	•	classifier
	•	deterministic parsers
	•	provisional graph builder
	•	chunking engine
	•	enrichment adapters

Retrieval
	•	query classifier
	•	router
	•	fusion/reranking
	•	context pack builder
	•	explainability traces

Capability intelligence
	•	capability schemas
	•	recommendation engine
	•	outcome tracking

Control plane
	•	identity integration
	•	OPA policies
	•	audit logging
	•	repair jobs

Experience
	•	MCP server
	•	CLI
	•	dashboard
	•	Python SDK

Quality
	•	tests
	•	evals
	•	benchmark scripts
	•	sample datasets

⸻

24. What to build first, concretely

Sprint 1
	•	scaffold monorepo
	•	docker compose for Postgres/Redis/Neo4j/vector backend
	•	FastAPI /health
	•	base domain models
	•	source envelope schema

Sprint 2
	•	ingest local repo path
	•	Python/Markdown/YAML deterministic parsing
	•	provisional graph write
	•	vector write

Sprint 3
	•	memory search endpoint
	•	query classifier
	•	context pack builder
	•	explainability trace model

Sprint 4
	•	MCP server tools
	•	CLI commands
	•	harness bootstrap scripts

Sprint 5
	•	remember_episode
	•	semantic/procedural promotion workflow
	•	summarization workflow

Sprint 6
	•	dashboard pages
	•	telemetry dashboards
	•	policy guardrails

⸻

25. Final recommendation

Start with Claude Code as the first-class harness target because its documented MCP, hooks, and plugin model make integration more direct. Add Codex immediately after via the same sidecar contract rather than building harness-specific memory logic twice. (docs.anthropic.com￼)

⸻

26. Copy/paste-ready monorepo starter

26.1 Root docker-compose.yml

version: "3.9"

services:
  postgres:
    image: postgres:16
    container_name: brain-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: brain_runtime
      POSTGRES_USER: brain
      POSTGRES_PASSWORD: brain
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    container_name: brain-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  neo4j:
    image: neo4j:5
    container_name: brain-neo4j
    restart: unless-stopped
    environment:
      NEO4J_AUTH: neo4j/password12345
      NEO4J_PLUGINS: '["apoc"]'
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs

  weaviate:
    image: semitechnologies/weaviate:1.25.5
    container_name: brain-weaviate
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: "true"
      PERSISTENCE_DATA_PATH: "/var/lib/weaviate"
      DEFAULT_VECTORIZER_MODULE: none
      ENABLE_MODULES: ""
      CLUSTER_HOSTNAME: node1
    volumes:
      - weaviate_data:/var/lib/weaviate

  temporal:
    image: temporalio/auto-setup:1.24.2
    container_name: brain-temporal
    restart: unless-stopped
    environment:
      DB: postgresql
      DB_PORT: 5432
      POSTGRES_USER: brain
      POSTGRES_PWD: brain
      POSTGRES_SEEDS: postgres
      DYNAMIC_CONFIG_FILE_PATH: config/dynamicconfig/development.yaml
    depends_on:
      - postgres
    ports:
      - "7233:7233"

  temporal-ui:
    image: temporalio/ui:2.27.0
    container_name: brain-temporal-ui
    restart: unless-stopped
    environment:
      TEMPORAL_ADDRESS: temporal:7233
    depends_on:
      - temporal
    ports:
      - "8233:8080"

  api:
    build:
      context: .
      dockerfile: infra/docker/api.Dockerfile
    container_name: brain-api
    restart: unless-stopped
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
      - neo4j
      - weaviate
      - temporal
    ports:
      - "8000:8000"
    volumes:
      - .:/app

  workers:
    build:
      context: .
      dockerfile: infra/docker/api.Dockerfile
    container_name: brain-workers
    restart: unless-stopped
    env_file:
      - .env
    command: ["python", "-m", "apps.workers.main"]
    depends_on:
      - api
      - temporal
    volumes:
      - .:/app

  mcp-server:
    build:
      context: .
      dockerfile: infra/docker/api.Dockerfile
    container_name: brain-mcp
    restart: unless-stopped
    env_file:
      - .env
    command: ["python", "-m", "apps.mcp_server.main"]
    depends_on:
      - api
    ports:
      - "8100:8100"
    volumes:
      - .:/app

  dashboard:
    build:
      context: .
      dockerfile: infra/docker/dashboard.Dockerfile
    container_name: brain-dashboard
    restart: unless-stopped
    env_file:
      - .env
    depends_on:
      - api
    ports:
      - "3000:3000"
    volumes:
      - .:/app

volumes:
  postgres_data:
  redis_data:
  neo4j_data:
  neo4j_logs:
  weaviate_data:

26.2 Root .env.example

APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=brain_runtime
POSTGRES_USER=brain
POSTGRES_PASSWORD=brain

REDIS_HOST=redis
REDIS_PORT=6379

NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password12345

WEAVIATE_URL=http://weaviate:8080

TEMPORAL_HOST=temporal:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=brain-runtime

BRAIN_DEFAULT_EMBEDDING_PROVIDER=local
BRAIN_DEFAULT_EMBEDDING_MODEL=bge-small-en-v1.5
BRAIN_DEFAULT_RERANKER_MODEL=bge-reranker-base
BRAIN_DEFAULT_EXTRACTOR_MODEL=qwen-instruct-local
BRAIN_DEFAULT_SUMMARIZER_MODEL=qwen-instruct-local

KEYCLOAK_URL=http://localhost:8081
KEYCLOAK_REALM=brain-runtime
KEYCLOAK_CLIENT_ID=brain-api
KEYCLOAK_CLIENT_SECRET=change-me

OPA_URL=http://localhost:8181

26.3 Root Makefile

.PHONY: up down logs api workers dashboard format lint test

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

api:
	uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload

workers:
	python -m apps.workers.main

dashboard:
	cd apps/dashboard && npm run dev

format:
	ruff format . && npm --prefix apps/dashboard run format

lint:
	ruff check . && npm --prefix apps/dashboard run lint

test:
	pytest -q

26.4 Root pyproject.toml

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "brain-runtime"
version = "0.1.0"
description = "Local-first cognitive sidecar for coding agent harnesses"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn[standard]>=0.30.0",
  "pydantic>=2.8.0",
  "pydantic-settings>=2.4.0",
  "sqlalchemy>=2.0.32",
  "psycopg[binary]>=3.2.1",
  "alembic>=1.13.2",
  "redis>=5.0.8",
  "neo4j>=5.23.1",
  "weaviate-client>=4.7.1",
  "temporalio>=1.7.0",
  "httpx>=0.27.0",
  "typer>=0.12.3",
  "rich>=13.7.1",
  "structlog>=24.4.0",
  "opentelemetry-api>=1.26.0",
  "opentelemetry-sdk>=1.26.0",
  "opentelemetry-instrumentation-fastapi>=0.47b0",
  "networkx>=3.3",
  "tree-sitter>=0.23.0",
  "tree-sitter-python>=0.23.2",
  "tree-sitter-javascript>=0.23.0",
  "markdown-it-py>=3.0.0",
  "pyyaml>=6.0.2",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3.2",
  "pytest-asyncio>=0.23.8",
  "ruff>=0.6.1",
  "mypy>=1.11.1",
]

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
asyncio_mode = "auto"

26.5 Root README.md

# Brain Runtime

Brain Runtime is a local-first cognitive sidecar for coding agent harnesses.

## Core capabilities
- graph-first ingestion
- hybrid memory
- context packs
- capability registry for skills/tools/MCPs
- Temporal-based maintenance and consolidation
- API + CLI + MCP + dashboard

## Quick start
1. Copy `.env.example` to `.env`
2. Run `make up`
3. Open API at `http://localhost:8000/docs`
4. Open dashboard at `http://localhost:3000`
5. Open Neo4j at `http://localhost:7474`
6. Open Temporal UI at `http://localhost:8233`

## MVP milestones
- ingest source files into graph + vector
- resolve task context packs
- expose MCP tools
- store episodes and promote facts/procedures


⸻

27. FastAPI starter

27.1 apps/api/main.py

from fastapi import FastAPI

from apps.api.routes.health import router as health_router
from apps.api.routes.context import router as context_router
from apps.api.routes.memory import router as memory_router
from apps.api.routes.ingest import router as ingest_router
from apps.api.routes.capabilities import router as capabilities_router


def create_app() -> FastAPI:
    app = FastAPI(title="Brain Runtime API", version="0.1.0")
    app.include_router(health_router, prefix="/v1")
    app.include_router(context_router, prefix="/v1")
    app.include_router(memory_router, prefix="/v1")
    app.include_router(ingest_router, prefix="/v1")
    app.include_router(capabilities_router, prefix="/v1")
    return app


app = create_app()

27.2 apps/api/routes/health.py

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

27.3 apps/api/routes/context.py

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["context"])


class ResolveContextRequest(BaseModel):
    workspace_id: str
    task: str = Field(min_length=1)
    namespace: str = "project"


class ResolveContextResponse(BaseModel):
    workspace_id: str
    summary: str
    recommended_capabilities: list[str]
    memory_ids: list[str]


@router.post("/context/resolve", response_model=ResolveContextResponse)
async def resolve_context(payload: ResolveContextRequest) -> ResolveContextResponse:
    return ResolveContextResponse(
        workspace_id=payload.workspace_id,
        summary=f"Context pack placeholder for task: {payload.task}",
        recommended_capabilities=["skill_debug_mcp", "tool_shell"],
        memory_ids=[],
    )

27.4 apps/api/routes/memory.py

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["memory"])


class MemorySearchRequest(BaseModel):
    query: str = Field(min_length=1)
    namespace: str = "project"
    limit: int = 10


class MemoryResult(BaseModel):
    memory_id: str
    title: str
    memory_type: str
    score: float


class MemorySearchResponse(BaseModel):
    results: list[MemoryResult]


@router.post("/memory/search", response_model=MemorySearchResponse)
async def search_memory(payload: MemorySearchRequest) -> MemorySearchResponse:
    return MemorySearchResponse(
        results=[
            MemoryResult(
                memory_id="mem_demo_001",
                title=f"Placeholder result for '{payload.query}'",
                memory_type="semantic",
                score=0.91,
            )
        ]
    )

27.5 apps/api/routes/ingest.py

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["ingest"])


class IngestSourceRequest(BaseModel):
    path: str = Field(min_length=1)
    workspace_id: str
    namespace: str = "project"


class IngestSourceResponse(BaseModel):
    source_id: str
    status: str


@router.post("/ingest/source", response_model=IngestSourceResponse)
async def ingest_source(payload: IngestSourceRequest) -> IngestSourceResponse:
    return IngestSourceResponse(source_id="src_demo_001", status=f"queued:{payload.path}")

27.6 apps/api/routes/capabilities.py

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["capabilities"])


class CapabilityRecommendRequest(BaseModel):
    task: str = Field(min_length=1)
    namespace: str = "project"


class CapabilityRecommendation(BaseModel):
    capability_id: str
    reason: str
    score: float


class CapabilityRecommendResponse(BaseModel):
    recommendations: list[CapabilityRecommendation]


@router.post("/capabilities/recommend", response_model=CapabilityRecommendResponse)
async def recommend_capabilities(
    payload: CapabilityRecommendRequest,
) -> CapabilityRecommendResponse:
    return CapabilityRecommendResponse(
        recommendations=[
            CapabilityRecommendation(
                capability_id="skill_repo_scan",
                reason=f"Relevant starter capability for task: {payload.task}",
                score=0.88,
            )
        ]
    )


⸻

28. Core package starter

28.1 packages/core/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "brain_runtime"
    postgres_user: str = "brain"
    postgres_password: str = "brain"

    redis_host: str = "localhost"
    redis_port: int = 6379

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password12345"

    weaviate_url: str = "http://localhost:8080"

    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "default"
    temporal_task_queue: str = "brain-runtime"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

28.2 packages/core/models/source.py

from datetime import datetime
from pydantic import BaseModel


class SourceEnvelope(BaseModel):
    source_id: str
    workspace_id: str
    namespace: str
    source_type: str
    content_class: str
    path: str | None = None
    raw_content_ref: str | None = None
    content_hash: str | None = None
    mime_type: str | None = None
    ingested_at: datetime

28.3 packages/core/models/memory.py

from datetime import datetime
from pydantic import BaseModel


class MemoryObject(BaseModel):
    memory_id: str
    type: str
    namespace: str
    title: str
    content: str
    truth_state: str
    confidence: float
    importance_score: float
    source_ids: list[str]
    valid_at: datetime | None = None
    invalid_at: datetime | None = None


⸻

29. Ingestion engine starter

29.1 packages/ingestion/service.py

from datetime import datetime, UTC
from pathlib import Path

from packages.core.models.source import SourceEnvelope
from packages.ingestion.classifier import classify_source
from packages.ingestion.parsers.registry import parse_source


class IngestionService:
    def ingest_path(self, workspace_id: str, path: str, namespace: str = "project") -> dict:
        file_path = Path(path)
        raw_text = file_path.read_text(encoding="utf-8", errors="ignore")

        envelope = SourceEnvelope(
            source_id=f"src_{file_path.stem}_{int(datetime.now(UTC).timestamp())}",
            workspace_id=workspace_id,
            namespace=namespace,
            source_type="repository_file",
            content_class=classify_source(file_path),
            path=str(file_path),
            raw_content_ref=None,
            content_hash=None,
            mime_type="text/plain",
            ingested_at=datetime.now(UTC),
        )

        parsed = parse_source(file_path, raw_text)

        return {
            "source": envelope.model_dump(),
            "parsed": parsed,
            "status": "parsed",
        }

29.2 packages/ingestion/classifier.py

from pathlib import Path


def classify_source(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return "source_code"
    if suffix in {".md", ".mdx"}:
        return "markdown_doc"
    if suffix in {".yaml", ".yml", ".json"}:
        return "config"
    return "text"

29.3 packages/ingestion/parsers/registry.py

from pathlib import Path

from packages.ingestion.parsers.markdown import parse_markdown
from packages.ingestion.parsers.python_ast import parse_python
from packages.ingestion.parsers.yaml_json import parse_yaml_json


def parse_source(path: Path, text: str) -> dict:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return parse_python(text)
    if suffix in {".md", ".mdx"}:
        return parse_markdown(text)
    if suffix in {".yaml", ".yml", ".json"}:
        return parse_yaml_json(text, suffix)
    return {"kind": "raw_text", "length": len(text)}

29.4 packages/ingestion/parsers/python_ast.py

import ast


def parse_python(text: str) -> dict:
    tree = ast.parse(text)
    functions: list[str] = []
    classes: list[str] = []
    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    return {
        "kind": "python_ast",
        "functions": sorted(set(functions)),
        "classes": sorted(set(classes)),
        "imports": sorted(set(imports)),
    }

29.5 packages/ingestion/parsers/markdown.py

def parse_markdown(text: str) -> dict:
    headings = [line.strip() for line in text.splitlines() if line.strip().startswith("#")]
    return {
        "kind": "markdown",
        "headings": headings,
        "length": len(text),
    }

29.6 packages/ingestion/parsers/yaml_json.py

import json
import yaml


def parse_yaml_json(text: str, suffix: str) -> dict:
    if suffix == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)

    keys = sorted(data.keys()) if isinstance(data, dict) else []
    return {
        "kind": "structured_config",
        "keys": keys,
    }


⸻

30. Temporal worker starter

30.1 apps/workers/main.py

import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from packages.core.settings import settings
from temporal.workflows.ingest import IngestSourceWorkflow
from temporal.activities.ingest import parse_source_activity


async def main() -> None:
    client = await Client.connect(settings.temporal_host, namespace=settings.temporal_namespace)
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[IngestSourceWorkflow],
        activities=[parse_source_activity],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

30.2 temporal/workflows/ingest.py

from datetime import timedelta
from temporalio import workflow


@workflow.defn
class IngestSourceWorkflow:
    @workflow.run
    async def run(self, workspace_id: str, path: str, namespace: str = "project") -> dict:
        return await workflow.execute_activity(
            "parse_source_activity",
            args=[workspace_id, path, namespace],
            start_to_close_timeout=timedelta(seconds=30),
        )

30.3 temporal/activities/ingest.py

from temporalio import activity

from packages.ingestion.service import IngestionService


@activity.defn(name="parse_source_activity")
def parse_source_activity(workspace_id: str, path: str, namespace: str = "project") -> dict:
    service = IngestionService()
    return service.ingest_path(workspace_id=workspace_id, path=path, namespace=namespace)


⸻

31. MCP server starter

31.1 apps/mcp_server/main.py

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Brain Runtime MCP Surface", version="0.1.0")


class ResolveContextPayload(BaseModel):
    workspace_id: str
    task: str


@app.post("/tools/resolve_context")
async def resolve_context(payload: ResolveContextPayload) -> dict:
    return {
        "workspace_id": payload.workspace_id,
        "task": payload.task,
        "summary": "MCP placeholder context pack",
        "recommended_capabilities": ["tool_shell", "skill_repo_scan"],
    }


@app.post("/tools/search_memory")
async def search_memory(payload: dict) -> dict:
    return {"results": [], "payload": payload}


⸻

32. CLI starter

32.1 apps/cli/main.py

import typer
import httpx

app = typer.Typer(help="Brain Runtime CLI")
API_URL = "http://localhost:8000/v1"


@app.command()
def init() -> None:
    typer.echo("Brain Runtime initialized")


@app.command()
def health() -> None:
    response = httpx.get(f"{API_URL}/health", timeout=10)
    typer.echo(response.text)


@app.command()
def ingest(path: str, workspace_id: str) -> None:
    response = httpx.post(
        f"{API_URL}/ingest/source",
        json={"path": path, "workspace_id": workspace_id, "namespace": "project"},
        timeout=30,
    )
    typer.echo(response.text)


@app.command()
def context(workspace_id: str, task: str) -> None:
    response = httpx.post(
        f"{API_URL}/context/resolve",
        json={"workspace_id": workspace_id, "task": task, "namespace": "project"},
        timeout=30,
    )
    typer.echo(response.text)


if __name__ == "__main__":
    app()


⸻

33. Dashboard starter

33.1 apps/dashboard/package.json

{
  "name": "brain-dashboard",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "format": "prettier --write ."
  },
  "dependencies": {
    "next": "15.0.0",
    "react": "18.3.1",
    "react-dom": "18.3.1"
  }
}

33.2 apps/dashboard/app/page.tsx

async function getHealth() {
  try {
    const res = await fetch("http://api:8000/v1/health", { cache: "no-store" });
    return await res.json();
  } catch {
    return { status: "unreachable" };
  }
}

export default async function HomePage() {
  const health = await getHealth();

  return (
    <main style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h1>Brain Runtime Dashboard</h1>
      <p>Minimal operator shell.</p>
      <section>
        <h2>Health</h2>
        <pre>{JSON.stringify(health, null, 2)}</pre>
      </section>
      <section>
        <h2>MVP pages to add next</h2>
        <ul>
          <li>Overview</li>
          <li>Search</li>
          <li>Graph</li>
          <li>Jobs</li>
          <li>Explainability</li>
        </ul>
      </section>
    </main>
  );
}


⸻

34. Dockerfiles

34.1 infra/docker/api.Dockerfile

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md /app/
RUN pip install --upgrade pip && pip install -e .

COPY . /app

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

34.2 infra/docker/dashboard.Dockerfile

FROM node:20-alpine
WORKDIR /app/apps/dashboard
COPY apps/dashboard/package.json /app/apps/dashboard/package.json
RUN npm install
COPY apps/dashboard /app/apps/dashboard
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3000"]


⸻

35. First coding-agent task list

Task 1: Repo bootstrap

Create the directory tree, root config files, Dockerfiles, and minimal FastAPI/CLI/dashboard startup paths exactly as specified above.

Task 2: Ingestion MVP

Implement deterministic parsers and IngestionService, then wire /v1/ingest/source to queue a Temporal workflow instead of returning a placeholder.

Task 3: Graph adapter

Create packages/graph/neo4j_adapter.py and write provisional graph nodes and edges for parsed Python/Markdown/YAML sources.

Task 4: Vector adapter

Create packages/vector/weaviate_adapter.py and store placeholder chunks with metadata.

Task 5: Context resolver

Replace placeholder resolve_context with retrieval router scaffolding and a simple context pack builder.

Task 6: MCP surface

Expand MCP server to expose the 6 core tools with stable request/response contracts.

Task 7: Dashboard shell

Build Overview, Search, Jobs, and Explainability pages with API calls.

⸻

36. Copy/paste coding prompt for Codex or Claude Code

Build the Brain Runtime monorepo according to the provided build kit.

Priority order:
1. Create the directory structure and root files.
2. Implement the Docker Compose stack and ensure the API boots.
3. Implement the ingestion MVP with deterministic parsing for Python, Markdown, YAML/JSON.
4. Add Temporal workflow wiring for source ingestion.
5. Add provisional graph writes and placeholder vector writes.
6. Implement context resolution and memory search scaffolding.
7. Add MCP server and CLI starter commands.
8. Add dashboard shell pages.

Engineering requirements:
- Use Python 3.11 and FastAPI.
- Keep code modular and typed.
- Preserve domain boundaries.
- Every stored object must carry provenance, namespace, timestamps, and truth_state where applicable.
- Do not over-engineer beyond the current milestone.
- Add tests for each implemented module.
- Keep raw source artifacts immutable.
- Prefer deterministic extraction before any model-based enrichment.


⸻

37. Immediate next files after scaffold

After the initial scaffold is complete, generate these next:
	•	packages/graph/neo4j_adapter.py
	•	packages/vector/weaviate_adapter.py
	•	packages/retrieval/router.py
	•	packages/context/service.py
	•	packages/explainability/service.py
	•	tests/unit/test_classifier.py
	•	tests/unit/test_python_parser.py
	•	tests/integration/test_health.py
	•	tests/integration/test_ingest_source.py

⸻

Implementation Specification

Purpose

This implementation specification converts the PRD into executable technical guidance for a coding harness. It defines service boundaries, data contracts, workflow behavior, interfaces, deployment patterns, and build order.

⸻

Section A — System Boundaries and Runtime Topology

A.1 Runtime Components

Core services
	•	API Service
	•	MCP Service
	•	Ingestion Service
	•	Memory Service
	•	Capability Service
	•	Retrieval Service
	•	Maintenance Service
	•	Governance Service
	•	Explainability Service
	•	Repair Service
	•	Worker Service
	•	Dashboard Service

Backing systems
	•	Postgres
	•	Redis
	•	Neo4j
	•	Vector DB
	•	Temporal
	•	Object store / local blob store
	•	Identity provider
	•	Policy engine
	•	Observability stack

A.2 Service Ownership

API Service

Owns request handling, auth enforcement, response shaping, public contracts.

MCP Service

Owns agent-facing tool/resource exposure, MCP request translation, hook-compatible interaction surface.

Ingestion Service

Owns source normalization, classification, deterministic parsing, enrichment dispatch, storage routing.

Memory Service

Owns memory records, memory lifecycle metadata, tier assignment, promotion inputs, provenance linkage.

Capability Service

Owns capability registry, capability scoring, lifecycle, dependency metadata, recommendation inputs.

Retrieval Service

Owns query classification, multi-store routing, fusion, reranking, context pack assembly.

Maintenance Service

Owns compression, retention, summarization, deduplication, archival movement.

Governance Service

Owns authorization, policy evaluation, mutation approval checks, namespace controls.

Explainability Service

Owns trace construction, retrieval path recording, recommendation rationale generation.

Repair Service

Owns repair jobs, conflict remediation, graph repair, re-embedding, restore logic.

Worker Service

Owns Temporal activities and workflow execution.

Dashboard Service

Owns operator-facing UI, policy controls, simulations, health and trace inspection.

A.3 Deployment Modes

Local single-node

All services run on one machine using containers.

Hybrid local + remote

Control plane and dashboard may run on a VPS; data-heavy memory plane can remain local.

Distributed

Services are independently deployable with externalized storage and workflow orchestration.

⸻

Section B — Canonical Data Contracts

B.1 Global Identifier Rules

All primary entities require stable IDs.

Required ID families
	•	source_id
	•	memory_id
	•	chunk_id
	•	episode_id
	•	fact_id
	•	procedure_id
	•	capability_id
	•	trace_id
	•	workflow_id
	•	policy_id
	•	namespace_id
	•	entity_id
	•	relation_id

B.2 Timestamps

All durable records must include:
	•	created_at
	•	updated_at
	•	valid_at (nullable)
	•	invalid_at (nullable)

B.3 Namespace Contract

Each durable object must include:
	•	namespace
	•	workspace_id (nullable for global objects)
	•	visibility_scope

B.4 Provenance Contract

Each derived object must include:
	•	source_ids
	•	parent_ids
	•	derivation_type
	•	model_version (nullable)
	•	workflow_name
	•	workflow_run_id

B.5 Truth State Enum
	•	deterministic
	•	extracted
	•	inferred
	•	ambiguous
	•	reinforced
	•	verified
	•	conflicting
	•	deprecated

B.6 Memory Object Contract

Required fields
	•	memory_id
	•	memory_type
	•	namespace
	•	workspace_id
	•	title
	•	content
	•	truth_state
	•	confidence
	•	importance_score
	•	current_tier
	•	source_ids
	•	parent_ids
	•	status
	•	created_by
	•	created_at
	•	updated_at
	•	valid_at
	•	invalid_at

Optional fields
	•	summary_of_ids
	•	embedding_ref
	•	graph_refs
	•	tags
	•	sensitivity
	•	pinned
	•	archived_reason

B.7 Capability Object Contract

Required fields
	•	capability_id
	•	capability_type
	•	namespace
	•	workspace_id
	•	name
	•	description
	•	version
	•	truth_state
	•	confidence
	•	status
	•	dependencies
	•	trigger_conditions
	•	supported_tasks
	•	reliability_score
	•	success_rate
	•	failure_rate
	•	average_latency_ms
	•	source_ids
	•	created_at
	•	updated_at

B.8 Source Envelope Contract

Required fields
	•	source_id
	•	workspace_id
	•	namespace
	•	source_type
	•	content_class
	•	content_subclass
	•	path_or_uri
	•	mime_type
	•	content_hash
	•	ingested_at
	•	ingestion_status

B.9 Chunk Contract

Required fields
	•	chunk_id
	•	memory_id
	•	source_id
	•	chunk_type
	•	strategy_used
	•	text
	•	token_count_estimate
	•	entities
	•	time_scope_start
	•	time_scope_end
	•	embedding_status
	•	created_at

B.10 Explainability Trace Contract

Required fields
	•	trace_id
	•	target_id
	•	target_type
	•	request_context
	•	reasons
	•	retrieval_path
	•	policy_filters_applied
	•	confidence_breakdown
	•	created_at

⸻

Section C — Storage Mapping Specification

C.1 Postgres Ownership

Use Postgres for:
	•	canonical metadata
	•	memory records
	•	capability records
	•	policy records
	•	workflow run summaries
	•	audit logs
	•	explainability traces
	•	retention and tier state

C.2 Neo4j Ownership

Use Neo4j for:
	•	entities
	•	relations
	•	temporal relationships
	•	project topology
	•	capability dependency graph
	•	provenance graph

C.3 Vector Store Ownership

Use vector storage for:
	•	semantic chunks
	•	summaries
	•	procedures
	•	natural language capability descriptions
	•	retrieval candidate embeddings

C.4 Redis Ownership

Use Redis for:
	•	working memory
	•	active context packs
	•	recent retrieval cache
	•	short-lived task state
	•	rate-limited simulation results

C.5 Blob/Object Storage Ownership

Use object storage or filesystem for:
	•	raw source content
	•	large transcripts
	•	archived artifacts
	•	workflow attachments
	•	export bundles

C.6 Source of Truth Rules
	•	Postgres is source of truth for record metadata and lifecycle status.
	•	Neo4j is source of truth for graph relationships.
	•	Vector store is source of truth for embedding-backed similarity retrieval.
	•	Blob store is source of truth for immutable raw inputs.
	•	Redis is never authoritative.

⸻

Section D — API Specification

D.1 API Conventions
	•	Prefix all endpoints with /v1.
	•	Require authentication for all non-health endpoints.
	•	Return structured errors with machine-readable codes.
	•	Idempotent mutation endpoints must accept a client request ID.

D.2 Error Contract

Response fields
	•	error_code
	•	message
	•	details
	•	trace_id

D.3 Context Endpoints

POST /v1/context/resolve

Purpose
Resolve a task-aware context pack.

Request
	•	workspace_id
	•	namespace
	•	task
	•	actor_id
	•	current_goal (optional)

Response
	•	context_pack_id
	•	summary
	•	facts
	•	episodes
	•	procedures
	•	graph_refs
	•	recommended_capabilities
	•	warnings
	•	trace_id

POST /v1/context/packs/build

Build a reusable named context pack.

D.4 Memory Endpoints

POST /v1/memory/search

Search across memory types.

POST /v1/memory/episodes

Create an episodic memory record.

POST /v1/memory/facts

Create or upsert a semantic fact.

POST /v1/memory/procedures

Create or upsert a procedure.

POST /v1/memory/promote

Promote memories to semantic or procedural form.

POST /v1/memory/archive

Archive a memory item.

POST /v1/memory/restore

Restore archived memory.

GET /v1/memory/{memory_id}

Fetch full memory record.

D.5 Capability Endpoints

POST /v1/capabilities/search

Search capability registry.

POST /v1/capabilities/recommend

Return ranked capabilities for a task.

POST /v1/capabilities/outcomes

Record execution outcome for a capability.

GET /v1/capabilities/{capability_id}

Fetch capability record.

D.6 Ingestion Endpoints

POST /v1/ingest/source

Queue ingestion of a single source.

POST /v1/ingest/repo

Queue ingestion of a repository path or repo snapshot.

POST /v1/ingest/git-diff

Queue incremental ingestion from a diff.

POST /v1/ingest/capability

Ingest a skill/tool/MCP manifest.

D.7 Explainability Endpoints

POST /v1/explain/recall

Generate or fetch explainability for retrieval.

GET /v1/explain/trace/{trace_id}

Fetch explainability trace.

D.8 Maintenance Endpoints

POST /v1/maintenance/run

Run a maintenance job.

POST /v1/maintenance/simulate

Simulate policy impact.

POST /v1/repair/run

Run a repair operation.

D.9 Admin Endpoints

GET /v1/health

Basic readiness and liveness.

GET /v1/metrics/summary

Aggregated system stats.

POST /v1/policies/evaluate

Evaluate a policy against a proposed action.

⸻

Section E — MCP Specification

E.1 MCP Tool Surface

Required tools
	•	resolve_context
	•	build_context_pack
	•	search_memory
	•	remember_episode
	•	upsert_fact
	•	store_procedure
	•	get_capabilities
	•	recommend_capabilities
	•	get_skill
	•	explain_recall
	•	report_outcome
	•	run_maintenance_job

E.2 MCP Tool Input Rules

Every MCP tool call must include:
	•	actor_id
	•	namespace
	•	workspace_id (when applicable)
	•	request_id

E.3 MCP Tool Output Rules

Every tool response must include:
	•	status
	•	result payload
	•	trace_id
	•	warnings (optional)

E.4 MCP Resource Surface

Required resources
	•	project_summary
	•	global_context
	•	capability_registry_snapshot
	•	memory_health_report
	•	policy_summary
	•	decision_map

E.5 MCP Router Behavior
	•	validate policy access before execution
	•	rank candidate MCP targets
	•	route to selected target
	•	record latency and outcome
	•	fall back to next valid target on failure when safe

⸻

Section F — Hook Specification

F.1 Pre-Execution Hook

Trigger points
	•	task start
	•	plan generation
	•	major tool-selection phase

Responsibilities
	•	resolve context pack
	•	retrieve recommended capabilities
	•	fetch warnings and constraints
	•	attach trace ID for downstream explainability

Inputs
	•	actor_id
	•	workspace_id
	•	namespace
	•	user task
	•	current goal (optional)

Outputs
	•	context pack
	•	capability recommendations
	•	policy constraints
	•	warnings
	•	trace_id

F.2 Post-Execution Hook

Trigger points
	•	task end
	•	tool execution completion
	•	error/failure completion

Responsibilities
	•	create episode
	•	extract facts/procedures when applicable
	•	record capability outcome
	•	trigger consolidation workflow

Inputs
	•	actor_id
	•	workspace_id
	•	namespace
	•	execution summary
	•	used capabilities
	•	outputs
	•	status

Outputs
	•	episode_id
	•	promoted_artifact_ids
	•	capability_outcome_ids
	•	maintenance_jobs_queued

F.3 Hook Safety Rules
	•	hooks must be idempotent
	•	hooks must tolerate partial failure
	•	post-hook must never block final response delivery
	•	hook payloads must respect token and latency budgets

⸻

Section G — Ingestion Implementation Specification

G.1 Source Classifier Interface

Input
	•	source envelope
	•	raw content metadata

Output
	•	content_class
	•	content_subclass
	•	recommended parsers
	•	candidate memory targets
	•	candidate chunking strategies

G.2 Deterministic Parser Interface

Input
	•	source envelope
	•	raw content

Output
	•	structural artifacts
	•	extracted deterministic nodes
	•	extracted deterministic edges
	•	parser warnings

G.3 Parser Types

Required initial parsers
	•	Python AST parser
	•	Markdown parser
	•	YAML/JSON parser
	•	transcript parser
	•	git diff parser

G.4 Enrichment Interface

Input
	•	source envelope
	•	deterministic artifacts
	•	ambiguity targets

Output
	•	facts
n- relations
	•	procedures
	•	events
	•	contradictions
	•	confidence values
	•	truth states

G.5 Storage Routing Rules
	•	Graph data → Neo4j
	•	Searchable chunk data → vector store
	•	Events/interactions → episodic memory in Postgres
	•	Facts → semantic memory in Postgres + graph linkages
	•	Procedures → procedural memory in Postgres + vector embeddings
	•	Large raw content → blob storage

G.6 Idempotency Rule

Ingestion must deduplicate by:
	•	source hash
	•	workspace_id
	•	parser version
	•	enrichment version

⸻

Section H — Retrieval Implementation Specification

H.1 Query Classifier Interface

Input
	•	query text
	•	workspace_id
	•	namespace
	•	actor_id
	•	current task state (optional)

Output
	•	query_types
	•	routing plan
	•	confidence per type

H.2 Retrieval Steps
	1.	classify query
	2.	fetch candidate records from appropriate stores
	3.	fuse candidates
	4.	rerank candidates
	5.	build context pack
	6.	generate explainability trace

H.3 Fusion Rules
	•	deduplicate by canonical record ID
	•	merge provenance lists
	•	preserve highest-confidence version as display default
	•	surface conflicting items separately

H.4 Reranking Inputs
	•	semantic relevance
	•	graph relevance
	•	procedural fit
	•	recency
	•	importance
	•	confidence
	•	policy visibility

H.5 Context Pack Contract

Required fields
	•	context_pack_id
	•	summary
	•	facts
	•	episodes
	•	procedures
	•	graph_refs
	•	recommended_capabilities
	•	warnings
	•	trace_id

⸻

Section I — Capability Implementation Specification

I.1 Registry Interface

Responsibilities
	•	register capability
	•	update capability
	•	search capability
	•	deactivate capability
	•	archive capability

I.2 Recommendation Interface

Inputs
	•	task
	•	context pack
	•	actor_id
	•	workspace_id
	•	namespace

Outputs
	•	ranked capabilities
	•	recommendation reasons
	•	trace_id

I.3 Outcome Interface

Inputs
	•	capability_id
	•	actor_id
	•	workspace_id
	•	task_summary
	•	success
	•	latency_ms
	•	error_type (optional)
	•	feedback (optional)

Effects
	•	update success/failure metrics
	•	update reliability score
	•	update recommendation model inputs

I.4 Lifecycle Rules
	•	active by default when registered
	•	deprecate on explicit operator action or policy
	•	archive after inactivity threshold
	•	disable on repeated policy or execution failure

⸻

Section J — Maintenance and Retention Specification

J.1 Tier Contract

Enum
	•	hot
	•	warm
	•	cold
	•	delete_candidate

J.2 Retention Policy Contract

Required fields
	•	policy_id
	•	scope
	•	namespace
	•	memory_type
	•	hot_ttl_days
	•	warm_ttl_days
	•	archive_after_days
	•	delete_after_days
	•	auto_archive
	•	auto_delete
	•	requires_review_if_sensitive
	•	enabled

J.3 Compression Policy Contract

Required fields
	•	policy_id
	•	memory_type
	•	strategy
	•	similarity_threshold
	•	min_cluster_size
	•	max_summary_depth
	•	protect_verified
	•	protect_sensitive
	•	enabled

J.4 Maintenance Workflows

Required scheduled jobs
	•	working memory cleanup
	•	episodic summarization
	•	semantic/procedural promotion
	•	deduplication
	•	graph compaction
	•	archive migration
	•	delete candidate cleanup

J.5 Restore Rules
	•	archived records must remain restorable during grace period
	•	delete_candidate records must require explicit or policy-approved purge
	•	restored records must regain provenance and prior tier history

⸻

Section K — Governance and Security Specification

K.1 Auth Contract

All non-health requests must include authenticated principal context.

K.2 Authorization Contract

Every mutation must evaluate:
	•	principal role
	•	namespace scope
	•	object sensitivity
	•	policy rules

K.3 Required Roles
	•	admin
	•	operator
	•	agent
	•	reader
	•	maintainer

K.4 Audit Log Contract

Every mutation must record:
	•	audit_id
	•	actor_id
	•	action
	•	target_type
	•	target_id
	•	namespace
	•	status
	•	timestamp
	•	policy_decision_ref

K.5 Sensitive Data Rules
	•	sensitive records require explicit policy visibility
	•	sensitive memory must be excluded from automated destructive operations unless explicitly allowed
	•	sensitive exports require authorization and audit logging

⸻

Section L — Explainability Specification

L.1 Explainability Coverage

Explainability is required for:
	•	retrieval outputs
	•	capability recommendations
	•	memory transformations
	•	policy denials

L.2 Explainability Record Requirements

Each trace must include:
	•	request summary
	•	target summary
	•	reasons
	•	ranking factors
	•	source references
	•	policy filters applied
	•	generation timestamp

L.3 UI Requirements

Operators must be able to inspect:
	•	why a memory was returned
	•	why a capability was recommended
	•	what workflow transformed a record
	•	what policy blocked an action

⸻

Section M — Repair Specification

M.1 Repair Job Types
	•	duplicate merge
	•	orphan cleanup
	•	graph edge repair
	•	entity merge
	•	contradiction clustering
	•	summary regeneration
	•	re-embedding
	•	provenance repair

M.2 Repair Job Contract

Required fields
	•	repair_job_id
	•	repair_type
	•	target_scope
	•	initiated_by
	•	dry_run
	•	status
	•	started_at
	•	completed_at
	•	affected_record_count

M.3 Safety Rules
	•	repair jobs must support dry-run mode
	•	high-impact repair jobs must be reversible
	•	repair jobs must emit audit and telemetry records

⸻

Section N — Dashboard Specification

N.1 Required Pages
	•	Overview
	•	Search
	•	Memories
	•	Capabilities
	•	Graph
	•	Timelines
	•	Jobs
	•	Policies
	•	Explainability
	•	Admin

N.2 Overview Widgets
	•	memory counts by type
	•	memory counts by tier
	•	ingestion throughput
	•	retrieval latency
	•	contradiction count
	•	capability success rate
	•	workflow queue depth
	•	storage growth

N.3 Required Operator Actions
	•	trigger ingest
	•	run maintenance
	•	run repair
	•	simulate policy
	•	move memory tier
	•	approve/reject sensitive change
	•	restore archived memory
	•	inspect explainability trace

⸻

Section O — Workflow Specification

O.1 Required Temporal Workflows
	•	ingest_source_workflow
	•	ingest_repo_workflow
	•	enrich_source_workflow
	•	route_storage_workflow
	•	resolve_context_workflow
	•	remember_episode_workflow
	•	semantic_promotion_workflow
	•	procedural_promotion_workflow
	•	summarization_workflow
	•	archive_migration_workflow
	•	graph_repair_workflow
	•	reembedding_workflow
	•	capability_outcome_update_workflow

O.2 Workflow Requirements
	•	durable execution
	•	retry-safe activities
	•	idempotent mutation handling
	•	observable execution history
	•	explicit workflow inputs and outputs

O.3 Activity Design Rule

Activities should be narrow and side-effect scoped. Domain orchestration belongs in workflows, not in activities.

⸻

Section P — Testing and Evaluation Specification

P.1 Required Test Layers
	•	unit tests for domain logic
	•	integration tests for storage adapters
	•	workflow tests for Temporal flows
	•	end-to-end tests for API + MCP + dashboard critical paths

P.2 Required Evaluation Domains
	•	retrieval quality
	•	context pack quality
	•	capability recommendation quality
	•	maintenance compression fidelity
	•	repair correctness

P.3 Release Gates

No release is valid without passing:
	•	API contract tests
	•	workflow regression tests
	•	retrieval regression tests
	•	policy enforcement tests
	•	restore and rollback tests

⸻

Section Q — Build Order Specification

Q.1 Phase 0 — Foundation
	•	repository scaffold
	•	env/config system
	•	health endpoints
	•	storage connectivity
	•	shared data contracts

Q.2 Phase 1 — Ingestion MVP
	•	source envelopes
	•	classifier
	•	deterministic parsers
	•	graph write MVP
	•	vector write MVP

Q.3 Phase 2 — Retrieval MVP
	•	query classifier
	•	retrieval routing
	•	context pack builder
	•	explainability traces

Q.4 Phase 3 — Agent Integration
	•	MCP server
	•	pre-hook
	•	post-hook
	•	memory skill definition

Q.5 Phase 4 — Promotion and Maintenance
	•	episodic memory creation
	•	fact/procedure promotion
	•	summarization
	•	tier movement

Q.6 Phase 5 — Control Plane
	•	auth integration
	•	policy engine integration
	•	audit logs
	•	dashboard controls

Q.7 Phase 6 — Hardening
	•	repair jobs
	•	simulations
	•	evaluation suite
	•	load and resilience testing

⸻

Section R — Coding Harness Execution Rules

R.1 Build Rules
	•	implement by phase, not by random feature selection
	•	keep domain models authoritative
	•	isolate adapters from domain logic
	•	do not bypass provenance fields
	•	do not mutate raw source artifacts

R.2 Required File Categories for Early Build
	•	contracts
	•	adapters
	•	workflows
	•	API handlers
	•	MCP handlers
	•	tests
	•	docs

R.3 Done Criteria for Any Feature

A feature is not done until it has:
	•	data contract
	•	API or workflow contract
	•	persistence path
	•	explainability coverage if applicable
	•	tests
	•	documentation update