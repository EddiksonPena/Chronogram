"""Auto-generated MCP wrapper: chronogram/chronogram_recall — Semantically search Chronogram memory for anything matching a natural-language query.

query — what you're looking for, in plain English (e.g. 'user design preferences' or 'how was the last deploy done?')
scope — optional filter to a specific scope (user-profile, project:name, workspace, etc.)

Returns ranked context items with confidence scores, provenance, and salience metadata."""
from __future__ import annotations
from ._client import call_mcp


async def chronogram_recall(
    query: str, scope: str | None = None
) -> dict:
    """Semantically search Chronogram memory for anything matching a natural-language query.

query — what you're looking for, in plain English (e.g. 'user design preferences' or 'how was the last deploy done?')
scope — optional filter to a specific scope (user-profile, project:name, workspace, etc.)

Returns ranked context items with confidence scores, provenance, and salience metadata.

    Args:
        query:  (required)
        scope: 
    """
    return await call_mcp("chronogram_recall", {"query": query, "scope": scope})


def chronogram_recall_sync(query: str, scope: str | None = None) -> dict:
    import asyncio; return asyncio.run(chronogram_recall(query, scope))
