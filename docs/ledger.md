# Ledger Report

Clerk ledgers are append-only JSONL. The report helper is a read-only view over that ledger.

## CLI

```bash
python -m clerk.cli report runs/<run-id>/trajectory.clerk.jsonl
```

The command prints Markdown with:

- decision count,
- review count,
- outcome count,
- one row per original decision,
- latest review recommendation,
- latest outcome,
- reviewer questions with no attached outcome yet.

## Boundary

The report does not score, gate, apply proposals, or write files. It only groups existing ledger entries:

- original decisions,
- `decision-accountability-review` entries,
- `decision-outcome` entries.

The report is read-only and makes no changes to the ledger or any consumer state.
