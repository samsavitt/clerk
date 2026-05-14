# Next

## Current state

- Project initialized 2026-05-13.
- Logger v0 implemented in Python:
  - `src/clerk/logger.py` exposes `log(entry, log_path=...)`.
  - `src/clerk/cli.py` exposes `clerk log --to <path>` when installed, and `python -m clerk.cli log --to <path>` from source.
  - `pyproject.toml` defines the package and console script.
- Scoring direction specified in `docs/scoring.md`: Clerk scoring is decision-accountability review, not domain evaluation.
- Consumer decision contract exists at `docs/decision-contract.md`; it defines recommended accountability fields for supervised decisions (`risk`, `reversibility`, `outcome_window`, and `reviewer_question`) without adding domain-specific rules.
- Non-invasive Memex compatibility fixtures exist in `tests/fixtures/memex_compatibility.json`; they verify Clerk can record Memex-style ingest decisions without importing Memex rules or touching Memex runtime.
- Scoring v0 implemented in `src/clerk/scoring.py`; it returns separate `decision-accountability-review` entries, never mutates the original decision, and now names concrete missing accountability fields in weak review reasons where possible.
- Outcome attachment v0 implemented in `src/clerk/outcomes.py`; it returns separate `decision-outcome` entries with `parent_id` pointing at the original decision and never mutates the original decision.
- Ledger report v0 implemented:
  - `src/clerk/ledger.py` groups original decisions, review entries, outcome entries, and unresolved reviewer questions.
  - `python -m clerk.cli report <ledger.jsonl>` prints a read-only Markdown report.
  - `docs/ledger.md` documents the helper.
- Ledger-usefulness review exists at `docs/reviews/ledger-usefulness-2026-05-14.md`.
- Controlled Memex dry-run Clerk trial completed; durable review is `docs/reviews/memex-dryrun-clerk-trial-2026-05-14.md`, with local ignored run artifacts at `runs/2026-05-14-memex-dryrun-clerk-trial/`:
  - Converted real Memex dry-run output from `/Users/samsavitt/Lab/memex/runs/2026-05-13-ingest-dryrun-001/trajectory.jsonl` into Clerk decision entries.
  - Appended Clerk `decision-accountability-review` entries and `decision-outcome` entries for each reviewed decision.
  - Review result: Clerk is useful enough to keep alive as a Lab prototype because it exposed missing risk/reversibility visibility, decision-row vs proposal-reasoning gaps, correction-causing accepted decisions, and clean outcome attachability that raw Memex logs did not make obvious.
- Controlled Memex contract dry-run trial completed; durable review is `docs/reviews/memex-contract-dryrun-clerk-trial-2026-05-14.md`, with local ignored run artifacts at `runs/2026-05-14-memex-contract-dryrun-clerk-trial/`:
  - Reused the same real Memex dry-run trajectory but added `docs/decision-contract.md` fields to each converted decision.
  - Result: explicit `risk`, `reversibility`, `outcome_window`, and `reviewer_question` fields removed the noisy missing-risk review flags.
  - Important boundary: CoEvoSkills scored as well-recorded (`review_need = none`) while its later outcome remained `caused-correction`, confirming Clerk reviews accountability quality rather than domain correctness.
- Ledger report v0 was run on both Memex trial ledgers:
  - `docs/reviews/memex-dryrun-ledger-report-2026-05-14.md`
  - `docs/reviews/memex-contract-dryrun-ledger-report-2026-05-14.md`
  - Result: the report makes the decision/review/outcome grouping easier to inspect than raw JSONL and makes the decision-contract improvement visible.
- Memex-side Clerk harness trial completed in `/Users/samsavitt/Lab/memex`:
  - `tools/clerk_harness_trial.py` converts Memex ingest trajectories into Clerk decision-contract ledgers and reports using this Clerk package from `../clerk/src`.
  - Trial run against Memex's existing dry-run trajectory grouped 3 decisions, 3 reviews, and 3 outcomes without test-vault or real-vault writes.
  - Next true proposal-batch trial is paused until Claude credits are refreshed or an alternate `--claude-bin` is supplied.
- Test harness exists in `tests/test_logger.py`.
- Verification on 2026-05-14: `python3 -m pytest` passed, 54 tests. Coverage includes required fields, auto-fill rules, wrong-type refusals, oversize-entry refusal, CLI success/failure, parent directory creation, 30-entry concurrent append behavior, Memex compatibility fixtures, scoring review entries, decision-contract field recognition, outcome attachment entries, ledger grouping, unresolved reviewer questions, and CLI report output.
- Origin context: extracted from the Memex substrate maintenance loop's trajectory log pattern. The cluster-synthesis (`vault:wiki/research/cluster-synthesis-2026-05-13.md`) identified "supervision layer for AI" as a cross-cluster meta-thesis; clerk is the standalone implementation of that thesis's load-bearing primitive (log + grade + gate).

## Next action

1. **While Memex is paused on Claude credits, optionally harden reliability.** Add golden-path and malformed-trajectory coverage around the Memex harness contract: missing `proposal`, missing/invalid `pages_read`, invalid JSONL, unknown disposition, empty trajectory, missing Clerk path, and report generation failure.
2. **After Claude is unblocked, run one fresh Memex proposal-batch trial.** Use `docs/decision-contract.md` and the Memex harness/report path only; do not add gates or runtime coupling.
3. **If the fresh trial is not more useful than raw logs, park Clerk at logger + scorer + outcomes + report v0 until another consumer needs accountability logging.**

Do not build gates, a review UI, or runtime integration until Clerk has a small report surface that proves the ledger is easier to review than raw agent logs.

## Open decisions

- **Language.** Resolved for v0: Python.
- **ID generation.** Resolved for v0: inline UUIDv7-compatible generation, no external dependency.
- **Log file path convention.** v0 accepts any explicit path and tests `runs/<run-id>/trajectory.jsonl`; confirm this convention during first consumer trial.
- **Scoring model.** Resolved for v0: separate append-only review entries, never mutation of the original decision entry.
- **Outcome model.** Resolved for v0: separate append-only outcome entries using a small shared label set, never mutation of the original decision entry.
- **Distribution.** Eventually clerk needs to be installable by other projects (Memex, Catalyst, Cortex). Decide: pip-installable package, vendored copy per consumer, or git submodule. Defer until logger is working.

## Vault context

- `vault:wiki/research/cluster-synthesis-2026-05-13.md` — identifies the measurement/governance layer as the cross-cluster thesis and Clerk as the primitive behind it.

## Kill / graduation criteria

- **Kill or park** if the logger cannot prove a clean, domain-neutral trajectory schema with simple tests.
- **Stay in Lab** until log + grade + gate are validated by at least one consumer.
- **Graduate to Studio** only if Clerk becomes an active shared package with real downstream integration work.

## Do not do

- Do not build the gate or review CLI before logger, scoring, and outcome attachment have been validated together in one consumer dry-run.
- Do not bake any Memex- or domain-specific assumptions into clerk's code. Domain-specific scoring rules live in the consumer, not in clerk itself.
- Do not touch x-growth while shaping Clerk's scoring contract. x-growth is active work and should not become a Clerk proving ground until Clerk earns integration.
- Do not wire Clerk into Memex runtime yet. Use fixtures/examples only until scoring v0 proves useful.
- Do not add a web UI in v1. CLI and Python library only.
- Do not add streaming-to-remote-storage, log rotation, or compression in v1. Those are operations concerns; clerk is a primitive.
- Do not commit any consumer-specific config (e.g., Memex's ingest prompt) into clerk.

## Origin and downstream consumers

Clerk is domain-neutral. Known and planned consumers:

- **Memex** — substrate maintenance agent. Already producing trajectory.jsonl entries by hand; will swap to clerk's logger once available.
- **Catalyst** (Cluster 1, not yet started) — content quality scoring.
- **Sentinel** (Cluster 2, not yet started) — AI governance.
- **Cortex** (Cluster 3, internal trading) — trade rationale logging.

Each consumer plugs in its own scoring functions and gate policies. Clerk itself does not import anything domain-specific.
