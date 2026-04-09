from hashlib import sha256
from uuid import NAMESPACE_URL, uuid5

import httpx

from packages.core.settings import settings
from packages.storage.db import SessionLocal
from packages.storage.repositories import search_chunks


class VectorService:
    def upsert_chunks(
        self,
        source: dict[str, object],
        chunks: list[dict[str, object]],
    ) -> dict[str, object]:
        try:
            self._ensure_schema()
            with httpx.Client(base_url=settings.weaviate_url, timeout=5.0) as client:
                for chunk in chunks:
                    payload = {
                        "class": settings.weaviate_collection_name,
                        "id": str(uuid5(NAMESPACE_URL, chunk["chunk_id"])),
                        "properties": {
                            "chunk_id": chunk["chunk_id"],
                            "source_id": source["source_id"],
                            "workspace_id": source["workspace_id"],
                            "namespace": source["namespace"],
                            "content_class": source["content_class"],
                            "text": chunk["text"],
                        },
                        "vector": self._embed(chunk["text"]),
                    }
                    response = client.post("/v1/objects", json=payload)
                    if response.status_code not in {200, 201, 422}:
                        response.raise_for_status()
                return {
                    "status": "persisted",
                    "backend": "weaviate",
                    "collection": settings.weaviate_collection_name,
                    "documents": len(chunks),
                }
        except Exception as exc:
            return {
                "status": "fallback",
                "backend": "control_plane",
                "collection": settings.weaviate_collection_name,
                "documents": len(chunks),
                "reason": str(exc),
            }

    def search(self, workspace_id: str, namespace: str, query: str, limit: int = 5) -> list[dict[str, object]]:
        try:
            results = self._search_weaviate(workspace_id, namespace, query, limit)
            if results:
                return results
        except Exception:
            pass

        with SessionLocal() as session:
            chunks = search_chunks(session, workspace_id, namespace, query, limit)
        results = []
        for chunk in chunks:
            results.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "source_id": chunk["source_id"],
                    "text": chunk["text"],
                    "score": 0.66,
                    "strategy": "lexical_fallback",
                    "content_class": chunk["content_class"],
                }
            )
        return results

    def _ensure_schema(self) -> None:
        with httpx.Client(base_url=settings.weaviate_url, timeout=5.0) as client:
            response = client.get(f"/v1/schema/{settings.weaviate_collection_name}")
            if response.status_code == 200:
                return
            schema = {
                "class": settings.weaviate_collection_name,
                "vectorizer": "none",
                "properties": [
                    {"name": "chunk_id", "dataType": ["text"]},
                    {"name": "source_id", "dataType": ["text"]},
                    {"name": "workspace_id", "dataType": ["text"]},
                    {"name": "namespace", "dataType": ["text"]},
                    {"name": "content_class", "dataType": ["text"]},
                    {"name": "text", "dataType": ["text"]},
                ],
            }
            create_response = client.post("/v1/schema", json=schema)
            if create_response.status_code not in {200, 201, 422}:
                create_response.raise_for_status()

    def _search_weaviate(
        self, workspace_id: str, namespace: str, query: str, limit: int
    ) -> list[dict[str, object]]:
        graphql_query = """
        {
          Get {
            %s(
              where: {
                operator: And,
                operands: [
                  {path: ["workspace_id"], operator: Equal, valueText: "%s"},
                  {path: ["namespace"], operator: Equal, valueText: "%s"}
                ]
              },
              nearVector: {vector: [%s]},
              limit: %d
            ) {
              chunk_id
              source_id
              text
              content_class
              _additional { distance id }
            }
          }
        }
        """ % (
            settings.weaviate_collection_name,
            workspace_id,
            namespace,
            ",".join(str(value) for value in self._embed(query)),
            limit,
        )
        with httpx.Client(base_url=settings.weaviate_url, timeout=5.0) as client:
            response = client.post("/v1/graphql", json={"query": graphql_query})
            response.raise_for_status()
            payload = response.json()["data"]["Get"].get(settings.weaviate_collection_name, [])
        return [
            {
                "chunk_id": item["chunk_id"],
                "source_id": item["source_id"],
                "text": item["text"],
                "score": round(1.0 - float(item["_additional"].get("distance", 1.0)), 4),
                "strategy": "weaviate",
                "content_class": item["content_class"],
            }
            for item in payload
        ]

    def _embed(self, text: str, dimensions: int = 16) -> list[float]:
        vector = [0.0] * dimensions
        for index, token in enumerate(text.lower().split()):
            digest = sha256(f"{index}:{token}".encode("utf-8")).digest()
            for dim in range(dimensions):
                vector[dim] += digest[dim] / 255.0
        magnitude = sum(value * value for value in vector) ** 0.5 or 1.0
        return [round(value / magnitude, 6) for value in vector]
