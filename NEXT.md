# Next

## Current state

- Project initialized 2026-05-13.
- Three spec files exist: `README.md`, `docs/schema.md` (entry schema), `docs/logger.md` (logger contract).
- No code yet.
- Origin context: extracted from the Memex substrate maintenance loop's trajectory log pattern. The cluster-synthesis (`vault:wiki/research/cluster-synthesis-2026-05-13.md`) identified "supervision layer for AI" as a cross-cluster meta-thesis; clerk is the standalone implementation of that thesis's load-bearing primitive (log + grade + gate).

## Next action

1. **Implement the logger in Python** per `docs/logger.md`. Smallest useful: a single module with a `log()` function and a small CLI wrapper. ~50–100 lines total.
2. **Add a test harness.** Validate every required field, every auto-fill rule, every error condition listed in `logger.md`.
3. **Run the logger against a synthetic stream.** Generate 20–30 entries by hand or script; confirm the JSONL file accumulates correctly, atomic writes hold under simulated concurrency, schema violations are refused cleanly.

Only after the logger is solid: spec and build the scoring framework, the gate, and the review CLI. Do not build them in parallel.

## Open decisions

- **Language.** Python is the default given vault and Memex precedent. Confirm at start of next session.
- **ID generation.** Spec says UUIDv7 (timestamped, sortable). Python `uuid` stdlib lacks v7; use `uuid6` library or implement inline. Decide at code time.
- **Log file path convention.** Spec defaults to `runs/<run-id>/trajectory.jsonl`. Confirm this is the right convention for clerk's consumers (Memex already uses this).
- **Distribution.** Eventually clerk needs to be installable by other projects (Memex, Catalyst, Cortex). Decide: pip-installable package, vendored copy per consumer, or git submodule. Defer until logger is working.

## Do not do

- Do not build the gate, scoring framework, or review CLI before the logger is validated. Building them in parallel locks in interface decisions before the logger has revealed what shape they need.
- Do not bake any Memex- or domain-specific assumptions into clerk's code. Domain-specific scoring rules live in the consumer, not in clerk itself.
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
