from pathlib import Path

from packages.ingestion.parsers.markdown import parse_markdown
from packages.ingestion.parsers.python_ast import parse_python
from packages.ingestion.parsers.yaml_json import parse_yaml_json


def parse_source(path: Path, text: str) -> dict[str, object]:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return parse_python(text)
    if suffix in {".md", ".mdx"}:
        return parse_markdown(text)
    if suffix in {".yaml", ".yml", ".json"}:
        return parse_yaml_json(text, suffix)
    return {"kind": "raw_text", "length": len(text)}
