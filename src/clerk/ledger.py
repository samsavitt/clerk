"""Read-only ledger reporting for Clerk JSONL logs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .outcomes import OUTCOME_ACTION_TYPE
from .scoring import REVIEW_ACTION_TYPE


def load_entries(log_path: str | Path) -> list[dict[str, Any]]:
    """Load a Clerk JSONL ledger."""

    path = Path(log_path)
    entries = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on line {line_number}: {exc}") from exc
        if not isinstance(entry, dict):
            raise ValueError(f"ledger line {line_number} must be a JSON object")
        entries.append(entry)
    return entries


def build_report(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Group decisions with review and outcome entries."""

    decisions = {
        entry["id"]: entry
        for entry in entries
        if isinstance(entry.get("id"), str)
        and entry.get("action_type") not in {REVIEW_ACTION_TYPE, OUTCOME_ACTION_TYPE}
    }
    reviews = _children_by_parent(entries, REVIEW_ACTION_TYPE)
    outcomes = _children_by_parent(entries, OUTCOME_ACTION_TYPE)

    rows = []
    unresolved_questions = []
    for decision_id, decision in decisions.items():
        decision_reviews = reviews.get(decision_id, [])
        decision_outcomes = outcomes.get(decision_id, [])
        question = _contract_field(decision, "reviewer_question")
        if question and not decision_outcomes:
            unresolved_questions.append(
                {
                    "id": decision_id,
                    "input_ref": _input_ref(decision),
                    "question": question,
                }
            )
        rows.append(
            {
                "id": decision_id,
                "input_ref": _input_ref(decision),
                "decision": _string(decision.get("decision")),
                "review_need": _latest_review_need(decision_reviews),
                "outcome": _latest_outcome(decision_outcomes),
                "reviewer_question": question,
                "proposal_path": _string(decision.get("proposal_path")),
                "review_count": len(decision_reviews),
                "outcome_count": len(decision_outcomes),
            }
        )

    return {
        "decision_count": len(decisions),
        "review_count": sum(len(items) for items in reviews.values()),
        "outcome_count": sum(len(items) for items in outcomes.values()),
        "decisions": rows,
        "unresolved_reviewer_questions": unresolved_questions,
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render a compact Markdown report."""

    lines = [
        "# Clerk Ledger Report",
        "",
        "## Summary",
        "",
        f"- Decisions: {report['decision_count']}",
        f"- Reviews: {report['review_count']}",
        f"- Outcomes: {report['outcome_count']}",
        "",
        "## Decisions",
        "",
        "| Input | Decision | Review need | Outcome | Reviewer question |",
        "|---|---|---|---|---|",
    ]
    for row in report["decisions"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_cell(row["input_ref"]),
                    _md_cell(row["decision"]),
                    _md_cell(row["review_need"]),
                    _md_cell(row["outcome"]),
                    _md_cell(row["reviewer_question"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Unresolved Reviewer Questions", ""])
    unresolved = report["unresolved_reviewer_questions"]
    if unresolved:
        for item in unresolved:
            lines.append(f"- `{item['input_ref']}`: {item['question']}")
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def _children_by_parent(
    entries: list[dict[str, Any]], action_type: str
) -> dict[str, list[dict[str, Any]]]:
    children: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        if entry.get("action_type") != action_type:
            continue
        parent_id = entry.get("parent_id")
        if isinstance(parent_id, str) and parent_id:
            children.setdefault(parent_id, []).append(entry)
    return children


def _latest_review_need(reviews: list[dict[str, Any]]) -> str:
    if not reviews:
        return ""
    value = reviews[-1].get("scores", {}).get("review_need")
    return _string(value)


def _latest_outcome(outcomes: list[dict[str, Any]]) -> str:
    if not outcomes:
        return ""
    return _string(outcomes[-1].get("decision"))


def _input_ref(entry: dict[str, Any]) -> str:
    input_data = entry.get("input")
    if isinstance(input_data, dict):
        return _string(input_data.get("ref"))
    return ""


def _contract_field(entry: dict[str, Any], field: str) -> str:
    input_data = entry.get("input")
    if isinstance(input_data, dict) and isinstance(input_data.get(field), str):
        return input_data[field]
    if isinstance(entry.get(field), str):
        return entry[field]
    return ""


def _string(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _md_cell(value: str) -> str:
    return (value or "").replace("|", "\\|").replace("\n", " ")
