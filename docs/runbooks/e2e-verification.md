# MemCortex End-to-End Verification Runbook

## Purpose

Use this runbook to verify MemCortex end to end: compose stack, API, MCP, CLI harness bootstrap, workflows, and dashboard reachability. This is the release-style gate for the repository.

## Prerequisites

- Docker and Docker Compose v2
- Python 3.11+
- The repo checked out locally
- Optional but recommended: the project virtual environment at `.venv`

## Bring Up The Stack

1. Copy `.env.example` to `.env` if you have not already.
2. If your machine already has common ports occupied, set the public port overrides in `.env`.
   Example:
   - `API_PUBLIC_PORT=18000`
   - `MCP_PUBLIC_PORT=18100`
   - `DASHBOARD_PUBLIC_PORT=13000`
3. Start the local runtime with `make up`.
3. Wait for these containers to report `running` or `Up`:
   - `postgres`
   - `redis`
   - `neo4j`
   - `weaviate`
   - `temporal`
   - `opa`
   - `keycloak`
   - `api`
   - `workers`
   - `mcp-server`
   - `dashboard`

## Run The Gate

Run the automated gate from the repo root:

```bash
python3 scripts/verify_e2e.py
```

If you changed the public ports, pass matching URLs through environment variables:

```bash
VERIFY_E2E_API_BASE=http://localhost:18000/v1 \
VERIFY_E2E_MCP_BASE=http://localhost:18100 \
VERIFY_E2E_DASHBOARD_BASE=http://localhost:13000 \
python3 scripts/verify_e2e.py
```

Or use the Makefile target:

```bash
make verify-e2e
```

The script checks:

- `docker compose ps` for the required services
- `GET /v1/health`
- `POST /v1/context/resolve`
- `POST /v1/memory/episodes` and `GET /v1/memory/{id}`
- `POST /v1/maintenance/run`
- `POST /tools/resolve_context` on the MCP server
- `python -m apps.cli.main harness targets`
- `python -m apps.cli.main harness install codex`
- `python -m apps.cli.main harness status`
- `python -m apps.cli.main harness mcp print-config codex`
- `GET /` on the dashboard

## Signoff Criteria

Treat the build as complete only if all of the following are true:

- Compose services are running.
- API health returns `ok`.
- Context resolution returns capability recommendations.
- Memory write/read round trip works.
- Maintenance goes through Temporal instead of degraded fallback.
- MCP tool invocation returns `status: ok`.
- Harness bootstrap commands succeed for Codex.
- Dashboard responds with HTTP 200.

## Troubleshooting

If the gate fails, triage in this order:

1. `docker compose ps`
2. `make logs`
3. `python3 scripts/verify_e2e.py`
4. `docker compose logs api workers temporal mcp-server dashboard --tail=200`

Common failure modes:

- `api` cannot reach Postgres, Redis, Neo4j, or Weaviate.
- `workers` is not connected to Temporal.
- `mcp-server` is up but auth headers are missing.
- The dashboard container is running but API requests are failing because the API service is not healthy yet.
