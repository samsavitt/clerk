# Next

## Product identity

Clerk is the **authorization infrastructure primitive** — an append-only log that captures human judgment decisions as replayable records, enabling AI execution to be gated on and audited against those records. It is domain-neutral by design: domain-specific scoring rules, gate policies, and schema extensions live in consumers, not in Clerk.

This is not an accountability review tool. It is not a Memex dependency. It is the substrate that makes AI execution in consequential domains auditable, replayable, and authorization-gated.

The vault's authorization infrastructure synthesis (`wiki/synthesis/authorization-infrastructure-thesis.md`) established that every consequential AI deployment needs this layer, and nobody has built the general version. Clerk is the general version.

---

## Current state

- Project initialized 2026-05-13.
- Logger v0 implemented in Python:
  - `src/clerk/logger.py` exposes `log(entry, log_path=...)`.
  - `src/clerk/cli.py` exposes `clerk log --to <path>` and `python -m clerk.cli log --to <path>`.
  - `pyproject.toml` defines the package and console script.
- Consumer decision contract exists at `docs/decision-contract.md`; defines `risk`, `reversibility`, `outcome_window`, and `reviewer_question` fields. These remain valid for the Memex use case; the judgment schema (see below) is the extension needed for authorization infrastructure consumers.
- Scoring v0 implemented (`src/clerk/scoring.py`) — returns separate `decision-accountability-review` entries, never mutates original decisions.
- Outcome attachment v0 implemented (`src/clerk/outcomes.py`) — returns separate `decision-outcome` entries with `parent_id`.
- Ledger report v0 implemented — `python -m clerk.cli report <ledger.jsonl>` prints read-only Markdown report.
- Controlled Memex dry-run trials completed and documented in `docs/reviews/`. Result: Clerk is useful for supervised accountability review.
- Verification on 2026-05-14: `python3 -m pytest` passed, 54 tests.

---

## Next action

### 1. Add judgment schema for authorization infrastructure consumers (next engineering session)

The existing decision-contract fields cover accountability review. The authorization infrastructure use case requires a judgment schema that encodes human authorization as a replayable record:

```json
{
  "judgment_id": "<uuidv7>",
  "domain": "<string>",
  "decision_time": "<iso8601>",
  "authorizer_id": "<string>",
  "inputs_hash": "<sha256 of the inputs presented to the authorizer>",
  "judgment_payload": "<the human's actual decision, structured>",
  "outcome_window": "<time horizon for outcome attachment>",
  "outcome_attached": false
}
```

This schema should be addable as an optional extension alongside the existing contract fields — not a replacement. Clerk remains backward-compatible with Memex consumers.

### 2. Onboard trajectory-eval-gate as first authorization infrastructure consumer

`Lab/agent-calibration/` and the trajectory-eval-gate concept use Clerk's log as the audit substrate for reasoning trajectory evaluation. Write a minimal consumer contract document for this use case and verify Clerk's logger handles it without modification.

### 3. Memex (when credits are restored)

Run one fresh Memex proposal-batch trial using the existing decision-contract flow. Do not block on this — Memex is a valid consumer but not the primary one.

---

## Primary consumers (priority order)

1. **trajectory-eval-gate** — reasoning trajectory as judgment record; counterexample-not-score as the judgment payload format; moat doesn't depreciate on model version releases. Concept: `wiki/research/concepts/trajectory-eval-gate.md`.
2. **agent-calibration** — behavioral fingerprint as routing authorization signal; arena simulation produces the judgment data. Concept: `wiki/research/concepts/agent-behavioral-calibration.md`.
3. **judgment-record** — premium professional decision capture; 10-decision first test; Clerk as the storage and replay primitive. Concept: `wiki/research/concepts/judgment-record.md`.
4. **Memex** — substrate maintenance agent; already using the accountability review schema. Valid consumer; lower priority than authorization infrastructure use cases.
5. **Catalyst / Cortex / Sentinel** — content scoring, trading rationale, governance. Future consumers.

---

## Open decisions

- **Judgment schema extension:** Add as a named schema variant alongside the existing decision-contract, or as an optional field set within the same schema?
- **Distribution:** pip-installable package, vendored copy per consumer, or git submodule? Defer until two consumers are live.
- **Language:** Resolved for v0: Python.

---

## Do not do

- Do not treat Memex as the primary consumer or the reason Clerk exists.
- Do not block Clerk's authorization infrastructure work on Memex's credit situation.
- Do not bake domain-specific assumptions into Clerk's code. Domain-specific rules live in consumers.
- Do not build a review UI, gates, or runtime integration before the judgment schema has been validated by one authorization infrastructure consumer.
- Do not add streaming, log rotation, or compression. Clerk is a primitive.

---

## Vault context

- `vault:wiki/synthesis/authorization-infrastructure-thesis.md` — the thesis Clerk is the primitive for; general product data model; trajectory-eval-gate as first market.
- `vault:wiki/research/concepts/trajectory-eval-gate.md` — first authorization infrastructure consumer.
- `vault:wiki/research/concepts/agent-behavioral-calibration.md` — second consumer; behavioral fingerprint as judgment payload.
- `vault:wiki/research/concepts/judgment-record.md` — third consumer; premium professional decision capture.
- `vault:wiki/research/cluster-synthesis-2026-05-13.md` — original identification of measurement/governance layer as cross-cluster thesis.

---

## Kill / graduation criteria

- **Kill** if the judgment schema cannot be added cleanly alongside the existing contract without breaking Memex compatibility.
- **Stay in Lab** until at least one authorization infrastructure consumer (trajectory-eval-gate or agent-calibration) validates the judgment schema in a real run.
- **Graduate to Studio** if Clerk becomes an active shared package with real downstream integration across multiple consumers.
