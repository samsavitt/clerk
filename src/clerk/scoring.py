"""Decision-accountability scoring for Clerk entries."""

from __future__ import annotations

import json
from typing import Any

from .logger import ValidationError

REVIEW_ACTION_TYPE = "decision-accountability-review"
REVIEW_AGENT = "clerk-scorer"
REVIEW_LABELS = ("none", "spot-check", "human-review", "block-until-reviewed")


def score(
    entry: dict[str, Any], context: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Return a separate review entry for a logged decision."""

    context = context or {}
    parent_id = _required_string(entry, "id")
    reason = _optional_string(entry, "reason")
    decision = _optional_string(entry, "decision")

    scores = {
        "rationale_clarity": _rationale_clarity(reason, decision, context),
        "provenance_sufficiency": _provenance_sufficiency(entry),
        "criterion_fit": _criterion_fit(entry, context),
        "risk_visibility": _risk_visibility(entry, context),
        "outcome_attachability": _outcome_attachability(entry, context),
    }
    scores["review_need"] = _review_need(scores)

    return {
        "agent": REVIEW_AGENT,
        "action_type": REVIEW_ACTION_TYPE,
        "input": {
            "ref": parent_id,
            "agent": _optional_string(entry, "agent"),
            "action_type": _optional_string(entry, "action_type"),
            "decision": decision,
        },
        "parent_id": parent_id,
        "decision": "reviewed",
        "reason": _review_reason(scores),
        "scores": scores,
        "provenance": [parent_id],
        "tags": ["clerk", "decision-accountability-review"],
    }


def _required_string(entry: dict[str, Any], field: str) -> str:
    value = entry.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"entry field {field!r} must be a non-empty string")
    return value


def _optional_string(entry: dict[str, Any], field: str) -> str:
    value = entry.get(field, "")
    return value if isinstance(value, str) else ""


def _rationale_clarity(
    reason: str, decision: str, context: dict[str, Any]
) -> float:
    reason_text = reason.strip()
    if not reason_text:
        return 0.0

    score_value = 0.0
    if len(reason_text.split()) >= 8:
        score_value += 0.35
    if decision and reason_text.lower() != decision.lower():
        score_value += 0.2
    if _contains_any(reason_text, _context_terms(context, "rationale_terms")):
        score_value += 0.25
    if any(mark in reason_text.lower() for mark in ("because", "so ", "therefore", "but", "lacks", "introduces", "contradict")):
        score_value += 0.2
    return _clamp(score_value)


def _provenance_sufficiency(entry: dict[str, Any]) -> float:
    provenance = entry.get("provenance")
    score_value = 0.0
    if isinstance(provenance, list) and provenance:
        score_value += 0.6
        if all(isinstance(item, str) and item.strip() for item in provenance):
            score_value += 0.2
    if _has_input_ref(entry) or isinstance(entry.get("proposal_path"), str):
        score_value += 0.2
    return _clamp(score_value)


def _criterion_fit(entry: dict[str, Any], context: dict[str, Any]) -> float:
    material = _entry_material(entry)
    terms = _context_terms(context, "criterion_terms")
    if terms:
        matches = sum(1 for term in terms if term.lower() in material)
        return _clamp(0.35 + (0.25 * matches))

    score_value = 0.0
    if _optional_string(entry, "action_type"):
        score_value += 0.3
    if _optional_string(entry, "decision"):
        score_value += 0.3
    if "scores" in entry or "gate_outcome" in entry:
        score_value += 0.2
    if _optional_string(entry, "reason"):
        score_value += 0.2
    return _clamp(score_value)


def _risk_visibility(entry: dict[str, Any], context: dict[str, Any]) -> float:
    material = _entry_material(entry)
    terms = _context_terms(context, "risk_terms")
    score_value = 0.0
    if isinstance(entry.get("gate_outcome"), str) or isinstance(entry.get("human_review"), dict):
        score_value += 0.35
    if any(mark in material for mark in ("risk", "review", "held", "reject", "discard", "contradict", "safety", "blocked", "not allowed")):
        score_value += 0.35
    if terms and any(term.lower() in material for term in terms):
        score_value += 0.3
    return _clamp(score_value)


def _outcome_attachability(entry: dict[str, Any], context: dict[str, Any]) -> float:
    score_value = 0.0
    if _optional_string(entry, "id"):
        score_value += 0.2
    if _has_input_ref(entry):
        score_value += 0.25
    if isinstance(entry.get("proposal_path"), str):
        score_value += 0.2
    if isinstance(entry.get("tags"), list) and entry["tags"]:
        score_value += 0.1
    if context.get("outcome_window") or context.get("outcome_ref") or context.get("outcome_fields"):
        score_value += 0.25
    return _clamp(score_value)


def _review_need(scores: dict[str, Any]) -> str:
    numeric = [
        value for key, value in scores.items() if key != "review_need" and isinstance(value, float)
    ]
    if any(value < 0.35 for value in numeric):
        return "block-until-reviewed"
    if any(value < 0.6 for value in numeric):
        return "human-review"
    if any(value < 0.8 for value in numeric):
        return "spot-check"
    return "none"


def _review_reason(scores: dict[str, Any]) -> str:
    label = scores["review_need"]
    if label == "none":
        return "Decision accountability review complete; all dimensions meet the no-review threshold."

    weak = [
        key
        for key, value in scores.items()
        if key != "review_need" and isinstance(value, float) and value < 0.8
    ]
    weakest = ", ".join(weak) if weak else "no dimension below threshold"
    return (
        f"Decision accountability review complete; review dimensions needing attention: {weakest}; "
        f"and review recommendation is {label}."
    )


def _context_terms(context: dict[str, Any], key: str) -> list[str]:
    terms = context.get(key, [])
    if isinstance(terms, str):
        return [terms]
    if isinstance(terms, list):
        return [term for term in terms if isinstance(term, str) and term.strip()]
    return []


def _contains_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term.lower() in lower for term in terms)


def _has_input_ref(entry: dict[str, Any]) -> bool:
    value = entry.get("input")
    return isinstance(value, dict) and isinstance(value.get("ref"), str)


def _entry_material(entry: dict[str, Any]) -> str:
    return json.dumps(entry, sort_keys=True, default=str).lower()


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 2)
