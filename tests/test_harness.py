import json
from pathlib import Path

import pytest

from packages.harness.service import HarnessService


def test_codex_install_writes_bootstrap_files(tmp_path: Path) -> None:
    service = HarnessService(repo_root=tmp_path)

    result = service.install("codex", workspace_id="proj_alpha", namespace="project")

    assert result["target"] == "codex"
    assert (tmp_path / ".memcortex" / "codex" / "adapter.json").exists()
    assert (tmp_path / ".memcortex" / "codex" / "bootstrap.json").exists()
    assert (tmp_path / ".memcortex" / "codex" / "mcp.json").exists()
    assert (tmp_path / ".memcortex" / "codex" / "hooks" / "pre-task.sh").exists()
    assert (tmp_path / ".memcortex" / "codex" / "hooks" / "post-task.sh").exists()
    assert (tmp_path / "examples" / "codex" / "mcp-config.example.json").exists()


def test_gemini_install_writes_hook_and_bootstrap_only(tmp_path: Path) -> None:
    service = HarnessService(repo_root=tmp_path)

    result = service.install("gemini", workspace_id="proj_alpha", namespace="project")

    assert result["target"] == "gemini"
    assert (tmp_path / ".memcortex" / "gemini" / "adapter.json").exists()
    assert (tmp_path / ".memcortex" / "gemini" / "bootstrap.json").exists()
    assert not (tmp_path / ".memcortex" / "gemini" / "mcp.json").exists()
    assert (tmp_path / ".memcortex" / "gemini" / "hooks" / "pre-task.sh").exists()


def test_copilot_install_writes_project_local_bootstrap_without_hooks(tmp_path: Path) -> None:
    service = HarnessService(repo_root=tmp_path)

    result = service.install("copilot")

    assert result["target"] == "copilot"
    assert (tmp_path / ".memcortex" / "copilot" / "adapter.json").exists()
    assert (tmp_path / ".memcortex" / "copilot" / "bootstrap.json").exists()
    assert not (tmp_path / ".memcortex" / "copilot" / "hooks" / "pre-task.sh").exists()
    assert not (tmp_path / ".memcortex" / "copilot" / "mcp.json").exists()


def test_status_reports_all_targets(tmp_path: Path) -> None:
    service = HarnessService(repo_root=tmp_path)
    for target in ["codex", "claude", "gemini", "copilot", "openclaw"]:
        service.install(target)

    status = service.status()

    assert "codex" in status["targets"]
    assert "claude" in status["targets"]
    assert "gemini" in status["targets"]
    assert "copilot" in status["targets"]
    assert "openclaw" in status["targets"]
    assert status["targets"]["copilot"]["checks"]["adapter_manifest"] is True


def test_print_mcp_config_is_valid_json_for_mcp_targets(tmp_path: Path) -> None:
    service = HarnessService(repo_root=tmp_path)

    codex = json.loads(service.print_mcp_config(target="codex", workspace_id="proj_alpha"))
    claude = json.loads(service.print_mcp_config(target="claude", workspace_id="proj_alpha"))

    assert codex["memcortex"]["url"].startswith("http://")
    assert claude["memcortex"]["url"].startswith("http://")
    assert "resolve_context" in codex["memcortex"]["tools"]


def test_print_mcp_config_fails_for_non_mcp_target(tmp_path: Path) -> None:
    service = HarnessService(repo_root=tmp_path)

    with pytest.raises(ValueError):
        service.print_mcp_config(target="copilot")


def test_list_targets_exposes_capability_negotiation(tmp_path: Path) -> None:
    service = HarnessService(repo_root=tmp_path)

    payload = service.list_targets()

    targets = {item["target"]: item for item in payload["targets"]}
    assert targets["claude"]["supports_mcp"] is True
    assert targets["gemini"]["supports_hooks"] is True
    assert targets["copilot"]["supports_hooks"] is False
