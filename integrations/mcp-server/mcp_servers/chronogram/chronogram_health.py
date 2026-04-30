"""Auto-generated MCP wrapper: chronogram/chronogram_health — Check if Chronogram is reachable and healthy. Returns service status, artifact counts, and graph stats."""
from __future__ import annotations
from ._client import call_mcp


async def chronogram_health(
    
) -> dict:
    """Check if Chronogram is reachable and healthy. Returns service status, artifact counts, and graph stats."""
    return await call_mcp("chronogram_health", {})


def chronogram_health_sync() -> dict:
    import asyncio; return asyncio.run(chronogram_health())
