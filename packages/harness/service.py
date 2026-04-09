from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

try:
    from packages.core.settings import settings as _settings
except ModuleNotFoundError:  # pragma: no cover - used by plain Python bootstrap path
    _settings = None


def _setting(name: str, default: str) -> str:
    if _settings is not None:
        return getattr(_settings, name)
    return os.getenv(name.upper(), default)


@dataclass(frozen=True)
class HarnessAdapter:
    key: str
    display_name: str
    supports_mcp: bool
    supports_hooks: bool
    supports_http: bool = True
    supports_stdio_json: bool = False
    supports_project_local_config: bool = True
    supports_post_task_writeback: bool = True
    integration_notes: tuple[str, ...] = ()


ADAPTERS: dict[str, HarnessAdapter] = {
    "codex": HarnessAdapter(
        key="codex",
        display_name="Codex",
        supports_mcp=True,
        supports_hooks=True,
        integration_notes=(
            "Use project-local hooks for pre-task context resolution and post-task outcome reporting.",
            "Use the generated MCP config to connect MemCortex as an external sidecar.",
        ),
    ),
    "claude": HarnessAdapter(
        key="claude",
        display_name="Claude Code",
        supports_mcp=True,
        supports_hooks=True,
        integration_notes=(
            "Prefer MCP as the primary integration path.",
            "Use hooks for deterministic writeback and pre-task resolution where supported.",
        ),
    ),
    "gemini": HarnessAdapter(
        key="gemini",
        display_name="Gemini CLI",
        supports_mcp=False,
        supports_hooks=True,
        supports_stdio_json=True,
        integration_notes=(
            "Default to hook and CLI wrapper integration.",
            "Use the HTTP API contract when direct MCP support is unavailable.",
        ),
    ),
    "copilot": HarnessAdapter(
        key="copilot",
        display_name="GitHub Copilot",
        supports_mcp=False,
        supports_hooks=False,
        supports_stdio_json=False,
        integration_notes=(
            "Default to API and project-local instruction/config integration.",
            "Use bootstrap artifacts as a team-standard sidecar contract rather than assuming CLI hooks.",
        ),
    ),
    "openclaw": HarnessAdapter(
        key="openclaw",
        display_name="OpenClaw",
        supports_mcp=False,
        supports_hooks=True,
        supports_stdio_json=True,
        integration_notes=(
            "Treat OpenClaw as a generic CLI harness unless it exposes a stable native protocol.",
            "Use HTTP and hook integration first, then add MCP only if the harness supports it cleanly.",
        ),
    ),
}


class HarnessService:
    def __init__(self, repo_root: str | Path | None = None) -> None:
        self.repo_root = Path(repo_root or Path.cwd()).resolve()

    def list_targets(self) -> dict[str, object]:
        return {
            "targets": [
                {
                    "target": adapter.key,
                    "display_name": adapter.display_name,
                    "supports_mcp": adapter.supports_mcp,
                    "supports_hooks": adapter.supports_hooks,
                    "supports_http": adapter.supports_http,
                    "supports_stdio_json": adapter.supports_stdio_json,
                    "supports_project_local_config": adapter.supports_project_local_config,
                    "supports_post_task_writeback": adapter.supports_post_task_writeback,
                }
                for adapter in ADAPTERS.values()
            ]
        }

    def install(
        self,
        target: str,
        *,
        workspace_id: str = "default",
        namespace: str = "project",
        overwrite: bool = True,
    ) -> dict[str, object]:
        adapter = self._adapter(target)
        target_dir = self.repo_root / ".memcortex" / adapter.key
        hooks_dir = target_dir / "hooks"
        target_dir.mkdir(parents=True, exist_ok=True)
        hooks_dir.mkdir(parents=True, exist_ok=True)

        files: dict[Path, str] = {
            target_dir / "adapter.json": self._adapter_manifest(adapter, workspace_id=workspace_id, namespace=namespace),
            target_dir / "bootstrap.json": self._bootstrap_config(adapter, workspace_id=workspace_id, namespace=namespace),
            target_dir / "README.md": self._readme(adapter),
        }
        if adapter.supports_mcp:
            files[target_dir / "mcp.json"] = self._mcp_config(workspace_id=workspace_id, namespace=namespace)
        if adapter.supports_hooks:
            files[hooks_dir / "pre-task.sh"] = self._pre_task_hook(workspace_id=workspace_id, namespace=namespace)
            files[hooks_dir / "post-task.sh"] = self._post_task_hook(workspace_id=workspace_id, namespace=namespace)

        written: list[str] = []
        for path, content in files.items():
            if overwrite or not path.exists():
                path.write_text(content, encoding="utf-8")
                written.append(str(path.relative_to(self.repo_root)))
                if path.suffix == ".sh":
                    path.chmod(0o755)

        examples_dir = self.repo_root / "examples" / adapter.key
        examples_dir.mkdir(parents=True, exist_ok=True)
        example_files = {
            examples_dir / "bootstrap.example.json": self._bootstrap_config(
                adapter,
                workspace_id=workspace_id,
                namespace=namespace,
            )
        }
        if adapter.supports_mcp:
            example_files[examples_dir / "mcp-config.example.json"] = self._mcp_config(
                workspace_id=workspace_id,
                namespace=namespace,
            )
        for path, content in example_files.items():
            path.write_text(content, encoding="utf-8")
            written.append(str(path.relative_to(self.repo_root)))

        return {
            "target": adapter.key,
            "display_name": adapter.display_name,
            "install_root": str(target_dir),
            "workspace_id": workspace_id,
            "namespace": namespace,
            "capabilities": self._capabilities(adapter),
            "files_written": written,
            "next_steps": self._next_steps(adapter),
        }

    def sync_hooks(
        self,
        *,
        target: str = "codex",
        workspace_id: str = "default",
        namespace: str = "project",
    ) -> dict[str, object]:
        adapter = self._adapter(target)
        if not adapter.supports_hooks:
            return {"target": target, "status": "unsupported", "reason": "target does not support hooks"}
        result = self.install(target, workspace_id=workspace_id, namespace=namespace, overwrite=True)
        return {"target": target, "status": "synced", "files_written": result["files_written"]}

    def status(self) -> dict[str, object]:
        targets: dict[str, object] = {}
        readiness: list[bool] = []
        for adapter in ADAPTERS.values():
            target_dir = self.repo_root / ".memcortex" / adapter.key
            hooks_dir = target_dir / "hooks"
            checks = {
                "target_root": target_dir.exists(),
                "adapter_manifest": (target_dir / "adapter.json").exists(),
                "bootstrap_config": (target_dir / "bootstrap.json").exists(),
                "readme": (target_dir / "README.md").exists(),
                "example_bootstrap": (self.repo_root / "examples" / adapter.key / "bootstrap.example.json").exists(),
            }
            if adapter.supports_mcp:
                checks["mcp_config"] = (target_dir / "mcp.json").exists()
                checks["example_mcp"] = (
                    self.repo_root / "examples" / adapter.key / "mcp-config.example.json"
                ).exists()
            if adapter.supports_hooks:
                checks["pre_task_hook"] = (hooks_dir / "pre-task.sh").exists()
                checks["post_task_hook"] = (hooks_dir / "post-task.sh").exists()
            target_ready = all(checks.values())
            readiness.append(target_ready)
            targets[adapter.key] = {
                "display_name": adapter.display_name,
                "path": str(target_dir),
                "capabilities": self._capabilities(adapter),
                "checks": checks,
                "ready": target_ready,
            }
        return {"ready": all(readiness), "targets": targets}

    def print_mcp_config(
        self,
        *,
        target: str = "codex",
        workspace_id: str = "default",
        namespace: str = "project",
    ) -> str:
        adapter = self._adapter(target)
        if not adapter.supports_mcp:
            raise ValueError(f"Harness target '{target}' does not support MCP bootstrap output")
        return self._mcp_config(workspace_id=workspace_id, namespace=namespace)

    def _adapter(self, target: str) -> HarnessAdapter:
        adapter = ADAPTERS.get(target)
        if adapter is None:
            raise ValueError(f"Unsupported harness target: {target}")
        return adapter

    def _capabilities(self, adapter: HarnessAdapter) -> dict[str, bool]:
        return {
            "supports_mcp": adapter.supports_mcp,
            "supports_hooks": adapter.supports_hooks,
            "supports_http": adapter.supports_http,
            "supports_stdio_json": adapter.supports_stdio_json,
            "supports_project_local_config": adapter.supports_project_local_config,
            "supports_post_task_writeback": adapter.supports_post_task_writeback,
        }

    def _next_steps(self, adapter: HarnessAdapter) -> list[str]:
        steps = [
            f"Review .memcortex/{adapter.key}/README.md for the local bootstrap flow.",
            "Keep MemCortex running with `make up` while the harness is active.",
        ]
        if adapter.supports_mcp:
            steps.append("Use `brain harness mcp print-config <target>` to print the MCP snippet for your client.")
        if adapter.supports_hooks:
            steps.append(f"Use `brain harness hooks sync {adapter.key}` after changing API or endpoint settings.")
        else:
            steps.append("Use the generated bootstrap JSON as the harness-side integration contract.")
        return steps

    def _mcp_config(self, *, workspace_id: str, namespace: str) -> str:
        payload = {
            "memcortex": {
                "transport": "http",
                "url": _setting("mcp_server_url", "http://localhost:8100"),
                "headers": {
                    "x-workspace-id": workspace_id,
                    "x-namespace": namespace,
                },
                "resources": ["/resources/project-summary"],
                "tools": [
                    "resolve_context",
                    "build_context_pack",
                    "search_memory",
                    "get_capabilities",
                    "recommend_capabilities",
                    "explain_recall",
                    "report_outcome",
                    "run_maintenance_job",
                ],
            }
        }
        return json.dumps(payload, indent=2)

    def _bootstrap_config(self, adapter: HarnessAdapter, *, workspace_id: str, namespace: str) -> str:
        payload = {
            "target": adapter.key,
            "display_name": adapter.display_name,
            "workspace_id": workspace_id,
            "namespace": namespace,
            "api_url": _setting("api_url", "http://localhost:8000"),
            "mcp_server_url": _setting("mcp_server_url", "http://localhost:8100"),
            "capabilities": self._capabilities(adapter),
            "pre_task_endpoint": "/v1/context/resolve",
            "post_task_endpoint": "/v1/capabilities/outcomes",
            "integration_notes": list(adapter.integration_notes),
        }
        return json.dumps(payload, indent=2)

    def _adapter_manifest(self, adapter: HarnessAdapter, *, workspace_id: str, namespace: str) -> str:
        payload = {
            "adapter": adapter.key,
            "display_name": adapter.display_name,
            "workspace_id": workspace_id,
            "namespace": namespace,
            "contract_version": "v1",
            "capabilities": self._capabilities(adapter),
        }
        return json.dumps(payload, indent=2)

    def _pre_task_hook(self, *, workspace_id: str, namespace: str) -> str:
        api_url = _setting("api_url", "http://localhost:8000")
        return f"""#!/usr/bin/env bash
set -euo pipefail

TASK="${{1:-}}"
if [ -z "$TASK" ]; then
  echo "usage: pre-task.sh '<task description>'" >&2
  exit 1
fi

API_URL="${{MEMCORTEX_API_URL:-{api_url}}}"
REQUEST_ID="req_$(date +%s)"

curl -sS "$API_URL/v1/context/resolve" \\
  -H "Content-Type: application/json" \\
  -H "x-request-id: $REQUEST_ID" \\
  -H "x-workspace-id: {workspace_id}" \\
  -H "x-namespace: {namespace}" \\
  --data "$(printf '{{"workspace_id":"{workspace_id}","namespace":"{namespace}","task":"%s"}}' "$TASK")"
"""

    def _post_task_hook(self, *, workspace_id: str, namespace: str) -> str:
        api_url = _setting("api_url", "http://localhost:8000")
        return f"""#!/usr/bin/env bash
set -euo pipefail

CAPABILITY_ID="${{1:-cap_memory_writeback}}"
SUCCESS="${{2:-true}}"
LATENCY_MS="${{3:-0}}"

API_URL="${{MEMCORTEX_API_URL:-{api_url}}}"

curl -sS "$API_URL/v1/capabilities/outcomes" \\
  -H "Content-Type: application/json" \\
  -H "x-workspace-id: {workspace_id}" \\
  -H "x-namespace: {namespace}" \\
  --data "$(printf '{{"workspace_id":"{workspace_id}","namespace":"{namespace}","capability_id":"%s","success":%s,"latency_ms":%s}}' "$CAPABILITY_ID" "$SUCCESS" "$LATENCY_MS")"
"""

    def _readme(self, adapter: HarnessAdapter) -> str:
        lines = [
            f"# MemCortex {adapter.display_name} Bootstrap",
            "",
            f"This directory contains a project-local {adapter.display_name} bootstrap package for MemCortex.",
            "",
            "Files:",
            "- `adapter.json`: adapter capabilities and contract metadata",
            "- `bootstrap.json`: API-side bootstrap contract for the harness",
        ]
        if adapter.supports_mcp:
            lines.append("- `mcp.json`: MemCortex MCP connection snippet")
        if adapter.supports_hooks:
            lines.extend(
                [
                    "- `hooks/pre-task.sh`: resolve context before a task",
                    "- `hooks/post-task.sh`: report a capability outcome after a task",
                ]
            )
        lines.extend(["", "Suggested flow:", "1. Start the local stack with `make up`.", "2. Review the bootstrap JSON and adapter manifest."])
        if adapter.supports_mcp:
            lines.append(f"3. Use `brain harness mcp print-config {adapter.key}` to print the MCP config snippet.")
        if adapter.supports_hooks:
            lines.append("4. Use the hooks as deterministic wrappers around task start and completion.")
        else:
            lines.append("4. Use the bootstrap JSON as the harness-side integration contract.")
        if adapter.integration_notes:
            lines.extend(["", "Integration notes:"])
            lines.extend([f"- {note}" for note in adapter.integration_notes])
        return "\n".join(lines) + "\n"
