#!/usr/bin/env python3
"""Post-tool-call hook: filter large Chronogram recall results.
Intercepts mcp_chronogram_* results. If the result contains full context
items with large content fields, summarizes them in code before the agent
sees them. Raw MCP results never enter the context window — only summaries.
"""
import json, sys

# Maximum characters before summarization kicks in
MAX_RESULT_SIZE = 800

try:
    ctx = json.load(sys.stdin)
except json.JSONDecodeError:
    print(json.dumps({"ok": False, "error": "Invalid stdin JSON"}))
    sys.exit(1)

tool_name = ctx.get("tool_name", "")
raw_result = ctx.get("result", "")

# Only filter Chronogram MCP tools
if not tool_name.startswith("mcp_chronogram_"):
    print(json.dumps({"ok": True}))
    sys.exit(0)

# Parse the result if it's JSON
try:
    data = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
except (json.JSONDecodeError, TypeError):
    # Can't parse — pass through as-is
    print(json.dumps({"ok": True}))
    sys.exit(0)

# Only filter recall results (large context arrays)
if tool_name in ("mcp_chronogram_recall",):
    context_items = data.get("context", [])
    if not context_items or sum(len(json.dumps(c)) for c in context_items) < MAX_RESULT_SIZE:
        print(json.dumps({"ok": True}))
        sys.exit(0)

    # Build a lightweight summary
    summary_items = []
    for item in context_items[:5]:  # Top 5 only
        summary_items.append({
            "type": item.get("type", "?"),
            "summary": item.get("content", "")[:150],
            "confidence": item.get("confidence", 0),
            "id": item.get("id", "")
        })

    filtered = {
        "_filtered": True,
        "_original_count": len(context_items),
        "_summary": f"Chronogram recall returned {len(context_items)} items. Top matches:",
        "top_matches": summary_items
    }

    print(json.dumps({
        "ok": True,
        "filtered_result": json.dumps(filtered),
        "inject_note": f"[Chronogram filter] {len(context_items)} results summarized to {len(summary_items)} top matches."
    }))
    sys.exit(0)

# For remember/compact/feedback — pass through (small results)
print(json.dumps({"ok": True}))
sys.exit(0)
