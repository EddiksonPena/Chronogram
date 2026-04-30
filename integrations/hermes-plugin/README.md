# Chronogram Memory System

Multi-modal memory OS plugin for Hermes. Semantic search, graph entities, episodic memory, session auto-compaction, code-execution MCP routing, and feedback-driven reinforcement — all installed in one command.

## What's Inside

| Component | What It Does |
|-----------|-------------|
| **Skill** | Full reference guide for the Chronogram memory workflow |
| **MCP Server** | FastMCP server exposing 6 tools: remember, recall, compact, feedback, health, list |
| **Typed Wrappers** | Auto-generated Python wrappers for code-execution routing (98.7% context savings) |
| **Session Start Hook** | Bootstraps context from Chronogram: user profile, project conventions, recent decisions |
| **Result Filter Hook** | Summarizes large recall results in code before they hit the context window |
| **Auto-Compact Hook** | Triggers session compaction at 70% context pressure — no agent intervention needed |
| **Session End Hook** | Persists full session to durable memory, sends feedback, saves open loops |

## Install

```bash
hermes plugin install EddiksonPena/chronogram-memory-system
```

## Prerequisites

- Chronogram running on `localhost:4000` (Docker compose up)
- `uv` installed for MCP server runtime
- `mcp` Python package for code-execution wrappers

## After Install

On next Hermes restart:
- Session-start automatically recalls your preferences from Chronogram
- MCP tools route through code-execution wrappers automatically
- Context auto-compacts at 70% pressure
- Session-end persists everything to durable memory

No agent intervention required — the hooks handle it.
