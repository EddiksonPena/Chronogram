# Chronogram Memory — OpenCode Integration

Persistent memory for OpenCode. Cross-session, cross-project, always available.

## MCP Tools
- `chronogram_health` — Health check
- `chronogram_remember(scope, content)` — Persist a fact
- `chronogram_recall(query, scope?)` — Semantic search
- `chronogram_compact(session_id, messages)` — Compress conversation
- `chronogram_feedback(artifact_id, useful)` — Rate a memory
- `chronogram_list(scope?)` — List all memories

## When to use
- **Remember** user preferences, project conventions, non-obvious fixes
- **Recall** before asking "what was that thing again?"
- **Feedback** after each recall — boost what helps, demote what doesn't
- **Compact** before ending a session to save working state

## Setup
1. `opencode.json` → merge into your project's OpenCode config
2. `AGENTS.md` → place in project root
3. Chronogram must be running in docker
