from pathlib import Path

from packages.ingestion.service import IngestionService
from packages.retrieval.service import RetrievalService
from packages.storage.db import SessionLocal, init_db
from packages.storage.models import SourceRecord


init_db()


def test_ingest_markdown_file(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.md"
    file_path.write_text("# Title\n\nBody", encoding="utf-8")

    result = IngestionService().ingest_path("proj_alpha", str(file_path))

    assert result["source"]["workspace_id"] == "proj_alpha"
    assert result["parsed"]["kind"] == "markdown"
    assert result["chunks"]
    assert result["graph_write"]["status"] in {"persisted", "fallback"}
    assert result["vector_write"]["status"] in {"persisted", "fallback"}
    with SessionLocal() as session:
        assert session.get(SourceRecord, result["source"]["source_id"]) is not None


def test_ingest_python_file(tmp_path: Path) -> None:
    file_path = tmp_path / "app.py"
    file_path.write_text("import os\n\nclass Demo:\n    pass\n\ndef run():\n    return 1\n", encoding="utf-8")

    result = IngestionService().ingest_path("proj_alpha", str(file_path))

    assert result["parsed"]["kind"] == "python_ast"
    assert "Demo" in result["parsed"]["classes"]
    assert "run" in result["parsed"]["functions"]


def test_retrieval_uses_ingested_chunks(tmp_path: Path) -> None:
    file_path = tmp_path / "runbook.md"
    file_path.write_text("# Deploy\n\nHow to deploy MemCortex safely.", encoding="utf-8")

    IngestionService().ingest_path("proj_alpha", str(file_path))
    result = RetrievalService().resolve_context(
        workspace_id="proj_alpha",
        task="how to deploy memcortex",
        namespace="project",
        principal_id="local.operator",
    )

    assert result["query_classification"]["modes"]
    assert result["chunks"]
    assert any("deploy" in chunk["text"].lower() for chunk in result["chunks"])
