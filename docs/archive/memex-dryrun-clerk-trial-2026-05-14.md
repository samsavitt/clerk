# Memex Dry-Run Clerk Trial

## Inputs

- Source trajectory: `/Users/samsavitt/Lab/memex/runs/2026-05-13-ingest-dryrun-001/trajectory.jsonl`
- Local Clerk ledger: `runs/2026-05-14-memex-dryrun-clerk-trial/trajectory.clerk.jsonl`
- Local summary: `runs/2026-05-14-memex-dryrun-clerk-trial/summary.json`

The local ledger contains 9 append-only entries: 3 converted Memex decisions, 3 Clerk `decision-accountability-review` entries, and 3 Clerk `decision-outcome` entries.

## Scores

| Source | Decision | Review need | Rationale | Provenance | Criterion fit | Risk visibility | Outcome attachability | Outcome |
|---|---|---|---:|---:|---:|---:|---:|---|
| `Recursive Language Models, clearly explained.md` | `discard` | `human-review` | 0.45 | 1.0 | 1.0 | 0.65 | 1.0 | `accepted` |
| `paper-2604.17849-cua-reliability.md` | `ingest-new` | `block-until-reviewed` | 0.8 | 1.0 | 1.0 | 0.0 | 1.0 | `accepted` |
| `paper-2604.01687-coevoskills.md` | `ingest-and-update` | `block-until-reviewed` | 0.8 | 1.0 | 1.0 | 0.0 | 1.0 | `caused-correction` |

## Finding

Clerk adds useful audit signal beyond the raw Memex trajectory, but the signal is accountability-shaped rather than domain-shaped.

The raw trajectory shows what Memex decided and which pages it read. The Clerk review entries reveal what is missing for supervision:

- Positive ingest decisions had no explicit risk or reversibility language in the decision row, so both `ingest-new` and `ingest-and-update` scored `risk_visibility = 0.0`.
- The duplicate discard was accepted after proposal review, but its raw trajectory reason was short enough that Clerk still flagged rationale clarity. The richer reasoning lived in the proposal, not in the decision row.
- Outcome attachment was clean once Clerk IDs existed. The raw Memex log had proposal paths, but no parent decision IDs or normalized outcome vocabulary.
- The CoEvoSkills proposal was useful but correction-triggering: it found a stale section-title issue and proposed many line-specific edits that require human verification before application. Raw Memex made this look like a straightforward `ingest-and-update`; Clerk separates the original decision from the later `caused-correction` outcome.

## Judgment

Useful enough to keep Clerk alive as a Lab prototype. The next proving step should be a second controlled fixture or harness-level dry run that asks Memex-style output to include risk/reversibility fields explicitly, then checks whether Clerk scores improve without adding domain-specific rules.

Do not wire Clerk into Memex runtime yet.
