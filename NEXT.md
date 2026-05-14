# Next

## Current state

- Project initialized 2026-05-13.
- Logger v0 implemented in Python:
  - `src/clerk/logger.py` exposes `log(entry, log_path=...)`.
  - `src/clerk/cli.py` exposes `clerk log --to <path>` when installed, and `python -m clerk.cli log --to <path>` from source.
  - `pyproject.toml` defines the package and console script.
- Scoring direction specified in `docs/scoring.md`: Clerk scoring is decision-accountability review, not domain evaluation.
- Non-invasive Memex compatibility fixtures exist in `tests/fixtures/memex_compatibility.json`; they verify Clerk can record Memex-style ingest decisions without importing Memex rules or touching Memex runtime.
- Test harness exists in `tests/test_logger.py`.
- Verification on 2026-05-14: `python3 -m pytest` passed, 27 tests. Coverage includes required fields, auto-fill rules, wrong-type refusals, oversize-entry refusal, CLI success/failure, parent directory creation, 30-entry concurrent append behavior, and Memex compatibility fixtures.
- Origin context: extracted from the Memex substrate maintenance loop's trajectory log pattern. The cluster-synthesis (`vault:wiki/research/cluster-synthesis-2026-05-13.md`) identified "supervision layer for AI" as a cross-cluster meta-thesis; clerk is the standalone implementation of that thesis's load-bearing primitive (log + grade + gate).

## Next action

1. **Implement scoring v0 as a pure library function.** It should receive one Clerk entry plus optional consumer-supplied context, and return a separate `decision-accountability-review` Clerk entry with `parent_id` pointing at the original.
2. **Test scoring v0 against the Memex fixtures.** The scorer should review record quality only: rationale clarity, provenance sufficiency, criterion fit, risk visibility, outcome attachability, and review need. It must not decide whether Memex's disposition is correct.
3. **Run the full test suite.** Keep this as library-only work. No gate, review UI, remote storage, log rotation, Memex runtime integration, or x-growth integration.

Only after the logger is solid: spec and build the scoring framework, the gate, and the review CLI. Do not build them in parallel.

## Open decisions

- **Language.** Resolved for v0: Python.
- **ID generation.** Resolved for v0: inline UUIDv7-compatible generation, no external dependency.
- **Log file path convention.** v0 accepts any explicit path and tests `runs/<run-id>/trajectory.jsonl`; confirm this convention during first consumer trial.
- **Scoring model.** Resolved for v0: separate append-only review entries, never mutation of the original decision entry.
- **Distribution.** Eventually clerk needs to be installable by other projects (Memex, Catalyst, Cortex). Decide: pip-installable package, vendored copy per consumer, or git submodule. Defer until logger is working.

## Vault context

- `vault:wiki/research/cluster-synthesis-2026-05-13.md` — identifies the measurement/governance layer as the cross-cluster thesis and Clerk as the primitive behind it.

## Kill / graduation criteria

- **Kill or park** if the logger cannot prove a clean, domain-neutral trajectory schema with simple tests.
- **Stay in Lab** until log + grade + gate are validated by at least one consumer.
- **Graduate to Studio** only if Clerk becomes an active shared package with real downstream integration work.

## Do not do

- Do not build the gate, scoring framework, or review CLI before the logger is validated. Building them in parallel locks in interface decisions before the logger has revealed what shape they need.
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
