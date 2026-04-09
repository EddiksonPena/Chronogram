def parse_markdown(text: str) -> dict[str, object]:
    headings = [line.strip() for line in text.splitlines() if line.strip().startswith("#")]
    paragraphs = len([line for line in text.splitlines() if line.strip()])
    return {
        "kind": "markdown",
        "headings": headings,
        "paragraphs": paragraphs,
        "length": len(text),
    }
