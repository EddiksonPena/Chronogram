#!/usr/bin/env python3
"""Session-start hook: bootstrap context from Chronogram.
Reads session context from stdin, recalls user profile + project conventions,
and injects results into the system prompt.
"""
import json, sys, os

CHRONOGRAM_URL = "http://127.0.0.1:4000"
USER_PROFILE_SCOPE = "user-profile"
PROJECT_SCOPE_PREFIX = "project:"
PLUGIN_SCOPE = "plugin:chronogram-memory-system"

try:
    ctx = json.load(sys.stdin)
except json.JSONDecodeError:
    print(json.dumps({"ok": False, "error": "Invalid stdin JSON"}))
    sys.exit(1)

session_id = ctx.get("session_id", "unknown")
cwd = ctx.get("cwd", os.getcwd())
skills = ctx.get("skills", [])

# Detect project from cwd — extract project name if under ~/projects/
project = None
if "/projects/" in cwd:
    parts = cwd.split("/projects/")[-1].split("/")[0]
    if parts:
        project = parts

# Build recall queries
recalls = []

# Always recall user profile
recalls.append(("user-profile", USER_PROFILE_SCOPE, "user preferences, tools, conventions, and style"))

# If in a project directory, recall project conventions
if project:
    recalls.append((f"project:{project}", f"{PROJECT_SCOPE_PREFIX}{project}",
                    f"conventions, decisions, and standards for project '{project}'"))

# Recall plugin-specific patterns
recalls.append(("plugin-patterns", PLUGIN_SCOPE, "patterns and pitfalls specific to this plugin"))

# Execute all recalls (sequential to keep it simple)
injections = []
results = []
import urllib.request

for label, scope, desc in recalls:
    try:
        req = urllib.request.Request(
            f"{CHRONOGRAM_URL}/v1/memories/recall",
            data=json.dumps({
                "query": desc,
                "scope": scope,
                "includeDiagnostics": False
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            context_items = data.get("context", [])
            if context_items:
                # Summarize: first item's content
                top = context_items[0].get("content", "")
                injections.append(f"[{label}] {top[:300]}")
                results.append({"label": label, "items": len(context_items), "top_confidence": context_items[0].get("confidence", 0)})
    except Exception as e:
        # Chronogram might be down — continue without it
        injections.append(f"[{label}] (Chronogram unavailable: {e})")

# Build injection text
injection_text = "\n".join(injections) if injections else ""

output = {
    "ok": True,
    "inject_into_system_prompt": injection_text,
    "metadata": {
        "chronogram_bootstrap": {
            "session_id": session_id,
            "project": project,
            "recalls": results,
            "injections": len(injections)
        }
    }
}

print(json.dumps(output))
sys.exit(0)
