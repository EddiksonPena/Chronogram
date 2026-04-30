# Chronogram Memory — Gemini CLI Integration

You have persistent memory through Chronogram. Never forget user preferences, project conventions, or hard-won solutions.

## MCP Tools
- `chronogram_health` — Verify Chronogram is running
- `chronogram_remember(scope, content)` — Store a durable fact
- `chronogram_recall(query, scope?)` — Search memory
- `chronogram_compact(session_id, messages)` — Compact conversation into memory
- `chronogram_feedback(artifact_id, useful)` — Train the memory
- `chronogram_list(scope?)` — Browse all memories

## Usage
- Store user preferences, environment details, and lessons learned with `chronogram_remember`
- Search memory with `chronogram_recall` before repeating yourself
- Feed back on recalled items to improve future relevance
- Compact after significant work so the state persists

## Setup
1. Place `settings.json` at `~/.gemini/settings.json` (or merge into existing)
2. Place `GEMINI.md` in your project root
3. Ensure Chronogram is running (`docker compose up -d` from monorepo root)
