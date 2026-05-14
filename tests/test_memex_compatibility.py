from __future__ import annotations

import json
from pathlib import Path

from clerk.logger import log


def test_memex_compatibility_fixtures_log_without_domain_rules(tmp_path):
    fixtures_path = Path(__file__).parent / "fixtures" / "memex_compatibility.json"
    entries = json.loads(fixtures_path.read_text())
    log_path = tmp_path / "runs" / "memex-compatibility" / "trajectory.jsonl"

    written = [log(entry, log_path=log_path) for entry in entries]

    rows = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert rows == written
    assert {row["decision"] for row in rows} == {
        "discard",
        "ingest-and-update",
        "flag-for-review-low-grade",
    }
    assert all(row["agent"] == "memex-ingest" for row in rows)
    assert all(row["proposal_path"].startswith("runs/") for row in rows)
    assert all("source_tier" in row["scores"] for row in rows)
