#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
API_BASE = os.getenv("VERIFY_E2E_API_BASE", "http://localhost:8000/v1")
MCP_BASE = os.getenv("VERIFY_E2E_MCP_BASE", "http://localhost:8100")
DASHBOARD_BASE = os.getenv("VERIFY_E2E_DASHBOARD_BASE", "http://localhost:3000")
DEFAULT_WORKSPACE = "e2e_verification"
DEFAULT_NAMESPACE = "project"
COMPOSE_SERVICES = [
    "postgres",
    "redis",
    "neo4j",
    "weaviate",
    "temporal",
    "opa",
    "keycloak",
    "api",
    "workers",
    "mcp-server",
    "dashboard",
]


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def run_command(args: list[str], cwd: Path = REPO_ROOT) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return completed.stdout


def parse_json_output(output: str) -> object:
    text = output.strip()
    if not text:
        return []
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        records = []
        for line in text.splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))
        return records


def run_json_command(args: list[str], cwd: Path = REPO_ROOT) -> object:
    return parse_json_output(run_command(args, cwd=cwd))


def http_json(
    method: str,
    url: str,
    payload: dict[str, object] | None = None,
    *,
    workspace_id: str,
    namespace: str,
) -> object:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Content-Type": "application/json",
            "x-principal-id": "e2e.operator",
            "x-principal-roles": "admin,operator",
            "x-request-id": "req_e2e",
            "x-workspace-id": workspace_id,
            "x-namespace": namespace,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"{method} {url} failed with HTTP {exc.code}: {exc.read().decode('utf-8')}") from exc


def check_compose_stack() -> CheckResult:
    output = run_json_command(["docker", "compose", "ps", "--format", "json"])
    records = output if isinstance(output, list) else [output]
    services = {record.get("Service") or record.get("Name"): record for record in records if isinstance(record, dict)}

    missing = [service for service in COMPOSE_SERVICES if service not in services]
    if missing:
        return CheckResult("compose", False, f"missing services: {', '.join(missing)}")

    not_running = []
    for service in COMPOSE_SERVICES:
        record = services.get(service, {})
        state = str(record.get("State") or record.get("Status") or "").lower()
        if "running" not in state and "up" not in state:
            not_running.append(f"{service}={state or 'unknown'}")
    if not_running:
        return CheckResult("compose", False, f"non-running services: {', '.join(not_running)}")

    return CheckResult("compose", True, "all required services are up")


def check_api_health(workspace_id: str, namespace: str) -> CheckResult:
    health = http_json("GET", f"{API_BASE}/health", workspace_id=workspace_id, namespace=namespace)
    if health.get("status") != "ok":
        return CheckResult("api-health", False, f"unexpected health payload: {health}")
    return CheckResult("api-health", True, "API health endpoint responded with ok")


def check_api_context(workspace_id: str, namespace: str) -> tuple[CheckResult, dict[str, object]]:
    response = http_json(
        "POST",
        f"{API_BASE}/context/resolve",
        {
            "workspace_id": workspace_id,
            "namespace": namespace,
            "task": "verify retrieval, policy, and harness readiness",
        },
        workspace_id=workspace_id,
        namespace=namespace,
    )
    if not response.get("recommended_capabilities"):
        return CheckResult("api-context", False, f"missing recommendations: {response}"), {}
    return CheckResult("api-context", True, "context resolution returned recommendations"), response


def check_api_memory(workspace_id: str, namespace: str) -> CheckResult:
    episode = http_json(
        "POST",
        f"{API_BASE}/memory/episodes",
        {
            "workspace_id": workspace_id,
            "namespace": namespace,
            "title": "E2E verification memory",
            "content": "MemCortex e2e verification created this memory.",
        },
        workspace_id=workspace_id,
        namespace=namespace,
    )
    memory_id = episode.get("memory_id")
    if not memory_id:
        return CheckResult("api-memory", False, f"missing memory id: {episode}")

    fetched = http_json("GET", f"{API_BASE}/memory/{memory_id}", workspace_id=workspace_id, namespace=namespace)
    if fetched.get("memory_id") != memory_id:
        return CheckResult("api-memory", False, f"lookup mismatch: {fetched}")
    return CheckResult("api-memory", True, "memory write/read round trip succeeded")


def check_api_maintenance(workspace_id: str, namespace: str) -> CheckResult:
    job = http_json(
        "POST",
        f"{API_BASE}/maintenance/run",
        {
            "workspace_id": workspace_id,
            "namespace": namespace,
            "job_name": "semantic_promotion",
        },
        workspace_id=workspace_id,
        namespace=namespace,
    )
    if job.get("execution_mode") != "temporal":
        return CheckResult("api-maintenance", False, f"maintenance did not run through temporal: {job}")
    if job.get("status") not in {"running", "completed"}:
        return CheckResult("api-maintenance", False, f"unexpected maintenance status: {job}")
    return CheckResult("api-maintenance", True, "maintenance workflow scheduled through temporal")


def check_mcp(workspace_id: str, namespace: str) -> CheckResult:
    response = http_json(
        "POST",
        f"{MCP_BASE}/tools/resolve_context",
        {
            "actor_id": "e2e.agent",
            "roles": ["agent"],
            "request_id": "req_e2e_mcp",
            "workspace_id": workspace_id,
            "namespace": namespace,
            "task": "verify MCP path",
        },
        workspace_id=workspace_id,
        namespace=namespace,
    )
    if response.get("status") != "ok":
        return CheckResult("mcp", False, f"unexpected MCP response: {response}")
    if not response.get("result"):
        return CheckResult("mcp", False, f"missing MCP result payload: {response}")
    return CheckResult("mcp", True, "MCP tool call resolved context successfully")


def check_cli_bootstrap() -> CheckResult:
    target_output = run_command([sys.executable, "-m", "apps.cli.main", "harness", "targets"])
    targets = parse_json_output(target_output)
    if not isinstance(targets, dict) or "targets" not in targets:
        return CheckResult("cli-targets", False, f"unexpected target listing: {targets}")

    install_output = run_command([sys.executable, "-m", "apps.cli.main", "harness", "install", "codex"])
    install = parse_json_output(install_output)
    if install.get("target") != "codex":
        return CheckResult("cli-install", False, f"unexpected install output: {install}")

    status_output = run_command([sys.executable, "-m", "apps.cli.main", "harness", "status"])
    status = parse_json_output(status_output)
    codex_ready = status.get("targets", {}).get("codex", {}).get("ready")
    if codex_ready is not True:
        return CheckResult("cli-status", False, f"codex target not ready: {status}")

    mcp_output = run_command([sys.executable, "-m", "apps.cli.main", "harness", "mcp", "print-config", "codex"])
    mcp_config = parse_json_output(mcp_output)
    if mcp_config.get("memcortex", {}).get("url") is None:
        return CheckResult("cli-mcp", False, f"unexpected MCP config: {mcp_config}")

    return CheckResult("cli-bootstrap", True, "CLI harness bootstrap commands succeeded")


def check_dashboard() -> CheckResult:
    request = urllib.request.Request(DASHBOARD_BASE, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200:
                return CheckResult("dashboard", False, f"unexpected status: {response.status}")
            return CheckResult("dashboard", True, "dashboard responded with HTTP 200")
    except Exception as exc:  # pragma: no cover - network failure path
        return CheckResult("dashboard", False, str(exc))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run MemCortex end-to-end verification checks.")
    parser.add_argument("--workspace-id", default=DEFAULT_WORKSPACE)
    parser.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    args = parser.parse_args()

    workspace_id = args.workspace_id
    namespace = args.namespace

    checks: list[CheckResult] = [
        check_compose_stack(),
        check_api_health(workspace_id, namespace),
        check_cli_bootstrap(),
        check_mcp(workspace_id, namespace),
        check_dashboard(),
    ]

    context_check, context_payload = check_api_context(workspace_id, namespace)
    checks.append(context_check)
    if context_check.ok and context_payload and not context_payload.get("recommended_capabilities"):
        checks.append(CheckResult("api-context-capabilities", False, "no capability recommendations"))

    checks.append(check_api_memory(workspace_id, namespace))
    checks.append(check_api_maintenance(workspace_id, namespace))

    print("MemCortex e2e verification")
    print("==========================")
    all_ok = True
    for result in checks:
        status = "PASS" if result.ok else "FAIL"
        print(f"[{status}] {result.name}: {result.detail}")
        all_ok = all_ok and result.ok

    if all_ok:
        print("All end-to-end checks passed.")
        return 0

    print("One or more checks failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
