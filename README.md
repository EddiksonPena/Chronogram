# Chronogram

![Chronogram cover](https://raw.githubusercontent.com/EddiksonPena/Chronogram/main/docs/assets/chronogram-cover.png)

[![Node.js](https://img.shields.io/badge/Node.js-22%2B-5FA04E?logo=nodedotjs&logoColor=white)](https://nodejs.org/)
![Temporal](https://img.shields.io/badge/Temporal-000000?logo=temporal&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)
![Weaviate](https://img.shields.io/badge/Weaviate-00C4B3?logo=weaviate&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-4581C3?logo=neo4j&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-black)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)

**Chronogram** is memory infrastructure for autonomous agents and LLM-backed applications—a single HTTP memory API layered over Redis (working memory), Weaviate (semantic recall), Neo4j (graph memory), and Temporal (background workflows).

Use it when you want one **ingest / recall / feedback / compaction** contract instead of wiring each datastore and maintenance job yourself.

---

## Table of contents

- [Overview](#overview)
- [Who this is for](#who-this-is-for)
- [What you get (and what you do not)](#what-you-get-and-what-you-do-not)
- [Quick start](#quick-start)
- [Authenticate your requests](#authenticate-your-requests)
- [Using the Memory API](#using-the-memory-api)
- [Integrations appendix](#integrations-openai-langgraph-crewai-style)
- [Architecture](#architecture)
- [Ports](#ports-reference)
- [Onboarding tooling](#onboarding-tooling)
- [Build, package, deploy](#build-package-deploy)
- [Operational validation](#operational-validation)
- [Monitoring](#monitoring)
- [Security & hardening](#security--hardening)
- [Release maturity](#release-maturity)
- [Repository layout](#repository-layout)
- [Documentation](#documentation)
- [Contributing](#contributing)

---

## Overview

Chronogram **ingests** experiences and conversation context, **routes** artifacts into the right substrates, **recalls** blended context across lexical, semantic, graph, and recency signals, and **runs workflows** that reindex, compact, and promote durable memory.

The runtime is intentionally **two services**: `memory-api` (online ingest/recall paths) and `worker` (async maintenance orchestrated via Temporal).

## Who this is for

Chronogram is aimed at engineers who need:

- **Local-first development** — run the stack on one machine with Docker Compose plus two Node processes.
- **Integration testing** — hit stable HTTP endpoints while swapping embeddings and models behind the control plane.
- **Reference deployments** — use container images and Kubernetes manifests as templates, then harden them for your environment.

It is **not** a turnkey multi-tenant SaaS. Plan to supply identity, tenancy, quotas, backups, and production-grade infra around the manifests this repo publishes.

## What you get (and what you do not)

| You get | You do not get (today) |
|--------|-------------------------|
| HTTP Memory API (`/v1/memories/*`, metrics, workflows view) | A hosted SaaS UI or multitenant billing |
| Hybrid retrieval orchestration across Redis / Weaviate / Neo4j | MCP or FastAPI facades bundled in-repo (planned in docs only) |
| Feedback-driven salience and adaptive compaction | A fully scripted production CD path tested on every fork |
| Docker Compose stacks, GHCR images, K8s reference manifests | Stateful services auto-provisioned in every `kubectl apply` snippet |
| Grafana / Prometheus configs and alerting examples | Opinionated SOC2-style compliance toolkit |

See [release maturity](#release-maturity) for where this realistically fits in your rollout.

---

## Quick start

Requirements: **Node.js 22+**, **pnpm**, **Docker Desktop** (or Compose-compatible engine).

### Option A — Fully containerized app stack (recommended for product smoke)

This path keeps the API, worker, data stores, and Qwen embedding runtime inside
Docker. It is the closest local version of the shippable application.

```bash
cp .env.production.example .env
# Set CHRONOGRAM_API_KEY and replace any production placeholders before sharing the stack.
docker compose --profile app up -d --build
```

The first build downloads and caches the default quantized embedding model in
the app images:

```bash
EMBEDDING_PROVIDER=transformers
EMBEDDING_MODEL=onnx-community/Qwen3-Embedding-0.6B-ONNX
EMBEDDING_DTYPE=q8
EMBEDDING_DIMENSIONS=1024
```

Use `WARM_EMBEDDING_MODEL=false docker compose --profile app up -d --build`
for faster local rebuilds after the model path has already been verified.

### Option B — One-shot bootstrap

Requires only Node (no prior `pnpm install`):

```bash
node scripts/bootstrap.mjs init
```

This typically creates `.env` when missing, installs dependencies, lifts infrastructure, optionally starts app containers, verifies health endpoints, and can emit a harness bundle under `generated/harness/`.

### Option C — Manual host services

This path runs Redis, Weaviate, Neo4j, and Temporal in Docker, then runs the
Node API and worker on the host for faster edit/test cycles.

```bash
pnpm install
cp .env.example .env
# Set CHRONOGRAM_API_KEY before starting APIs (see Authenticate your requests).
docker compose up -d

pnpm --filter @chronogram/memory-api dev      # Terminal 1
pnpm --filter @chronogram/worker dev           # Terminal 2
```

### Smoke health checks

```bash
curl http://127.0.0.1:4000/health
curl http://127.0.0.1:4010/health
```

Prefer a guided UX? Install deps, then:

```bash
pnpm chronogram:ui
```

Open [`http://127.0.0.1:4020`](http://127.0.0.1:4020).

---

## Authenticate your requests

Default `.env.example` pins `CHRONOGRAM_AUTH_MODE=api-key`. Until `CHRONOGRAM_API_KEY` is **non-empty**, every `/v1/*` and `/workflows/*` request is rejected (**health** routes stay open).

Recommended paths:

1. **Bootstrap** — `node scripts/bootstrap.mjs init` generates a random key when `.env` is blank.
2. **Manual secret** — set `CHRONOGRAM_API_KEY=your-strong-secret`.
3. **Local-only experiments** — set `CHRONOGRAM_AUTH_MODE=none` (**never expose this publicly**).

Callers authenticate with **`x-api-key: <CHRONOGRAM_API_KEY>`** (or `Authorization: Bearer <same value>`).

JWT / hybrid modes (`CHRONOGRAM_AUTH_MODE=jwt|hybrid`) require issuer/JWKS configuration—follow [`SECURITY.md`](SECURITY.md) patterns.

Examples below assume you exported your key:

```bash
export CHRONOGRAM_API_KEY="$(grep '^CHRONOGRAM_API_KEY=' .env | cut -d= -f2-)"
API_AUTH=(-H "content-type: application/json" -H "x-api-key: ${CHRONOGRAM_API_KEY}")
```

If you flipped auth mode to `none`, drop the `-H x-api-key` lines.

---

## Using the Memory API

Base URL defaults to **`http://127.0.0.1:4000`** (`memory-api`). Worker HTTP defaults to **`http://127.0.0.1:4010`**.

### 1. Ingest memory

```bash
curl -X POST "${CHRONOGRAM_BASE_URL:-http://127.0.0.1:4000}/v1/memories/ingest" \
  -H 'content-type: application/json' \
  -H "x-api-key: ${CHRONOGRAM_API_KEY:?set CHRONOGRAM_API_KEY from .env}" \
  -d '{
    "scope": "workspace",
    "source": "readme-example",
    "tags": ["memory-os", "demo"],
    "content": "The Retrieval Orchestrator uses Redis for working memory, Weaviate for semantic search, and Neo4j for graph reasoning."
  }'
```

Artifacts land in Redis, Weaviate, and Neo4j; background workflows enqueue as configured.

### 2. Recall context

```bash
curl -X POST "${CHRONOGRAM_BASE_URL:-http://127.0.0.1:4000}/v1/memories/recall" \
  -H 'content-type: application/json' \
  -H "x-api-key: ${CHRONOGRAM_API_KEY:?set CHRONOGRAM_API_KEY from .env}" \
  -d '{
    "query": "What does the Retrieval Orchestrator use for working memory and graph reasoning?",
    "scope": "workspace",
    "includeDiagnostics": true
  }'
```

### 3. Apply feedback / salience

```bash
curl -X POST "${CHRONOGRAM_BASE_URL:-http://127.0.0.1:4000}/v1/memories/feedback" \
  -H 'content-type: application/json' \
  -H "x-api-key: ${CHRONOGRAM_API_KEY:?set CHRONOGRAM_API_KEY from .env}" \
  -d '{
    "artifactId": "<paste-artifact-id>",
    "useful": true
  }'
```

### 4. Compact & promote conversation memory

```bash
curl -X POST "${CHRONOGRAM_BASE_URL:-http://127.0.0.1:4000}/v1/memories/compact" \
  -H 'content-type: application/json' \
  -H "x-api-key: ${CHRONOGRAM_API_KEY:?set CHRONOGRAM_API_KEY from .env}" \
  -d '{
    "scope": "workspace",
    "occupancyRatio": 0.74,
    "sessionId": "demo-session",
    "messages": [
      { "role": "user", "content": "Redis runs on port 6380 locally." },
      { "role": "assistant", "content": "Check docker compose, restart worker, recall again." },
      { "role": "user", "content": "Follow up on auth rollout." }
    ]
  }'
```

### 5. Trigger maintenance workflows (worker API)

```bash
curl -X POST "${CHRONOGRAM_WORKER_URL:-http://127.0.0.1:4010}/workflows/reindex" \
  -H 'content-type: application/json' \
  -H "x-api-key: ${CHRONOGRAM_API_KEY:?set CHRONOGRAM_API_KEY from .env}" \
  -d '{}'
```

Inspect runs:

```bash
curl "${CHRONOGRAM_BASE_URL:-http://127.0.0.1:4000}/v1/workflows/runs"
curl "${CHRONOGRAM_WORKER_URL:-http://127.0.0.1:4010}/workflows/definitions"
```

### 6. Metrics & dashboards

```bash
curl http://127.0.0.1:4000/v1/metrics/modules
curl http://127.0.0.1:4000/metrics
curl http://127.0.0.1:4010/metrics
```

Default local dashboards (when infra profile is enabled): Grafana [`127.0.0.1:3001`](http://127.0.0.1:3001), Prometheus [`127.0.0.1:9090`](http://127.0.0.1:9090), Alertmanager [`127.0.0.1:9093`](http://127.0.0.1:9093).

### Minimal route map

Memory API highlights:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Liveness probe |
| `GET` | `/v1/memories` | Inspect stored summaries |
| `POST` | `/v1/memories/ingest` | Create memory artifacts |
| `POST` | `/v1/memories/recall` | Hybrid retrieval |
| `POST` | `/v1/memories/feedback` | Reward / attenuate artifacts |
| `POST` | `/v1/memories/compact` | Adaptive compaction workflow |
| `GET` | `/v1/workflows/runs` | Workflow visibility |
| `GET` | `/v1/metrics/modules` | JSON module telemetry |
| `GET` | `/metrics` | Prometheus scrape surface |

Worker highlights:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Worker probe |
| `POST` | `/workflows/reindex` | Kick async reindex |
| `POST` | `/workflows/execute` | Generic workflow enqueue |
| `GET` | `/workflows/definitions` | Enumerate workflow definitions |
| `GET` | `/workflows/runs` | Inspect run history |

---

## Integrations (OpenAI, LangGraph, CrewAI-style)

Chronogram is transport-agnostic HTTP. For **recall → augment prompt → respond → ingest** wiring with popular agent stacks, copy the patterns in [**`docs/integration/harness-integrations.md`**](docs/integration/harness-integrations.md) (minimal `fetch` helpers, an OpenAI Chat Completions example using `openai` on npm, LangGraph-style graph notes, and Crew-style tool hooks).

---

## Architecture

Services:

- **`memory-api`** — synchronous ingestion, retrieval, compaction, telemetry.
- **`worker`** — durable maintenance via Temporal (reindexing, housekeeping, batch jobs).

Data plane backends (managed by this repo via Compose manifests or externally in production):

| Store | Responsibility |
|-------|----------------|
| Redis | Working memory plus shared ephemeral state (`MEMORY_STATE_BACKEND=redis` recommended in containers). |
| Weaviate | Embeddings / semantic retrieval. |
| Neo4j | Temporal graph reasoning for entities & relations. |

Operational packaging includes Prometheus scraping, Grafana dashboards, Docker Compose presets, Kubernetes references, Alertmanager stubs, plus GitHub Actions for CI, image pushes, staged deploy pipelines.

![Reference architecture: Chronogram interface, API, control plane, data plane, execution plane, operations](https://raw.githubusercontent.com/EddiksonPena/Chronogram/main/docs/assets/architecture-reference.png)

Editable SVG source — [`docs/assets/architecture-reference.svg`](https://github.com/EddiksonPena/Chronogram/blob/main/docs/assets/architecture-reference.svg).

Deeper dives: [**System overview**](docs/architecture/system-overview.md) explains flows, compaction heuristics, and subsystem boundaries beyond this diagram.

---

## Ports reference

| Service | Port |
|---------|------|
| Memory API | `4000` |
| Worker | `4010` |
| Onboarding UI (`pnpm chronogram:ui`) | `4020` |
| Redis | `6380` (purposefully off `6379` to dodge host clashes) |
| Weaviate | `8080` |
| Neo4j Browser / Bolt | `7474` / `7687` |
| Temporal Frontend | `7233` |
| Grafana | `3001` |
| Prometheus | `9090` |
| Alertmanager | `9093` |

Local file-backed snapshots default to `./data` when `.env` uses `MEMORY_STATE_BACKEND=file`; container workloads should prefer Redis-backed coordination.

---

## Onboarding tooling

| Command | When to run |
|---------|--------------|
| `node scripts/bootstrap.mjs doctor` | Pre-flight prerequisites before sharing with teammates. |
| `node scripts/bootstrap.mjs init` | First-time workstation setup plus optional stack orchestration. |
| `node scripts/bootstrap.mjs connect` | Echo harness snippets for external agent stacks. |
| `node scripts/bootstrap.mjs down` | Tear down compose profiles started by onboarding. |

Harness payloads land in [`generated/harness/`](generated/harness/) (`chronogram-harness-config.{json,md}`) with `.env`-style exports, fetch samples, curl smoke snippets.

---

## Build, package, deploy

### Containers

```bash
docker build -f apps/memory-api/Dockerfile -t chronogram/memory-api:local .
docker build -f apps/worker/Dockerfile -t chronogram/worker:local .
```

### Compose “app profile”

```bash
cp .env.production.example .env   # Customize secrets before trusting this path
docker compose --profile app up -d --build
```

By default, the Compose app profile builds the Memory API and worker images with
`WARM_EMBEDDING_MODEL=true`, which downloads and caches the quantized Qwen
embedding model declared by:

```bash
EMBEDDING_PROVIDER=transformers
EMBEDDING_MODEL=onnx-community/Qwen3-Embedding-0.6B-ONNX
EMBEDDING_DTYPE=q8
EMBEDDING_DIMENSIONS=1024
```

Set `WARM_EMBEDDING_MODEL=false` for faster local image rebuilds, or set
`EMBEDDING_PROVIDER=hash` for deterministic offline smoke tests.

CI publishes immutable tags via [`.github/workflows/release-images.yml`](.github/workflows/release-images.yml).

### Kubernetes

Reference manifests live under [`deploy/k8s/`](deploy/k8s/) (ConfigMaps, workloads, PDBs, HPA hooks, Ingress examples).

**Bare reference** — applies only Chronogram workloads; operators must attach managed Redis / Weaviate / Neo4j / Temporal / Postgres externally.

```bash
kubectl apply -f deploy/k8s/namespace.yaml
kubectl apply -f deploy/k8s/configmap.yaml
kubectl apply -f deploy/k8s/secret.example.yaml
kubectl apply -f deploy/k8s/memory-api-deployment.yaml
kubectl apply -f deploy/k8s/worker-deployment.yaml
```

**Stacked demo** (`deploy/k8s/platform`) folds in Compose-adjacent data dependencies for evaluation clusters—still **reference-grade**, not a compliance-ready production bundle.

Staging / production rollout guidance: [**Production readiness playbook**](docs/deployment/production-readiness.md), [**Backup & restore**](docs/deployment/backup-and-restore.md), **[Distributed deployment considerations](docs/deployment/distributed-open-source-deployment.md)**.

GitHub workflows for reference environments: **[`deploy-reference.yml`](.github/workflows/deploy-reference.yml)**, **[`promote-release.yml`](.github/workflows/promote-release.yml)** — enable environment protection gates on GitHub Environment names before trusting automated promotion logic.

---

## Operational validation

```bash
pnpm chronogram:preflight -- --env-file .env.production.example
pnpm chronogram:smoke
pnpm chronogram:load -- --requests 60 --concurrency 6
```

These wrap [`scripts/production-readiness.mjs`](scripts/production-readiness.mjs)—pair them with staged smoke tests hitting every dependency tier.

---

## Monitoring

- Memory API publishes JSON summaries at **`GET /v1/metrics/modules`** and Prometheus text at **`GET /metrics`**.
- Worker publishes the same split at **`GET /metrics/modules`** and **`GET /metrics`**.
- Example **`ServiceMonitor`**, **`PrometheusRule`**, and **`AlertmanagerConfig`** resources live beside the Kubernetes manifests; tune receivers before applying to live clusters.

---

## Security & hardening

What already exists:

- Configurable **`CHRONOGRAM_AUTH_MODE`**: `api-key`, `jwt`, `hybrid`, `none`.
- Payload guardrails (`MAX_REQUEST_BYTES`).
- Cooperative shutdown honoring `SIGTERM`/`SIGINT`.
- Optional Redis-backed state for clustered pods.

Mandatory before trusting this on hostile networks:

- TLS termination at ingress
- Dedicated secret vaulting (avoid committing real secrets—even “example” overlays should rotate)
- Network policies narrowed to Temporal + datastore subnets
- Backups + restores validated per datastore (see **[backup playbook](docs/deployment/backup-and-restore.md)**)

Responsible disclosure guidelines live in **`SECURITY.md`**.

---

## Release maturity

| Stage | Suitability |
|-------|--------------|
| **Local / OSS evaluation** | **Ready** — Compose + docs + onboarding UI keep spin-up repeatable. CI enforces lint/build/typecheck/tests. GHCR publishes tags. |
| **Staging clusters** | **Partial** — You must bolt on managed infra, ingress, rotated secrets, and smoke automation. Harness integration **remains HTTP-first** (bring your own MCP if needed). |
| **Highly regulated enterprise production** | **Not endorsed yet** — You still need hardened dependency bundles, audited authorization semantics, repeatable CD plus rollback rehearsal, and field-tested ops runbooks. Finish those externally before staking production SLAs on this distribution. |

Use this framing in internal reviews and stakeholder updates so expectations stay grounded.

---

## Repository layout

| Path | Role |
|------|------|
| `apps/memory-api` | Production HTTP façade |
| `apps/worker` | Temporal-connected worker daemon |
| `packages/core` | Routing, ingestion, retrieval, lifecycle, adapters |
| `packages/config`, `packages/schemas`, `packages/auth`, `packages/onboarding` | Contracts + utilities |
| `infra/docker`, `deploy/k8s` | Runtime wiring & cluster templates |
| `docs/` | Narrative docs, roadmap, alignment notes |
| `scripts/` | Bootstrap + operational CLIs |

---

## Documentation

- [**Harness integrations (OpenAI / LangGraph-style / CrewAI-style)**](docs/integration/harness-integrations.md)
- [**Setup & day-two usage**](docs/setup/setup-and-usage.md)
- [**System overview & heuristics**](docs/architecture/system-overview.md)
- [**Production readiness checklist**](docs/deployment/production-readiness.md)
- [**Distributed deployment nuances**](docs/deployment/distributed-open-source-deployment.md)
- [**Kubernetes reference README**](deploy/k8s/README.md)
- [**Source alignment stance**](docs/reference/source-alignment.md)
- [**MVP roadmap**](docs/roadmap/mvp-roadmap.md)
- [**ADR 001 · Control-plane boundaries**](docs/adr/001-control-plane-boundaries.md)

Optional advanced topic — **Python Graphiti bridge**:

- Set `TEMPORAL_GRAPH_BACKEND=graphiti-python`.
- Provision `GRAPHITI_PYTHON_BIN` plus Graphiti's Ollama-backed model env vars
  (`OLLAMA_HOST`, `EXTRACTION_MODEL`, `GRAPHITI_EMBEDDING_MODEL`, etc.).
- Pin `GRAPHITI_GROUP_ID` for namespace isolation.

---

## Contributing

Please read **[`CONTRIBUTING.md`](CONTRIBUTING.md)** and **`CODE_OF_CONDUCT.md`** before submitting issues or patches.

---

MIT License · see **`LICENSE`** for full text.
