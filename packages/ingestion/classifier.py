from pathlib import Path


def classify_source(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return "source_code"
    if suffix in {".md", ".mdx"}:
        return "markdown_doc"
    if suffix in {".yaml", ".yml", ".json"}:
        return "config"
    return "text"
