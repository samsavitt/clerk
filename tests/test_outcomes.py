from __future__ import annotations

import json

import pytest

from clerk.logger import ValidationError, log
from clerk.outcomes import OUTCOME_ACTION_TYPE, OUTCOME_AGENT, attach_outcome


def decision_entry():
    return {
        "id": "decision-001",
        "agent": "memex-ingest",
        "action_type": "ingest-classify",
        "input": {"ref": "raw/inbox/source.md"},
        "decision": "ingest-and-update",
        "reason": "Primary source fills an existing research gap.",
        "provenance": ["raw/inbox/source.md"],
    }


def test_attach_outcome_returns_separate_entry_without_mutating_parent():
    source = decision_entry()
    original = json.loads(json.dumps(source))

    outcome = attach_outcome(
        source,
        "accepted",
        reason="Human review accepted the proposed wiki update.",
        outcome_ref="runs/review/proposals/source.md",
        reviewer="sam",
        occurred_at="2026-05-14T17:00:00Z",
    )

    assert source == original
    assert outcome["agent"] == OUTCOME_AGENT
    assert outcome["action_type"] == OUTCOME_ACTION_TYPE
    assert outcome["parent_id"] == source["id"]
    assert outcome["input"]["ref"] == source["id"]
    assert outcome["input"]["decision"] == source["decision"]
    assert outcome["input"]["outcome_ref"] == "runs/review/proposals/source.md"
    assert outcome["decision"] == "accepted"
    assert outcome["provenance"] == [source["id"], "runs/review/proposals/source.md"]
    assert "accepted" in outcome["tags"]


def test_attach_outcome_entry_is_loggable(tmp_path):
    source = decision_entry()
    outcome = attach_outcome(
        source,
        "rejected",
        reason="Human review rejected it as duplicative.",
    )
    path = tmp_path / "runs" / "review" / "trajectory.jsonl"

    written = log(outcome, log_path=path)

    assert written["schema"] == "clerk/v1"
    assert written["parent_id"] == source["id"]
    assert json.loads(path.read_text())["decision"] == "rejected"


def test_attach_outcome_accepts_parent_id_string():
    outcome = attach_outcome(
        "decision-002",
        "later-useful",
        reason="The rejected source became useful after a later synthesis gap appeared.",
    )

    assert outcome["parent_id"] == "decision-002"
    assert outcome["input"] == {"ref": "decision-002", "outcome": "later-useful"}
    assert outcome["decision"] == "later-useful"


@pytest.mark.parametrize(
    "outcome",
    ["approved", "useful-later", "", "ACCEPTED"],
)
def test_attach_outcome_rejects_unknown_outcomes(outcome):
    with pytest.raises(ValidationError):
        attach_outcome(decision_entry(), outcome, reason="Some reason.")


@pytest.mark.parametrize(
    "parent",
    [{}, {"id": ""}, {"id": 123}, ""],
)
def test_attach_outcome_requires_parent_id(parent):
    with pytest.raises(ValidationError):
        attach_outcome(parent, "accepted", reason="Some reason.")


@pytest.mark.parametrize("reason", ["", "   ", 123])
def test_attach_outcome_requires_reason(reason):
    with pytest.raises(ValidationError):
        attach_outcome(decision_entry(), "accepted", reason=reason)
