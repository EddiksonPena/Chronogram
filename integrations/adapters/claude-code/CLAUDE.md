# Chronogram Memory — Claude Code Integration

Chronogram gives you persistent, cross-session memory across all your projects.

## Tools Available
- `chronogram_health` — Check if Chronogram is running and healthy
- `chronogram_remember` — Store a fact, decision, or discovery permanently
- `chronogram_recall` — Semantically search your memory for anything
- `chronogram_compact` — Compact a conversation into durable memory
- `chronogram_feedback` — Reinforce or demote a memory
- `chronogram_list` — List all memories, optionally by scope

## When to remember
Store into Chronogram any time you:
- Learn a user preference, convention, or habit
- Fix a non-obvious error with a workaround worth reusing
- Complete a complex multi-step task successfully
- The user explicitly asks you to remember something

Use scope `user-profile` for facts about the user, `project:<name>` for project conventions, and `workspace` for general lessons.

## When to recall
Search Chronogram before asking the user to repeat themselves. If a question seems familiar or the user says "as I mentioned" or "remember when," recall first.

## Setup
1. Ensure Chronogram is running: `docker compose up -d` from the monorepo root
2. Copy `.mcp.json` to your project root (or merge into existing)
3. Claude Code auto-discovers MCP servers from `.mcp.json`
