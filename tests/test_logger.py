from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from clerk.logger import MAX_ATOMIC_WRITE_BYTES, ValidationError, log

UUID7_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def entry(**overrides):
    base = {
        "agent": "memex-ingest",
        "action_type": "ingest-classify",
        "input": {"ref": "raw/inbox/x.md"},
        "decision": "discard",
        "reason": "duplicate",
    }
    base.update(overrides)
    return base


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def cli_env():
    env = os.environ.copy()
    src_path = str(Path(__file__).parents[1] / "src")
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src_path if not existing else f"{src_path}{os.pathsep}{existing}"
    return env


def test_log_auto_fills_required_metadata(tmp_path):
    path = tmp_path / "runs" / "demo" / "trajectory.jsonl"

    written = log(entry(), log_path=path)

    assert written["schema"] == "clerk/v1"
    assert UUID7_RE.match(written["id"])
    assert written["ts"].endswith("Z")
    assert read_jsonl(path) == [written]


def test_log_preserves_caller_metadata(tmp_path):
    path = tmp_path / "trajectory.jsonl"
    supplied = entry(schema="custom/v1", id="entry-001", ts="2026-05-13T19:42:11Z")

    written = log(supplied, log_path=path)

    assert written["schema"] == "custom/v1"
    assert written["id"] == "entry-001"
    assert written["ts"] == "2026-05-13T19:42:11Z"


@pytest.mark.parametrize(
    "field",
    ["agent", "action_type", "input", "decision", "reason"],
)
def test_required_field_missing_refuses_without_touching_log(tmp_path, field):
    path = tmp_path / "trajectory.jsonl"
    payload = entry()
    payload.pop(field)

    with pytest.raises(ValidationError, match=f"missing required field: {field}"):
        log(payload, log_path=path)

    assert not path.exists()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema", 1),
        ("id", 1),
        ("ts", 1),
        ("agent", 1),
        ("action_type", 1),
        ("input", []),
        ("decision", 1),
        ("reason", 1),
        ("provenance", ["ok", 2]),
        ("scores", []),
        ("gate_outcome", 1),
        ("proposal_path", 1),
        ("parent_id", 1),
        ("tags", ["ok", 2]),
        ("human_review", []),
    ],
)
def test_wrong_typed_fields_are_refused(tmp_path, field, value):
    path = tmp_path / "trajectory.jsonl"

    with pytest.raises(ValidationError):
        log(entry(**{field: value}), log_path=path)

    assert not path.exists()


def test_refuses_entries_over_atomic_write_limit(tmp_path):
    path = tmp_path / "trajectory.jsonl"
    payload = entry(reason="x" * MAX_ATOMIC_WRITE_BYTES)

    with pytest.raises(ValidationError, match="serialized entry"):
        log(payload, log_path=path)

    assert not path.exists()


def test_concurrent_writes_accumulate_valid_jsonl(tmp_path):
    path = tmp_path / "runs" / "concurrent" / "trajectory.jsonl"

    with ThreadPoolExecutor(max_workers=8) as executor:
        written = list(
            executor.map(
                lambda i: log(entry(input={"ref": f"item-{i}"}), log_path=path),
                range(30),
            )
        )

    rows = read_jsonl(path)
    assert len(rows) == 30
    assert {row["id"] for row in rows} == {row["id"] for row in written}
    assert {row["input"]["ref"] for row in rows} == {f"item-{i}" for i in range(30)}


def test_cli_writes_entry_and_prints_written_json(tmp_path):
    path = tmp_path / "runs" / "cli" / "trajectory.jsonl"
    payload = json.dumps(entry())

    result = subprocess.run(
        [sys.executable, "-m", "clerk.cli", "log", "--to", str(path)],
        input=payload,
        text=True,
        capture_output=True,
        env=cli_env(),
        check=False,
    )

    assert result.returncode == 0
    written = json.loads(result.stdout)
    assert read_jsonl(path) == [written]
    assert result.stderr == ""


def test_cli_validation_failure_exits_2_without_writing(tmp_path):
    path = tmp_path / "trajectory.jsonl"

    result = subprocess.run(
        [sys.executable, "-m", "clerk.cli", "log", "--to", str(path)],
        input=json.dumps({"agent": "memex-ingest"}),
        text=True,
        capture_output=True,
        env=cli_env(),
        check=False,
    )

    assert result.returncode == 2
    assert "missing required field" in result.stderr
    assert not path.exists()
