from neo4j import GraphDatabase

from packages.core.settings import settings
from packages.storage.db import SessionLocal
from packages.storage.repositories import graph_candidates


class GraphService:
    def upsert_source(
        self,
        source: dict[str, object],
        parsed: dict[str, object],
        chunks: list[dict[str, object]],
    ) -> dict[str, object]:
        try:
            with GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            ) as driver:
                with driver.session() as session:
                    session.run(
                        """
                        MERGE (s:Source {source_id: $source_id})
                        SET s.workspace_id = $workspace_id,
                            s.namespace = $namespace,
                            s.path = $path,
                            s.content_class = $content_class,
                            s.source_type = $source_type,
                            s.content_hash = $content_hash,
                            s.parsed = $parsed
                        """,
                        source_id=source["source_id"],
                        workspace_id=source["workspace_id"],
                        namespace=source["namespace"],
                        path=source.get("path"),
                        content_class=source["content_class"],
                        source_type=source["source_type"],
                        content_hash=source.get("content_hash"),
                        parsed=parsed,
                    )
                    for chunk in chunks:
                        session.run(
                            """
                            MATCH (s:Source {source_id: $source_id})
                            MERGE (c:Chunk {chunk_id: $chunk_id})
                            SET c.workspace_id = $workspace_id,
                                c.namespace = $namespace,
                                c.text = $text,
                                c.chunk_order = $chunk_order,
                                c.content_class = $content_class
                            MERGE (s)-[:HAS_CHUNK]->(c)
                            """,
                            source_id=source["source_id"],
                            chunk_id=chunk["chunk_id"],
                            workspace_id=source["workspace_id"],
                            namespace=source["namespace"],
                            text=chunk["text"],
                            chunk_order=chunk["order"],
                            content_class=source["content_class"],
                        )
                return {
                    "status": "persisted",
                    "backend": "neo4j",
                    "nodes": 1 + len(chunks),
                    "relationships": len(chunks),
                }
        except Exception as exc:
            return {
                "status": "fallback",
                "backend": "control_plane",
                "reason": str(exc),
                "nodes": 1 + len(chunks),
                "relationships": len(chunks),
            }

    def neighborhood(self, workspace_id: str, namespace: str, query: str, limit: int = 5) -> list[dict[str, object]]:
        try:
            with GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            ) as driver:
                with driver.session() as session:
                    records = session.run(
                        """
                        MATCH (s:Source)-[:HAS_CHUNK]->(c:Chunk)
                        WHERE s.workspace_id = $workspace_id
                          AND s.namespace = $namespace
                          AND (
                            toLower(coalesce(s.path, "")) CONTAINS toLower($query)
                            OR toLower(coalesce(c.text, "")) CONTAINS toLower($query)
                            OR toLower(coalesce(s.content_class, "")) CONTAINS toLower($query)
                          )
                        RETURN s.source_id AS node_id,
                               s.path AS path,
                               s.content_class AS content_class,
                               collect(c.chunk_id)[0..3] AS chunk_ids
                        LIMIT $limit
                        """,
                        workspace_id=workspace_id,
                        namespace=namespace,
                        query=query,
                        limit=limit,
                    )
                    results = []
                    for record in records:
                        results.append(
                            {
                                "node_id": record["node_id"],
                                "node_type": "source",
                                "path": record["path"],
                                "content_class": record["content_class"],
                                "relationships": ["chunks", *record["chunk_ids"]],
                                "strategy": "neo4j",
                            }
                        )
                    if results:
                        return results
        except Exception:
            pass

        with SessionLocal() as session:
            results = graph_candidates(session, workspace_id, namespace, query, limit)
        for item in results:
            item["strategy"] = "control_plane_fallback"
        return results
