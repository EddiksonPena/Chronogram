from pathlib import Path

from packages.ingestion.service import IngestionService


def test_ingest_markdown_file(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.md"
    file_path.write_text("# Title\n\nBody", encoding="utf-8")

    result = IngestionService().ingest_path("proj_alpha", str(file_path))

    assert result["source"]["workspace_id"] == "proj_alpha"
    assert result["parsed"]["kind"] == "markdown"
    assert result["chunks"]


def test_ingest_python_file(tmp_path: Path) -> None:
    file_path = tmp_path / "app.py"
    file_path.write_text("import os\n\nclass Demo:\n    pass\n\ndef run():\n    return 1\n", encoding="utf-8")

    result = IngestionService().ingest_path("proj_alpha", str(file_path))

    assert result["parsed"]["kind"] == "python_ast"
    assert "Demo" in result["parsed"]["classes"]
    assert "run" in result["parsed"]["functions"]
