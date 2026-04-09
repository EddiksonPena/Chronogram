# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-04-08

### Added
- FastAPI API and MCP surfaces for context resolution, memory operations, ingestion, explainability, maintenance, policy evaluation, and admin harness views.
- CLI bootstrap and status flows for `codex`, `claude`, `gemini`, `copilot`, and `openclaw`.
- Operator dashboard overview and harness readiness pages.
- Control-plane persistence with SQLAlchemy-backed job, memory, source, chunk, capability, and policy-decision records.
- Retrieval pipeline with query classification, stored chunk search, graph/vector adapter hooks, and context-pack assembly.
- Temporal workflows and activities for ingestion and maintenance execution.
- Docker Compose local runtime with Postgres, Redis, Neo4j, Weaviate, Temporal, OPA, Keycloak, API, MCP server, workers, and dashboard.
- CI workflow, contribution guide, license, examples, and end-to-end verification script/runbook.

### Changed
- Local runtime ports are configurable through `.env` so MemCortex can run alongside other local stacks.
- Local pytest execution is isolated from Docker-only database hostnames and falls back cleanly to local test configuration.

### Verified
- `pytest -q`
- `ruff check .`
- `npm run --prefix apps/dashboard build`
- `python3 scripts/verify_e2e.py` with the live Docker stack
