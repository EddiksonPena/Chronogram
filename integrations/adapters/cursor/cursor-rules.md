# Chronogram Memory — Cursor Rules

You have access to Chronogram, a persistent memory system. Use it to never forget.

## Available MCP Tools
- `chronogram_health` — Check service status
- `chronogram_remember(scope, content)` — Save a fact permanently
- `chronogram_recall(query)` — Find anything by meaning
- `chronogram_compact(session_id, messages)` — Archive conversation
- `chronogram_feedback(artifact_id, useful)` — Train the memory
- `chronogram_list(scope?)` — Browse stored memories

## Rules for using Chronogram
1. Save user preferences, conventions, and lessons immediately with `chronogram_remember`
2. Before asking the user to repeat info, try `chronogram_recall` first
3. After completing a complex task, compact it so the next session benefits
4. Give feedback on recall results — useful ones should rank higher next time
5. Use scope `user-profile` for personal facts, `project:<name>` for project context

## Setup
1. Copy `mcp.json` to `.cursor/mcp.json` in your project
2. Restart Cursor — MCP servers auto-discover
3. Ensure Chronogram docker containers are running
