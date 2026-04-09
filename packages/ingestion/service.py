from datetime import UTC, datetime
from pathlib import Path

from packages.core.ids import make_id
from packages.core.models.contracts import SourceEnvelope
from packages.ingestion.classifier import classify_source
from packages.ingestion.parsers.registry import parse_source


class IngestionService:
    def ingest_path(
        self,
        workspace_id: str,
        path: str,
        namespace: str = "project",
        principal_id: str = "local.operator",
    ) -> dict[str, object]:
        file_path = Path(path)
        raw_text = file_path.read_text(encoding="utf-8", errors="ignore")
        content_hash = f"sha256:{abs(hash(raw_text))}"
        source = SourceEnvelope(
            source_id=make_id("src"),
            workspace_id=workspace_id,
            namespace=namespace,
            principal_id=principal_id,
            source_type="repository_file",
            content_class=classify_source(file_path),
            path=str(file_path),
            raw_content_ref=None,
            content_hash=content_hash,
            mime_type="text/plain",
            ingested_at=datetime.now(UTC),
        )
        parsed = parse_source(file_path, raw_text)
        chunks = self._chunk_text(raw_text, file_path.suffix.lower())
        return {
            "source": source.model_dump(mode="json"),
            "parsed": parsed,
            "chunks": chunks,
            "graph_write": {
                "status": "planned",
                "nodes": max(1, len(chunks)),
                "relationships": max(0, len(chunks) - 1),
            },
            "vector_write": {
                "status": "planned",
                "collection": "memory_documents",
                "documents": len(chunks),
            },
            "status": "parsed",
        }

    def ingest_repository(
        self,
        workspace_id: str,
        path: str,
        namespace: str = "project",
        principal_id: str = "local.operator",
    ) -> dict[str, object]:
        base_path = Path(path)
        files = [candidate for candidate in base_path.rglob("*") if candidate.is_file()]
        supported = [
            str(candidate)
            for candidate in files
            if candidate.suffix.lower() in {".py", ".md", ".mdx", ".yml", ".yaml", ".json"}
        ][:20]
        return {
            "workspace_id": workspace_id,
            "namespace": namespace,
            "principal_id": principal_id,
            "path": str(base_path),
            "files_considered": len(files),
            "files_supported": supported,
            "status": "queued_repo_ingest",
        }

    def _chunk_text(self, text: str, suffix: str) -> list[dict[str, object]]:
        if suffix in {".md", ".mdx"}:
            segments = [segment.strip() for segment in text.split("\n#") if segment.strip()]
        else:
            segments = [segment.strip() for segment in text.split("\n\n") if segment.strip()]
        chunks = []
        for index, segment in enumerate(segments[:20], start=1):
            chunks.append({"chunk_id": make_id(f"chunk{index}"), "text": segment[:500], "order": index})
        return chunks or [{"chunk_id": make_id("chunk1"), "text": text[:500], "order": 1}]
