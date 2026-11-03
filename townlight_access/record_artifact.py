"""Complete, deterministic Access records; source content is data, never markup."""

from __future__ import annotations

from datetime import date, datetime
import hashlib
import json
from typing import Any


def _json_value(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    raise TypeError(f"Unsupported record value: {type(value).__name__}")


def build_record_artifact(record: dict[str, Any]) -> dict[str, str]:
    """Keep all supplied record fields and produce verifiable UTF-8 Markdown."""
    payload = json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2, default=_json_value)
    # Escape potential Markdown/HTML delimiters without changing JSON values.
    payload = payload.replace("`", "\\u0060").replace("<", "\\u003c")
    content = f"# Townlight Access record\n\n```json\n{payload}\n```\n"
    return {"content": content, "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}
