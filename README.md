# MemCortex

MemCortex is a local-first cognitive sidecar for coding agent harnesses. This repository now contains the initial monorepo scaffold for the architecture defined in [`memory-prd.md`](./memory-prd.md) and [`memory-implementation.md`](./memory-implementation.md).

## What is implemented

- FastAPI service with versioned API routes for health, context, memory, ingestion, capabilities, explainability, maintenance, and policy evaluation
- Shared domain contracts for sources, memories, capabilities, explainability, jobs, and policy decisions
- Deterministic ingestion pipeline for Python, Markdown, YAML, and JSON
- Retrieval, capability recommendation, and maintenance placeholder services wired through the API and MCP surface
- Temporal workflow and activity starter for source ingestion
- Typer CLI for local operator and harness bootstrap commands
- Next.js dashboard shell with overview of active services and planned pages
- Docker Compose stack for Postgres, Redis, Neo4j, Weaviate, Temporal, OPA, Keycloak, API, workers, MCP server, and dashboard
- Basic API and ingestion tests

## Quick start

1. Copy `.env.example` to `.env`
2. Install Python dependencies: `pip install -e .[dev]`
3. Install dashboard dependencies: `npm install --prefix apps/dashboard`
4. Run tests: `pytest -q`
5. Start the local stack: `make up`
6. Open the API docs at `http://localhost:8000/docs`
7. Open the dashboard at `http://localhost:3000`

## Key paths

- [`apps/api/main.py`](/Users/eddiksonpena/Projects/MemCortex/apps/api/main.py)
- [`apps/mcp_server/main.py`](/Users/eddiksonpena/Projects/MemCortex/apps/mcp_server/main.py)
- [`apps/cli/main.py`](/Users/eddiksonpena/Projects/MemCortex/apps/cli/main.py)
- [`packages/core/models/contracts.py`](/Users/eddiksonpena/Projects/MemCortex/packages/core/models/contracts.py)
- [`packages/ingestion/service.py`](/Users/eddiksonpena/Projects/MemCortex/packages/ingestion/service.py)
- [`packages/retrieval/service.py`](/Users/eddiksonpena/Projects/MemCortex/packages/retrieval/service.py)
