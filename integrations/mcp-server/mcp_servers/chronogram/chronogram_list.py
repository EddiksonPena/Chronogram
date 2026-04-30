"""Auto-generated MCP wrapper: chronogram/chronogram_list — List all memories stored in Chronogram, optionally filtered by scope.

scope — optional filter: 'user-profile', 'project:<name>', 'skill:<name>', 'workspace', etc."""
from __future__ import annotations
from ._client import call_mcp


async def chronogram_list(
    scope: str | None = None
) -> dict:
    """List all memories stored in Chronogram, optionally filtered by scope.

scope — optional filter: 'user-profile', 'project:<name>', 'skill:<name>', 'workspace', etc.

    Args:
        scope: 
    """
    return await call_mcp("chronogram_list", {"scope": scope})


def chronogram_list_sync(scope: str | None = None) -> dict:
    import asyncio; return asyncio.run(chronogram_list(scope))
