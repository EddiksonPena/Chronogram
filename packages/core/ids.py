from datetime import UTC, datetime


def make_id(prefix: str) -> str:
    return f"{prefix}_{int(datetime.now(UTC).timestamp() * 1000)}"
