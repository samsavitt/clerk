"""Outcome attachment for previously logged decisions."""

from __future__ import annotations

from typing import Any

from .logger import ValidationError

OUTCOME_ACTION_TYPE = "decision-outcome"
OUTCOME_AGENT = "clerk-outcome"
ALLOWED_OUTCOMES = {
    "accepted",
    "rejected",
    "later-useful",
    "reversed",
    "caused-correction",
    "human-disagreement",
    "unclear",
}


def attach_outcome(
    parent: dict[str, Any] | str,
    outcome: str,
    *,
    reason: str,
    outcome_ref: str | None = None,
    reviewer: str | None = None,
    occurred_at: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Return a separate outcome entry for a prior Clerk decision."""

    parent_id = _parent_id(parent)
    if outcome not in ALLOWED_OUTCOMES:
        allowed = ", ".join(sorted(ALLOWED_OUTCOMES))
        raise ValidationError(f"outcome must be one of: {allowed}")
    if not isinstance(reason, str) or not reason.strip():
        raise ValidationError("reason must be a non-empty string")

    input_data = {
        "ref": parent_id,
        "outcome": outcome,
    }
    if isinstance(parent, dict):
        input_data.update(
            {
                "agent": _optional_string(parent, "agent"),
                "action_type": _optional_string(parent, "action_type"),
                "decision": _optional_string(parent, "decision"),
            }
        )
    if outcome_ref:
        input_data["outcome_ref"] = outcome_ref
    if reviewer:
        input_data["reviewer"] = reviewer
    if occurred_at:
        input_data["occurred_at"] = occurred_at

    provenance = [parent_id]
    if outcome_ref:
        provenance.append(outcome_ref)

    merged_tags = ["clerk", "decision-outcome", outcome]
    if tags:
        merged_tags.extend(_string_list(tags, "tags"))

    return {
        "agent": OUTCOME_AGENT,
        "action_type": OUTCOME_ACTION_TYPE,
        "input": input_data,
        "parent_id": parent_id,
        "decision": outcome,
        "reason": reason.strip(),
        "scores": {"outcome": outcome},
        "provenance": provenance,
        "tags": merged_tags,
    }


def _parent_id(parent: dict[str, Any] | str) -> str:
    if isinstance(parent, str) and parent.strip():
        return parent
    if isinstance(parent, dict):
        value = parent.get("id")
        if isinstance(value, str) and value.strip():
            return value
    raise ValidationError("parent must be a non-empty entry id or entry with id")


def _optional_string(entry: dict[str, Any], field: str) -> str:
    value = entry.get(field, "")
    return value if isinstance(value, str) else ""


def _string_list(values: list[str], field: str) -> list[str]:
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise ValidationError(f"{field} must contain only non-empty strings")
    return values
