import json

import httpx
import typer

app = typer.Typer(help="MemCortex CLI")
API_URL = "http://localhost:8000/v1"


def print_json(payload: object) -> None:
    typer.echo(json.dumps(payload, indent=2))


@app.command()
def init() -> None:
    typer.echo("MemCortex initialized")


@app.command()
def doctor() -> None:
    response = httpx.get(f"{API_URL}/health", timeout=10)
    print_json(response.json())


@app.command()
def ingest(path: str, workspace_id: str, namespace: str = "project") -> None:
    response = httpx.post(
        f"{API_URL}/ingest/source",
        json={"path": path, "workspace_id": workspace_id, "namespace": namespace},
        timeout=30,
    )
    print_json(response.json())


@app.command()
def context(workspace_id: str, task: str, namespace: str = "project") -> None:
    response = httpx.post(
        f"{API_URL}/context/resolve",
        json={"workspace_id": workspace_id, "task": task, "namespace": namespace},
        timeout=30,
    )
    print_json(response.json())


@app.command()
def memory(query: str, workspace_id: str = "default", namespace: str = "project") -> None:
    response = httpx.post(
        f"{API_URL}/memory/search",
        json={
            "query": query,
            "workspace_id": workspace_id,
            "namespace": namespace,
        },
        timeout=30,
    )
    print_json(response.json())


@app.command()
def capability(task: str, workspace_id: str = "default", namespace: str = "project") -> None:
    response = httpx.post(
        f"{API_URL}/capabilities/recommend",
        json={
            "task": task,
            "workspace_id": workspace_id,
            "namespace": namespace,
        },
        timeout=30,
    )
    print_json(response.json())


@app.command("maintenance-run")
def maintenance_run(job_name: str, workspace_id: str = "default", namespace: str = "project") -> None:
    response = httpx.post(
        f"{API_URL}/maintenance/run",
        json={
            "job_name": job_name,
            "workspace_id": workspace_id,
            "namespace": namespace,
        },
        timeout=30,
    )
    print_json(response.json())


if __name__ == "__main__":
    app()
