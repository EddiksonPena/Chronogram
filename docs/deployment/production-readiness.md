# Production Readiness

## Goal

This runbook covers the final repo-level checks to perform before promoting a Chronogram build into production.

It is meant to sit on top of:

- the deployment reference in [`deploy/k8s/README.md`](../../deploy/k8s/README.md)
- the backup and recovery runbook in [`backup-and-restore.md`](./backup-and-restore.md)

## What This Runbook Verifies

The production readiness commands added in this repo cover three layers:

- preflight config validation
- live deployment smoke validation
- basic authenticated recall load validation

These checks do not replace cluster-specific load testing, chaos testing, or real restore drills, but they close the biggest “did we configure and wire this correctly?” gap before rollout.

## 1. Preflight The Production Config

Validate your production env file before deploying:

```bash
pnpm chronogram:preflight -- --env-file .env.production.example
```

For a real secret-injected file:

```bash
pnpm chronogram:preflight -- --env-file /path/to/chronogram-production.env
```

What it checks:

- `MEMORY_STATE_BACKEND=redis`
- required Redis, Weaviate, Neo4j, and Temporal settings exist
- placeholder values like `replace-me` are gone
- auth is not disabled
- API key settings are present when `api-key` or `hybrid` auth is used
- JWT issuer, audience, and JWKS reachability are checked when `jwt` or `hybrid` auth is used

## 2. Smoke Test A Live Deployment

Run against a running environment after deploy:

```bash
CHRONOGRAM_BASE_URL=https://chronogram-api.example.com \
CHRONOGRAM_WORKER_URL=https://chronogram-worker.example.com \
CHRONOGRAM_API_KEY=replace-with-real-key \
pnpm chronogram:smoke
```

Or with bearer auth:

```bash
CHRONOGRAM_BASE_URL=https://chronogram-api.example.com \
CHRONOGRAM_WORKER_URL=https://chronogram-worker.example.com \
CHRONOGRAM_BEARER_TOKEN=replace-with-real-token \
pnpm chronogram:smoke
```

What it verifies:

- API and worker `/health`
- public `/metrics`
- authenticated ingest
- authenticated recall of the injected smoke memory
- app module metrics endpoint
- worker workflow definitions
- worker workflow runs

The Kubernetes deploy workflow now uses this same smoke script after rollout.

## 3. Run A Basic Recall Load Check

After smoke passes, run a small authenticated load burst:

```bash
CHRONOGRAM_BASE_URL=https://chronogram-api.example.com \
CHRONOGRAM_API_KEY=replace-with-real-key \
pnpm chronogram:load -- --requests 60 --concurrency 6
```

This is not a substitute for formal performance testing, but it gives you a lightweight regression signal for:

- outright request failures
- elevated tail latency
- auth regressions under concurrent request pressure

## 4. Recommended Promotion Sequence

1. Publish a versioned image tag.
2. Run `promote-release` to deploy the same tag to staging.
3. Run `pnpm chronogram:smoke` against staging.
4. Run `pnpm chronogram:load` against staging.
5. Verify alert routing and dashboards.
6. Confirm backup freshness and restore readiness.
7. Promote the exact tested tag to production.

## 5. Still External To The Repo

These checks still need to happen in your real environment:

- DNS, TLS, ingress, and certificate validation
- real identity-provider token issuance for JWT mode
- restore drills using your real storage and object backup systems
- alert receiver verification for PagerDuty, Slack, or webhooks
- scaling and failure testing under your actual workload profile
