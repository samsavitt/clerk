from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from clerk.logger import JUDGMENT_SCHEMA, ValidationError, log

UUID7_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def judgment(**overrides):
    base = {
        "schema": JUDGMENT_SCHEMA,
        "domain": "trajectory-eval-gate",
        "authorizer_id": "reviewer-001",
        "inputs_hash": "a" * 64,
        "judgment_payload": {"verdict": "approve", "counterexample": None},
        "outcome_window": "7d",
    }
    base.update(overrides)
    return base


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_judgment_auto_fills_id_time_and_outcome_attached(tmp_path):
    path = tmp_path / "judgments.jsonl"

    written = log(judgment(), log_path=path)

    assert written["schema"] == JUDGMENT_SCHEMA
    assert UUID7_RE.match(written["judgment_id"])
    assert written["decision_time"].endswith("Z")
    assert written["outcome_attached"] is False
    assert read_jsonl(path) == [written]


def test_judgment_preserves_caller_metadata(tmp_path):
    path = tmp_path / "judgments.jsonl"
    supplied = judgment(
        judgment_id="j-001",
        decision_time="2026-05-20T10:00:00Z",
        outcome_attached=True,
    )

    written = log(supplied, log_path=path)

    assert written["judgment_id"] == "j-001"
    assert written["decision_time"] == "2026-05-20T10:00:00Z"
    assert written["outcome_attached"] is True


@pytest.mark.parametrize(
    "field",
    ["domain", "authorizer_id", "inputs_hash", "judgment_payload", "outcome_window"],
)
def test_judgment_required_field_missing_refuses(tmp_path, field):
    path = tmp_path / "judgments.jsonl"
    payload = judgment()
    payload.pop(field)

    with pytest.raises(ValidationError, match=f"missing required field: {field}"):
        log(payload, log_path=path)

    assert not path.exists()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("domain", 1),
        ("authorizer_id", 1),
        ("inputs_hash", 1),
        ("judgment_payload", []),
        ("judgment_payload", "approve"),
        ("outcome_window", 7),
        ("outcome_attached", "no"),
        ("outcome_attached", 0),
    ],
)
def test_judgment_wrong_typed_fields_refused(tmp_path, field, value):
    path = tmp_path / "judgments.jsonl"

    with pytest.raises(ValidationError):
        log(judgment(**{field: value}), log_path=path)

    assert not path.exists()


def test_judgment_optional_provenance_and_tags(tmp_path):
    path = tmp_path / "judgments.jsonl"

    written = log(
        judgment(provenance=["src-a", "src-b"], tags=["pilot"]),
        log_path=path,
    )

    assert written["provenance"] == ["src-a", "src-b"]
    assert written["tags"] == ["pilot"]


def test_judgment_does_not_require_decision_contract_fields(tmp_path):
    """Authorization judgments must not need the consumer contract fields."""

    path = tmp_path / "judgments.jsonl"
    written = log(judgment(), log_path=path)

    assert "agent" not in written
    assert "action_type" not in written
    assert "input" not in written
    assert "decision" not in written
    assert "reason" not in written


def test_existing_contract_still_works_alongside_judgment(tmp_path):
    """Backward compatibility: default schema entries must still validate."""

    path = tmp_path / "mixed.jsonl"
    log(
        {
            "agent": "memex-ingest",
            "action_type": "ingest-classify",
            "input": {"ref": "x"},
            "decision": "discard",
            "reason": "duplicate",
        },
        log_path=path,
    )
    log(judgment(), log_path=path)

    rows = read_jsonl(path)
    assert len(rows) == 2
    assert rows[0]["schema"] == "clerk/v1"
    assert rows[1]["schema"] == JUDGMENT_SCHEMA
