# Decision Contract

Clerk supervises decisions, not domains. A consumer should send Clerk one entry per decision worth auditing later.

## Required by the logger

Every entry must satisfy the base Clerk logger schema:

- `agent`: consumer agent name
- `action_type`: the kind of decision
- `input`: the thing being decided on
- `decision`: the chosen action
- `reason`: why this action was chosen

Clerk fills `schema`, `id`, and `ts` if they are missing.

## Recommended for supervised decisions

These fields make review entries more useful without making Clerk domain-specific:

| Field | Where | Meaning |
|---|---|---|
| `risk` | `input` or top level | What could go wrong if this decision is accepted? |
| `reversibility` | `input` or top level | How hard is the decision to undo? Use consumer vocabulary such as `easy`, `medium`, or `hard`. |
| `outcome_window` | `input` or top level | When should a reviewer know whether the decision was good? |
| `reviewer_question` | `input` or top level | The one question a human should answer before accepting the decision. |
| `proposal_path` | top level | Artifact to review or apply, if any. |
| `provenance` | top level | Files, sources, prior entries, or lookups used to reach the decision. |

These are accountability fields. They do not tell Clerk whether the decision is correct.

## Memex dry-run example

```json
{
  "agent": "memex-ingest",
  "action_type": "ingest-classify",
  "input": {
    "ref": "raw/inbox/paper-example.md",
    "risk": "Could update the wrong synthesis page if overlap is only thematic.",
    "reversibility": "medium",
    "outcome_window": "after human proposal review",
    "reviewer_question": "Does the proposal name the exact existing page it changes and the criterion for changing it?"
  },
  "decision": "ingest-and-update",
  "reason": "The source fills an explicit gap in an existing synthesis page and includes a concrete proposed edit.",
  "provenance": [
    "wiki/INDEX.md",
    "wiki/synthesis/example.md"
  ],
  "proposal_path": "runs/example/proposals/paper-example.md",
  "tags": ["memex", "dry-run"]
}
```

## Effective use

Use Clerk for decisions where later regret or learning matters:

- ingest, discard, or update decisions,
- proposal acceptance decisions,
- durable-state changes,
- high-impact recommendations.

Do not use Clerk for routine reads, status messages, or every intermediate thought.

The next useful trial is to run a Memex-style dry run with these recommended fields present, then compare whether Clerk's review entries become more focused without adding Memex-specific scoring rules.

Use `python -m clerk.cli report <ledger.jsonl>` to inspect whether decisions, reviews, outcomes, and unresolved reviewer questions are easy to review as a grouped ledger.
