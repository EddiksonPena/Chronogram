QUERY_MODE_KEYWORDS = {
    "contextual": {"context", "current", "active", "task"},
    "episodic": {"history", "past", "previous", "episode", "decision"},
    "semantic": {"fact", "what", "why", "knowledge", "architecture"},
    "procedural": {"how", "steps", "procedure", "workflow", "runbook"},
    "graph": {"relationship", "dependency", "graph", "connected"},
    "temporal": {"when", "changed", "timeline", "evolved"},
    "capability": {"tool", "skill", "capability", "mcp"},
    "explainability": {"explain", "reason", "trace", "why selected"},
}


def classify_query(query: str) -> dict[str, object]:
    lowered = query.lower()
    matched: list[str] = []
    for mode, keywords in QUERY_MODE_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            matched.append(mode)

    if not matched:
        matched = ["contextual", "semantic", "capability"]

    priority_map = {
        "contextual": ["memory", "chunks", "graph"],
        "episodic": ["memory", "chunks"],
        "semantic": ["memory", "chunks", "graph"],
        "procedural": ["memory", "chunks", "capability"],
        "graph": ["graph", "memory"],
        "temporal": ["memory", "graph"],
        "capability": ["capability", "memory"],
        "explainability": ["memory", "graph", "capability"],
    }

    plan: list[str] = []
    for mode in matched:
        for source in priority_map[mode]:
            if source not in plan:
                plan.append(source)

    return {"query": query, "modes": matched, "routing_plan": plan}
