import json

import yaml


def parse_yaml_json(text: str, suffix: str) -> dict[str, object]:
    if suffix == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    keys = sorted(data.keys()) if isinstance(data, dict) else []
    return {"kind": "structured_config", "keys": keys, "is_mapping": isinstance(data, dict)}
