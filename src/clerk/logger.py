"""Append-only JSONL decision logger."""

from __future__ import annotations

import json
import os
import secrets
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "clerk/v1"
MAX_ATOMIC_WRITE_BYTES = 4096

REQUIRED_FIELDS = {
    "schema": str,
    "id": str,
    "ts": str,
    "agent": str,
    "action_type": str,
    "input": dict,
    "decision": str,
    "reason": str,
}

OPTIONAL_FIELDS = {
    "provenance": list,
    "scores": dict,
    "gate_outcome": str,
    "proposal_path": str,
    "parent_id": str,
    "tags": list,
    "human_review": dict,
}


class ValidationError(ValueError):
    """Raised when an entry does not satisfy Clerk's logger contract."""


def log(entry: dict[str, Any], log_path: str | os.PathLike[str]) -> dict[str, Any]:
    """Validate and append one entry to ``log_path`` as JSONL."""

    written = _prepare_entry(entry)
    line = json.dumps(written, separators=(",", ":"), ensure_ascii=False) + "\n"
    data = line.encode("utf-8")

    if len(data) > MAX_ATOMIC_WRITE_BYTES:
        raise ValidationError(
            f"serialized entry is {len(data)} bytes; limit is {MAX_ATOMIC_WRITE_BYTES}"
        )

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        bytes_written = os.write(fd, data)
        if bytes_written != len(data):
            raise OSError(f"short write: wrote {bytes_written} of {len(data)} bytes")
    finally:
        os.close(fd)

    return written


def _prepare_entry(entry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValidationError("entry must be a JSON object")

    written = dict(entry)
    written.setdefault("schema", SCHEMA)
    written.setdefault("id", _uuid7())
    written.setdefault("ts", _utc_now())
    _validate(written)
    return written


def _validate(entry: dict[str, Any]) -> None:
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in entry:
            raise ValidationError(f"missing required field: {field}")
        if not isinstance(entry[field], expected_type):
            raise ValidationError(
                f"field {field!r} must be {expected_type.__name__}, "
                f"got {type(entry[field]).__name__}"
            )

    for field, expected_type in OPTIONAL_FIELDS.items():
        if field in entry and not isinstance(entry[field], expected_type):
            raise ValidationError(
                f"field {field!r} must be {expected_type.__name__}, "
                f"got {type(entry[field]).__name__}"
            )

    _validate_string_array(entry, "provenance")
    _validate_string_array(entry, "tags")


def _validate_string_array(entry: dict[str, Any], field: str) -> None:
    if field not in entry:
        return
    if not all(isinstance(value, str) for value in entry[field]):
        raise ValidationError(f"field {field!r} must contain only strings")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _uuid7() -> str:
    unix_ms = int(time.time_ns() // 1_000_000) & ((1 << 48) - 1)
    rand_a = secrets.randbits(12)
    rand_b = secrets.randbits(62)
    value = (
        (unix_ms << 80)
        | (0x7 << 76)
        | (rand_a << 64)
        | (0b10 << 62)
        | rand_b
    )
    return str(uuid.UUID(int=value))
