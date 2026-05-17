#!/usr/bin/env python3
"""
session_start hook: validate Chronogram is wired + recall context.
Hermes sends JSON on stdin: {session_id, cwd, tools, ...}
Validates 3 layers (API, config, MCP tools), recalls user/project memory.
"""
import json
import os
import sys
import urllib.request
import urllib.error

CHRONOGRAM_URL = os.environ.get("CHRONOGRAM_BASE_URL", "http://127.0.0.1:4000").rstrip("/")
CHRONOGRAM_API_KEY = os.environ.get("CHRONOGRAM_API_KEY", "").strip()


def headers():
    value = {"Content-Type": "application/json"}
    if CHRONOGRAM_API_KEY:
        value["x-api-key"] = CHRONOGRAM_API_KEY
    return value


def check_health():
    try:
        req = urllib.request.Request(f"{CHRONOGRAM_URL}/health", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
        if data.get("status") == "ok":
            mem = data.get("memory", {})
            return True, f"healthy — {mem.get('artifactCount', '?')} artifacts"
        return False, f"unhealthy: {data.get('status')}"
    except Exception as e:
        return False, f"unreachable: {e}"


def check_mcp_tools(tools):
    chrono = [t for t in tools if t.startswith("mcp_chronogram_")]
    return bool(chrono), chrono


def check_config():
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    try:
        with open(config_path) as f:
            return ("chronogram:" in f.read() and "mcp_servers:" in f.read())
    except Exception:
        return False


def recall_from_chronogram(scope, query, label):
    try:
        req = urllib.request.Request(
            f"{CHRONOGRAM_URL}/v1/memories/recall",
            data=json.dumps({"query": query, "scope": scope, "includeDiagnostics": False}).encode(),
            headers=headers(), method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        items = data.get("context", [])
        if items:
            return f"[{label}] {items[0].get('content', '')[:300]}"
    except Exception:
        pass
    return None


# ── Main ──
try:
    ctx = json.load(sys.stdin)
except json.JSONDecodeError:
    print(json.dumps({"ok": False, "error": "Invalid stdin JSON"}))
    sys.exit(1)

session_id = ctx.get("session_id", "unknown")
cwd = ctx.get("cwd", os.getcwd())
tools = ctx.get("tools", [])

injections = []
issues = []

# Layer 1: API health
api_ok, api_detail = check_health()
injections.append(f"[chronogram-api] {api_detail}")
if not api_ok:
    issues.append("Chronogram API not reachable. Run: docker compose up -d")

# Layer 2: Config check
config_ok = check_config()
injections.append(f"[chronogram-config] {'✓ wired' if config_ok else '✗ missing'}")
if not config_ok:
    issues.append("MCP server missing from config.yaml")

# Layer 3: MCP tools
tools_ok, chrono_tools = check_mcp_tools(tools)
if tools_ok:
    injections.append(f"[chronogram-mcp] {len(chrono_tools)} tools: {', '.join(chrono_tools)}")
else:
    issues.append("CHRONOGRAM MCP TOOLS NOT DISCOVERED. Run /reload-mcp in chat.")

# Warning block
if issues:
    injections.append("\n## ⚠️ CHRONOGRAM DISCOVERY WARNING\n" + "\n".join(f"- {i}" for i in issues))

# Memory recall
project = None
if "/projects/" in cwd:
    parts = cwd.split("/projects/")[-1].split("/")[0]
    if parts:
        project = parts

recalled = recall_from_chronogram("user-profile", "user preferences, tools, conventions, style", "user-profile")
if recalled:
    injections.append(recalled)

if project:
    recalled = recall_from_chronogram(f"project:{project}", f"conventions and decisions for {project}", f"project:{project}")
    if recalled:
        injections.append(recalled)

print(json.dumps({
    "ok": True,
    "inject_into_system_prompt": "\n".join(injections),
    "metadata": {
        "api_ok": api_ok, "config_ok": config_ok,
        "tools_ok": tools_ok, "mcp_tools": chrono_tools if tools_ok else [],
        "project": project, "action_required": not tools_ok
    }
}))
sys.exit(0)
