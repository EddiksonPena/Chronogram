#!/usr/bin/env python3
"""Context pressure hook: auto-compact working memory to Chronogram.
When occupancy crosses threshold (default 70%), compacts recent messages
into Chronogram's durable memory stores and returns a working summary
so the agent can continue without losing context.
"""
import json, sys, os, urllib.request

CHRONOGRAM_URL = "http://127.0.0.1:4000"
DEFAULT_THRESHOLD = 0.70

try:
    ctx = json.load(sys.stdin)
except json.JSONDecodeError:
    print(json.dumps({"ok": False, "error": "Invalid stdin JSON"}))
    sys.exit(1)

occupancy = ctx.get("occupancy_ratio", 0)
session_id = ctx.get("session_id", "unknown")
threshold = ctx.get("threshold", DEFAULT_THRESHOLD)

# Only trigger if above threshold
if occupancy < threshold:
    print(json.dumps({"ok": True, "triggered": False}))
    sys.exit(0)

# Build minimal compact payload
# In a real implementation, the hook would have access to recent messages.
# Here we call Chronogram's compact endpoint with a placeholder — the actual
# messages would come from Hermes' context manager.
compact_payload = {
    "scope": "workspace",
    "occupancyRatio": occupancy,
    "sessionId": session_id,
    "messages": [
        {"role": "system", "content": f"Context at {occupancy*100:.0f}% occupancy. Compacting to free space."}
    ]
}

try:
    req = urllib.request.Request(
        f"{CHRONOGRAM_URL}/v1/memories/compact",
        data=json.dumps(compact_payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())

    output = {
        "ok": True,
        "triggered": data.get("triggered", False),
        "compacted_summary": data.get("workingSummary", "Context compacted."),
        "open_loops": data.get("openLoops", []),
    }
    print(json.dumps(output))
    sys.exit(0)

except Exception as e:
    # Chronogram unavailable — pass through
    print(json.dumps({
        "ok": True,
        "triggered": False,
        "note": f"Auto-compact skipped (Chronogram unavailable: {e})"
    }))
    sys.exit(0)
