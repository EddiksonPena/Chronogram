import json
import sys

from packages.harness.service import HarnessService

try:
    import typer
except ModuleNotFoundError:  # pragma: no cover - exercised via plain Python bootstrap path
    typer = None

API_URL = "http://localhost:8000/v1"


def print_json(payload: object) -> None:
    text = json.dumps(payload, indent=2)
    if typer is not None:
        typer.echo(text)
    else:
        print(text)


def api_client():
    import httpx

    return httpx


def init() -> None:
    if typer is not None:
        typer.echo("MemCortex initialized")
    else:
        print("MemCortex initialized")


def doctor() -> None:
    response = api_client().get(f"{API_URL}/health", timeout=10)
    print_json(response.json())


def ingest(path: str, workspace_id: str, namespace: str = "project") -> None:
    response = api_client().post(
        f"{API_URL}/ingest/source",
        json={"path": path, "workspace_id": workspace_id, "namespace": namespace},
        timeout=30,
    )
    print_json(response.json())


def context(workspace_id: str, task: str, namespace: str = "project") -> None:
    response = api_client().post(
        f"{API_URL}/context/resolve",
        json={"workspace_id": workspace_id, "task": task, "namespace": namespace},
        timeout=30,
    )
    print_json(response.json())


def memory(query: str, workspace_id: str = "default", namespace: str = "project") -> None:
    response = api_client().post(
        f"{API_URL}/memory/search",
        json={
            "query": query,
            "workspace_id": workspace_id,
            "namespace": namespace,
        },
        timeout=30,
    )
    print_json(response.json())


def capability(task: str, workspace_id: str = "default", namespace: str = "project") -> None:
    response = api_client().post(
        f"{API_URL}/capabilities/recommend",
        json={
            "task": task,
            "workspace_id": workspace_id,
            "namespace": namespace,
        },
        timeout=30,
    )
    print_json(response.json())


def maintenance_run(job_name: str, workspace_id: str = "default", namespace: str = "project") -> None:
    response = api_client().post(
        f"{API_URL}/maintenance/run",
        json={
            "job_name": job_name,
            "workspace_id": workspace_id,
            "namespace": namespace,
        },
        timeout=30,
    )
    print_json(response.json())


def harness_install(
    target: str,
    workspace_id: str = "default",
    namespace: str = "project",
) -> None:
    service = HarnessService()
    try:
        print_json(service.install(target, workspace_id=workspace_id, namespace=namespace))
    except ValueError as exc:
        if typer is not None:
            raise typer.BadParameter(str(exc)) from exc
        raise SystemExit(str(exc)) from exc


def harness_status() -> None:
    print_json(HarnessService().status())


def harness_targets() -> None:
    print_json(HarnessService().list_targets())


def harness_hooks_sync(
    target: str = "codex",
    workspace_id: str = "default",
    namespace: str = "project",
) -> None:
    print_json(HarnessService().sync_hooks(target=target, workspace_id=workspace_id, namespace=namespace))


def harness_mcp_print_config(
    target: str = "codex",
    workspace_id: str = "default",
    namespace: str = "project",
) -> None:
    try:
        text = HarnessService().print_mcp_config(target=target, workspace_id=workspace_id, namespace=namespace)
        if typer is not None:
            typer.echo(text)
        else:
            print(text)
    except ValueError as exc:
        if typer is not None:
            raise typer.BadParameter(str(exc)) from exc
        raise SystemExit(str(exc)) from exc

if typer is not None:
    app = typer.Typer(help="MemCortex CLI")
    harness_app = typer.Typer(help="Harness bootstrap commands")
    mcp_app = typer.Typer(help="MCP bootstrap helpers")

    app.command()(init)
    app.command()(doctor)
    app.command()(ingest)
    app.command()(context)
    app.command()(memory)
    app.command()(capability)
    app.command("maintenance-run")(maintenance_run)
    harness_app.command("install")(harness_install)
    harness_app.command("status")(harness_status)
    harness_app.command("targets")(harness_targets)
    harness_app.command("hooks-sync")(harness_hooks_sync)
    mcp_app.command("print-config")(harness_mcp_print_config)
    harness_app.add_typer(mcp_app, name="mcp")
    app.add_typer(harness_app, name="harness")


def fallback_main(argv: list[str]) -> int:
    if not argv:
        print("MemCortex CLI fallback supports: harness install codex | harness status | harness hooks-sync | harness mcp print-config")
        return 0

    if argv[:2] == ["harness", "install"]:
        target = argv[2] if len(argv) > 2 else "codex"
        harness_install(target=target)
        return 0
    if argv[:2] == ["harness", "status"]:
        harness_status()
        return 0
    if argv[:2] == ["harness", "targets"]:
        harness_targets()
        return 0
    if argv[:2] == ["harness", "hooks-sync"]:
        target = argv[2] if len(argv) > 2 else "codex"
        harness_hooks_sync(target=target)
        return 0
    if argv[:3] == ["harness", "mcp", "print-config"]:
        target = argv[3] if len(argv) > 3 else "codex"
        harness_mcp_print_config(target=target)
        return 0

    print("This command requires the project CLI dependencies. Use `.venv/bin/python -m apps.cli.main ...` for full CLI support.")
    return 1


if __name__ == "__main__":
    if typer is not None:
        app()
    else:
        raise SystemExit(fallback_main(sys.argv[1:]))
