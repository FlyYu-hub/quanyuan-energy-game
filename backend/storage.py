from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


def _path(name: str) -> Path:
    if not name.endswith(".json"):
        name = f"{name}.json"
    return DATA_DIR / name


def read_json(name: str, default: Any | None = None) -> Any:
    path = _path(name)
    if default is None:
        default = []
    if not path.exists():
        write_json(name, default)
        return default
    try:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            return default
        return json.loads(text)
    except json.JSONDecodeError:
        backup = path.with_suffix(".broken.json")
        path.replace(backup)
        write_json(name, default)
        return default


def write_json(name: str, data: Any) -> None:
    path = _path(name)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def append_json_list(name: str, item: dict[str, Any]) -> list[dict[str, Any]]:
    data = read_json(name, [])
    if not isinstance(data, list):
        data = []
    data.append(item)
    write_json(name, data)
    return data


def clear_json_list(name: str) -> None:
    write_json(name, [])
