# Outcome attachment

Outcome attachment records what happened after a Clerk decision. It does not change the original decision and it does not decide whether the original domain call was correct. It appends a separate `decision-outcome` entry with `parent_id` pointing at the earlier entry.

This matters before gates because Clerk needs calibration evidence. A decision can be well-recorded but later rejected, or weakly-recorded but later useful. Those are different signals.

## Outcome labels

V0 uses a small shared vocabulary:

| Outcome | Meaning |
|---|---|
| `accepted` | A human or downstream process accepted the decision or proposal. |
| `rejected` | A human or downstream process rejected it. |
| `later-useful` | It was not immediately accepted, but later became useful evidence or context. |
| `reversed` | A later decision explicitly reversed the original decision. |
| `caused-correction` | The decision led to a correction, cleanup, or remediation. |
| `human-disagreement` | A human disagreed with the decision but no final accepted/rejected result exists yet. |
| `unclear` | The downstream result is ambiguous. |

## Example

```json
{"schema":"clerk/v1","id":"01957a30-...","ts":"2026-05-14T17:05:00Z","agent":"clerk-outcome","action_type":"decision-outcome","input":{"ref":"decision-001","outcome":"accepted","agent":"research-agent","action_type":"ingest-classify","decision":"ingest-and-update","outcome_ref":"runs/review/proposals/source.md","reviewer":"human"},"parent_id":"decision-001","decision":"accepted","reason":"Human review accepted the proposed wiki update.","scores":{"outcome":"accepted"},"provenance":["decision-001","runs/review/proposals/source.md"],"tags":["clerk","decision-outcome","accepted"]}
```

## Current boundary

Outcome entries are calibration data only. Clerk does not yet update scoring weights, enforce gates, or apply proposals from outcome data. The next useful consumer trial is to attach `accepted`, `rejected`, or `later-useful` outcomes to a completed dry run, then check whether scoring dimensions predicted the outcome direction.
