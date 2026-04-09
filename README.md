# MemCortex

MemCortex is a local-first cognitive sidecar for coding agent harnesses. This repository now contains the initial monorepo scaffold for the architecture defined in [`memory-prd.md`](./memory-prd.md) and [`memory-implementation.md`](./memory-implementation.md).

## What is implemented

- FastAPI service with versioned API routes for health, context, memory, ingestion, capabilities, explainability, maintenance, and policy evaluation
- Shared domain contracts for sources, memories, capabilities, explainability, jobs, and policy decisions
- SQLAlchemy-backed control-plane persistence for sources, memories, capabilities, jobs, explainability traces, and policy decisions
- API route and MCP tool authz enforcement with bearer-token support, Keycloak-compatible JWT validation, OPA-backed authorization, and development-mode local fallback
- MCP tool envelopes with `actor_id`, `request_id`, wrapped `status/result/trace_id`, policy validation, and optional bearer token support
- Retrieval query classification, lexical document search over persisted chunks, and graph-neighborhood fallback routing
- Deterministic ingestion pipeline for Python, Markdown, YAML, and JSON
- Retrieval, capability recommendation, and maintenance services wired through the API and MCP surface
- Temporal-backed ingestion and maintenance workflow execution with degraded fallback when Temporal is unavailable
- Typer CLI for local operator and multi-harness bootstrap commands
- Next.js dashboard shell with overview of active services and planned pages
- Docker Compose stack for Postgres, Redis, Neo4j, Weaviate, Temporal, OPA, Keycloak, API, workers, MCP server, and dashboard
- API, ingestion, and harness bootstrap tests

## Quick start

1. Copy `.env.example` to `.env`
2. Install Python dependencies: `pip install -e .[dev]`
3. Install dashboard dependencies: `npm install --prefix apps/dashboard`
4. Run tests: `pytest -q`
5. Start the local stack: `make up`
6. Open the API docs at `http://localhost:8000/docs`
7. Open the dashboard at `http://localhost:3000`

## Auth model

- In development, API routes fall back to a local admin principal when no headers are supplied.
- In explicit auth mode, either send a bearer token or send headers such as `x-principal-id`, `x-principal-type`, `x-principal-roles`, `x-request-id`, `x-workspace-id`, and `x-namespace`.
- MCP tool calls must include `actor_id`, `request_id`, `workspace_id`, and `namespace`, or provide `bearer_token`.

## Harness bootstrap

Supported bootstrap targets:
- `codex`
- `claude`
- `gemini`
- `copilot`
- `openclaw`

Commands:
- List supported targets and capability negotiation: `python -m apps.cli.main harness targets`
- Install project-local bootstrap artifacts: `python -m apps.cli.main harness install <target>`
- Show bootstrap status for every target: `python -m apps.cli.main harness status`
- Regenerate hook scripts for hook-capable targets: `python -m apps.cli.main harness hooks-sync <target>`
- Print the MCP config snippet for MCP-capable targets: `python -m apps.cli.main harness mcp print-config <target>`

The install command writes project-local runtime artifacts under `.memcortex/<target>/` and shareable examples under `examples/<target>/`.

## Verification

- Run the end-to-end gate: `python3 scripts/verify_e2e.py`
- Or use the Makefile target: `make verify-e2e`
- Operator runbook: [`docs/runbooks/e2e-verification.md`](./docs/runbooks/e2e-verification.md)

## Release

- Current version: `0.1.0`
- Changelog: [`CHANGELOG.md`](./CHANGELOG.md)
- Release runbook: [`docs/runbooks/release.md`](./docs/runbooks/release.md)

## Key paths

- [`apps/api/main.py`](/Users/eddiksonpena/Projects/MemCortex/apps/api/main.py)
- [`apps/mcp_server/main.py`](/Users/eddiksonpena/Projects/MemCortex/apps/mcp_server/main.py)
- [`apps/cli/main.py`](/Users/eddiksonpena/Projects/MemCortex/apps/cli/main.py)
- [`packages/core/models/contracts.py`](/Users/eddiksonpena/Projects/MemCortex/packages/core/models/contracts.py)
- [`packages/ingestion/service.py`](/Users/eddiksonpena/Projects/MemCortex/packages/ingestion/service.py)
- [`packages/retrieval/service.py`](/Users/eddiksonpena/Projects/MemCortex/packages/retrieval/service.py)
- [`packages/storage/db.py`](/Users/eddiksonpena/Projects/MemCortex/packages/storage/db.py)
