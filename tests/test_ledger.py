from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from clerk.ledger import build_report, load_entries, render_markdown
from clerk.logger import log
from clerk.outcomes import attach_outcome
from clerk.scoring import score


def cli_env():
    import os

    env = os.environ.copy()
    src_path = str(Path(__file__).parents[1] / "src")
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src_path if not existing else f"{src_path}{os.pathsep}{existing}"
    return env


def decision(ref: str, **overrides):
    entry = {
        "agent": "memex-ingest",
        "action_type": "ingest-classify",
        "input": {
            "ref": ref,
            "risk": "Could update the wrong page.",
            "reversibility": "medium",
            "outcome_window": "after review",
            "reviewer_question": "Is this the right target page?",
        },
        "decision": "ingest-and-update",
        "reason": "The source fills an explicit gap in the existing page.",
        "provenance": ["wiki/INDEX.md"],
        "proposal_path": "runs/demo/proposals/source.md",
    }
    entry.update(overrides)
    return entry


def test_build_report_groups_decisions_reviews_and_outcomes(tmp_path):
    path = tmp_path / "trajectory.jsonl"
    first = log(decision("raw/inbox/a.md"), path)
    log(score(first), path)
    log(attach_outcome(first, "accepted", reason="Human accepted it."), path)
    second = log(decision("raw/inbox/b.md"), path)
    log(score(second), path)

    report = build_report(load_entries(path))

    assert report["decision_count"] == 2
    assert report["review_count"] == 2
    assert report["outcome_count"] == 1
    assert report["decisions"][0]["outcome"] == "accepted"
    assert report["decisions"][1]["outcome"] == ""
    assert report["unresolved_reviewer_questions"] == [
        {
            "id": second["id"],
            "input_ref": "raw/inbox/b.md",
            "question": "Is this the right target page?",
        }
    ]


def test_render_markdown_includes_summary_and_unresolved_questions(tmp_path):
    path = tmp_path / "trajectory.jsonl"
    entry = log(decision("raw/inbox/a.md"), path)
    log(score(entry), path)

    markdown = render_markdown(build_report(load_entries(path)))

    assert "# Clerk Ledger Report" in markdown
    assert "- Decisions: 1" in markdown
    assert "| raw/inbox/a.md | ingest-and-update |" in markdown
    assert "`raw/inbox/a.md`: Is this the right target page?" in markdown


def test_cli_report_prints_markdown(tmp_path):
    path = tmp_path / "trajectory.jsonl"
    entry = log(decision("raw/inbox/a.md"), path)
    log(score(entry), path)
    log(attach_outcome(entry, "accepted", reason="Human accepted it."), path)

    result = subprocess.run(
        [sys.executable, "-m", "clerk.cli", "report", str(path)],
        text=True,
        capture_output=True,
        env=cli_env(),
        check=False,
    )

    assert result.returncode == 0
    assert "# Clerk Ledger Report" in result.stdout
    assert "raw/inbox/a.md" in result.stdout
    assert "- None" in result.stdout
    assert result.stderr == ""


def test_load_entries_rejects_non_object_lines(tmp_path):
    path = tmp_path / "trajectory.jsonl"
    path.write_text(json.dumps(["not", "an", "object"]) + "\n")

    try:
        load_entries(path)
    except ValueError as exc:
        assert "must be a JSON object" in str(exc)
    else:
        raise AssertionError("expected ValueError")
