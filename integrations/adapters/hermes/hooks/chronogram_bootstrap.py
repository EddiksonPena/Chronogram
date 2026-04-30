#!/usr/bin/env python3
"""
Session-start hook: bootstrap context from Chronogram + MCP discovery guard.
Reads session context from stdin, recalls user profile + project conventions,
verifies Chronogram MCP tools are wired, and injects results into the system prompt.
"""
import json
import os
import sys
import urllib.request
import urllib.error

CHRONOGRAM_URL = "http://127.0.0.1:4000"
USER_PROFILE_SCOPE = "user-profile"
PROJECT_SCOPE_PREFIX = "project:"
PLUGIN_SCOPE = "plugin:chronogram-memory-system"
MCP_TOOL_PREFIX = "mcp_chronogram_"


def check_chronogram_health():
    """Health-check Chronogram API. Returns (ok, detail)."""
    try:
        req = urllib.request.Request(
            f"{CHRONOGRAM_URL}/health",
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            if data.get("status") == "ok":
                memory = data.get("memory", {})
                return True, f"healthy — {memory.get('artifactCount', '?')} artifacts"
            return False, f"unhealthy: {data.get('status')}"
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        return False, f"unreachable: {e}"
    except Exception as e:
        return False, f"error: {e}"


def check_mcp_tools_available(ctx):
    """Check if mcp_chronogram_* tools are in the session tool list."""
    tools = ctx.get("tools", [])
    chronogram_tools = [t for t in tools if t.startswith(MCP_TOOL_PREFIX)]
    return bool(chronogram_tools), chronogram_tools


def check_config_has_chronogram():
    """Check if config.yaml has mcp_servers.chronogram."""
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    try:
        with open(config_path) as f:
            content = f.read()
        return "chronogram:" in content and "mcp_servers:" in content
    except Exception:
        return False


def recall_from_chronogram(scope, query, label):
    """Recall from Chronogram API. Returns injection string or error."""
    try:
        req = urllib.request.Request(
            f"{CHRONOGRAM_URL}/v1/memories/recall",
            data=json.dumps({
                "query": query,
                "scope": scope,
                "includeDiagnostics": False
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            items = data.get("context", [])
            if items:
                top = items[0].get("content", "")
                return f"[{label}] {top[:300]}"
    except Exception as e:
        pass  # Continue without Chronogram — non-fatal
    return None


def detect_project(cwd):
    """Extract project name from working directory."""
    if "/projects/" in cwd:
        parts = cwd.split("/projects/")[-1].split("/")[0]
        if parts:
            return parts
    return None


# ── Main ──────────────────────────────────────────────
try:
    ctx = json.load(sys.stdin)
except json.JSONDecodeError:
    print(json.dumps({"ok": False, "error": "Invalid stdin JSON"}))
    sys.exit(1)

session_id = ctx.get("session_id", "unknown")
cwd = ctx.get("cwd", os.getcwd())

injections = []
discovery_issues = []

# Phase 1: Chronogram service health
api_ok, api_detail = check_chronogram_health()
if api_ok:
    injections.append(f"[chronogram-api] {api_detail}")
else:
    injections.append(f"[chronogram-api] {api_detail}")
    discovery_issues.append(
        "Chronogram API is not reachable. Start it with: docker compose up -d"
    )

# Phase 2: MCP config check
config_ok = check_config_has_chronogram()
if config_ok:
    injections.append("[chronogram-mcp] config.yaml has mcp_servers.chronogram entry ✓")
else:
    discovery_issues.append(
        "MCP server not in config. Run: hermes config set mcp_servers.chronogram.command uv"
    )

# Phase 3: MCP tool availability
tools_ok, chronogram_tools = check_mcp_tools_available(ctx)
if tools_ok:
    injections.append(
        f"[chronogram-mcp] {len(chronogram_tools)} tools available: "
        f"{', '.join(chronogram_tools)}"
    )
else:
    discovery_issues.append(
        "CHRONOGRAM MCP TOOLS NOT DISCOVERED. "
        "In chat, run slash command: /reload-mcp"
    )

if not tools_ok and discovery_issues:
    injections.append(
        "\n## ⚠️ CHRONOGRAM DISCOVERY WARNING\n"
        + "\n".join(f"- {issue}" for issue in discovery_issues)
    )

# Phase 4: Memory recall
project = detect_project(cwd)

result = recall_from_chronogram(
    USER_PROFILE_SCOPE,
    "user preferences, tools, conventions, and style",
    "user-profile"
)
if result:
    injections.append(result)

if project:
    result = recall_from_chronogram(
        f"{PROJECT_SCOPE_PREFIX}{project}",
        f"conventions, decisions, and standards for project '{project}'",
        f"project:{project}"
    )
    if result:
        injections.append(result)

# Return
output = {
    "ok": True,
    "inject_into_system_prompt": "\n".join(injections) if injections else "",
    "metadata": {
        "chronogram_bootstrap": {
            "session_id": session_id,
            "api_ok": api_ok,
            "config_ok": config_ok,
            "tools_ok": tools_ok,
            "mcp_tools": chronogram_tools if tools_ok else [],
            "project": project,
            "action_required": not tools_ok,
        }
    }
}

print(json.dumps(output))
sys.exit(0)
