# MemCortex Release Runbook

## Current release

- Version: `0.1.0`
- Git tag: `v0.1.0`

## Release gate

Run these from the repo root before tagging:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
npm run --prefix apps/dashboard build
VERIFY_E2E_API_BASE=http://localhost:18000/v1 \
VERIFY_E2E_MCP_BASE=http://localhost:18100 \
VERIFY_E2E_DASHBOARD_BASE=http://localhost:13000 \
python3 scripts/verify_e2e.py
```

## Tagging

```bash
git tag -a v0.1.0 -m "MemCortex v0.1.0"
git push origin main --follow-tags
```

## Release contents

- Multi-harness bootstrap support
- Operator dashboard
- Control-plane persistence
- Retrieval and context-pack assembly
- Temporal maintenance execution
- Local Docker runtime and E2E verification tooling
