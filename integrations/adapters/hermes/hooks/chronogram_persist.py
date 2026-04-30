#!/usr/bin/env python3
"""Session-end hook: persist everything to Chronogram.
Compacts the full session into durable episodic, semantic, and procedural
memory. Sends feedback on all recalls made during the session. Saves open
loops for the next session start.
"""
import json, sys, urllib.request

CHRONOGRAM_URL = "http://127.0.0.1:4000"

try:
    ctx = json.load(sys.stdin)
except json.JSONDecodeError:
    print(json.dumps({"ok": False, "error": "Invalid stdin JSON"}))
    sys.exit(1)

session_id = ctx.get("session_id", "unknown")
message_count = ctx.get("message_count", 0)
recalls_made = ctx.get("recalls_made", [])
tools_used = ctx.get("tools_used", [])

persisted_count = 0
feedbacks_sent = 0

# 1. Compact full session to durable memory
compact_payload = {
    "scope": "workspace",
    "occupancyRatio": 1.0,  # Force compaction at session end
    "sessionId": session_id,
    "messages": [
        {"role": "system", "content": f"Session {session_id} ended after {message_count} messages. Persisting knowledge."}
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
        if data.get("triggered"):
            promoted = data.get("promoted", [])
            persisted_count = len(promoted)
except Exception as e:
    pass  # Persist best-effort — don't block session end on failure

# 2. Send feedback on recalls made during session
for recall in recalls_made:
    try:
        art_id = recall.get("artifact_id", "")
        useful = recall.get("useful", True)
        if art_id:
            req = urllib.request.Request(
                f"{CHRONOGRAM_URL}/v1/memories/feedback",
                data=json.dumps({"artifactId": art_id, "useful": useful}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                fb = json.loads(resp.read())
                if fb.get("updated"):
                    feedbacks_sent += 1
    except Exception:
        pass

# 3. Store open loops for next session
# (The compact response already returned open loops — they'll be picked up
#  by the next session_start bootstrap hook.)

output = {
    "ok": True,
    "triggered": True,
    "persisted_count": persisted_count,
    "feedbacks_sent": feedbacks_sent,
    "note": f"Session {session_id} persisted: {persisted_count} memories promoted, {feedbacks_sent} feedbacks sent."
}

print(json.dumps(output))
sys.exit(0)
