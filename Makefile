.PHONY: up down logs api workers mcp dashboard format lint test verify-e2e

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

mcp:
	uvicorn apps.mcp_server.main:app --host 0.0.0.0 --port 8100 --reload

dashboard:
	cd apps/dashboard && npm run dev

format:
	ruff format .

lint:
	ruff check .

test:
	pytest -q

verify-e2e:
	python3 scripts/verify_e2e.py
