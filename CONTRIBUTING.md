# Contributing

## Local setup

1. Copy `.env.example` to `.env`.
2. Create a virtual environment and install dependencies:
   `python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'`
3. Install dashboard dependencies:
   `npm install --prefix apps/dashboard`

## Validation

- Python tests: `.venv/bin/pytest -q`
- Python lint: `.venv/bin/ruff check .`
- Dashboard build: `npm run --prefix apps/dashboard build`

## Contribution rules

- Keep domain and business logic in `packages/*`; adapter layers in `apps/*` should stay thin.
- Add tests with every behavior change.
- Preserve the contracts and boundaries defined in `memory-prd.md` and `memory-implementation.md`.
- Prefer additive, backward-compatible schema changes.
