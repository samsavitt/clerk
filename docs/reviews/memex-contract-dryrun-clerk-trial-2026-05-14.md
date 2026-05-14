# Memex Contract Dry-Run Clerk Trial

## Inputs

- Source trajectory: `/Users/samsavitt/Lab/memex/runs/2026-05-13-ingest-dryrun-001/trajectory.jsonl`
- Decision contract: `docs/decision-contract.md`
- Local Clerk ledger: `runs/2026-05-14-memex-contract-dryrun-clerk-trial/trajectory.clerk.jsonl`
- Local summary: `runs/2026-05-14-memex-contract-dryrun-clerk-trial/summary.json`

This trial reused the same real Memex dry-run trajectory as the first Clerk trial, but added explicit accountability fields to each converted decision:

- `risk`
- `reversibility`
- `outcome_window`
- `reviewer_question`

No Memex runtime integration was added.

## Scores

| Source | Decision | Review need | Rationale | Provenance | Criterion fit | Risk visibility | Outcome attachability | Outcome |
|---|---|---|---:|---:|---:|---:|---:|---|
| `Recursive Language Models, clearly explained.md` | `discard` | `human-review` | 0.45 | 1.0 | 1.0 | 1.0 | 1.0 | `accepted` |
| `paper-2604.17849-cua-reliability.md` | `ingest-new` | `none` | 0.8 | 1.0 | 1.0 | 1.0 | 1.0 | `accepted` |
| `paper-2604.01687-coevoskills.md` | `ingest-and-update` | `none` | 0.8 | 1.0 | 1.0 | 1.0 | 1.0 | `caused-correction` |

## Comparison With First Trial

The decision contract made Clerk more useful:

- `risk_visibility` improved from 0.0 to 1.0 on both positive ingest decisions.
- `outcome_attachability` stayed strong, but now came from explicit outcome-window fields rather than only from context supplied to the scorer.
- Review reasons became less noisy. The first trial flagged missing accountability fields; the second trial focused only on remaining weak dimensions.

The second trial also exposed the most important boundary: Clerk can say a decision is well-recorded while the later outcome still says `caused-correction`. For CoEvoSkills, `review_need = none` means the decision record was auditable, not that the domain proposal was automatically correct.

## Judgment

Clerk is useful as a decision-accountability layer when consumers follow a small decision contract. The contract should come before any runtime integration.

The next useful improvement is not a gate or UI. It is a tiny comparison/report helper that reads a Clerk ledger and groups:

- original decisions,
- review entries,
- outcome entries,
- and unresolved reviewer questions.

That helper would make Clerk easier to use without changing its architecture or importing Memex rules.

## Boundaries Preserved

- No real vault writes.
- No x-growth work.
- No gate implementation.
- No UI.
- No remote storage or log rotation.
- No Memex runtime integration.
