from __future__ import annotations

import json
from pathlib import Path

import pytest

from clerk.logger import ValidationError, log
from clerk.scoring import REVIEW_ACTION_TYPE, REVIEW_AGENT, score


def load_memex_fixtures():
    fixture_path = Path(__file__).parent / "fixtures" / "memex_compatibility.json"
    return json.loads(fixture_path.read_text())


def memex_context():
    return {
        "criterion_terms": [
            "tier",
            "source",
            "proposal",
            "duplicate",
            "contradiction",
        ],
        "rationale_terms": [
            "source",
            "existing",
            "primary",
            "social-grade",
            "lacks",
            "introduces",
        ],
        "risk_terms": [
            "low-grade",
            "contradiction",
            "review",
            "held",
        ],
        "outcome_window": "after human proposal review",
        "outcome_fields": ["accepted", "rejected", "later-useful"],
    }


def test_score_returns_separate_review_entry_without_mutating_source():
    source = load_memex_fixtures()[0]
    original = json.loads(json.dumps(source))

    review = score(source, context=memex_context())

    assert source == original
    assert review["agent"] == REVIEW_AGENT
    assert review["action_type"] == REVIEW_ACTION_TYPE
    assert review["parent_id"] == source["id"]
    assert review["input"]["ref"] == source["id"]
    assert review["decision"] == "reviewed"
    assert review["scores"]["review_need"] in {
        "none",
        "spot-check",
        "human-review",
        "block-until-reviewed",
    }


def test_score_review_entry_is_loggable(tmp_path):
    source = load_memex_fixtures()[1]
    review = score(source, context=memex_context())
    path = tmp_path / "runs" / "review" / "trajectory.jsonl"

    written = log(review, log_path=path)

    assert written["schema"] == "clerk/v1"
    assert written["parent_id"] == source["id"]
    assert json.loads(path.read_text())["parent_id"] == source["id"]


def test_score_memex_fixtures_without_judging_disposition_correctness():
    reviews = [score(entry, context=memex_context()) for entry in load_memex_fixtures()]

    assert [review["decision"] for review in reviews] == ["reviewed"] * 3
    assert {review["input"]["decision"] for review in reviews} == {
        "discard",
        "ingest-and-update",
        "flag-for-review-low-grade",
    }
    assert all("source_tier" not in review["scores"] for review in reviews)
    assert all("review_need" in review["scores"] for review in reviews)


def test_score_reason_names_dimensions_that_need_attention():
    source = load_memex_fixtures()[0]

    review = score(source, context=memex_context())

    assert review["scores"]["review_need"] == "spot-check"
    assert "risk_visibility" in review["reason"]
    assert "Missing explicit risk, reversibility field(s)" in review["reason"]


def test_score_reason_says_when_no_review_is_needed():
    source = load_memex_fixtures()[1]

    review = score(source, context=memex_context())

    assert review["scores"]["review_need"] == "none"
    assert "all dimensions meet" in review["reason"]


def test_score_uses_explicit_consumer_contract_fields_without_domain_rules():
    source = load_memex_fixtures()[1] | {
        "input": {
            **load_memex_fixtures()[1]["input"],
            "risk": "Could fragment existing synthesis if the proposal overlaps hidden coverage.",
            "reversibility": "medium",
            "outcome_window": "after human proposal review",
            "reviewer_question": "Does the proposal identify the right update target?",
        }
    }

    review = score(source, context=memex_context())

    assert review["scores"]["risk_visibility"] == 1.0
    assert "Missing explicit risk" not in review["reason"]
    assert "No reviewer_question" not in review["reason"]


@pytest.mark.parametrize("entry", [{}, {"id": ""}, {"id": 123}])
def test_score_requires_parent_entry_id(entry):
    with pytest.raises(ValidationError):
        score(entry)
