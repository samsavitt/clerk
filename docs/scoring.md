# Clerk Scoring

Clerk scoring is not domain evaluation. It is decision-accountability review.

The scorer does not decide whether a Memex source should be ingested, whether a content candidate is good, or whether a trade rationale is attractive. The consumer owns that domain judgment. Clerk scores whether the decision record is legible enough to audit, compare, learn from, and later connect to outcomes.

## Boundary

### Consumer-owned

Consumers own:

- the action being decided,
- the allowed decision values,
- the domain-specific quality rules,
- the acceptance thresholds,
- the human approval policy,
- the outcome definition.

For Memex, this means Memex owns source tiers, disposition constraints, proposal quality, wiki safety boundaries, and whether an ingest/update/contradiction decision is correct.

### Clerk-owned

Clerk owns:

- whether the decision has enough evidence to review later,
- whether the rationale names the criterion that mattered,
- whether the provenance is sufficient for replay,
- whether the decision's risk and reversibility are visible,
- whether a future outcome can be attached cleanly,
- whether a human reviewer can tell what happened without reading the whole run.

This is the wedge: Clerk is a judgment ledger, not another evaluator.

## Review Dimensions

Scoring v0 should be small and cross-domain. Recommended dimensions:

| Score | Type | Meaning |
|---|---|---|
| `rationale_clarity` | number 0-1 | Does the reason explain the actual criterion, not just restate the decision? |
| `provenance_sufficiency` | number 0-1 | Are the consulted sources, files, prior entries, or artifacts named well enough to replay the judgment? |
| `criterion_fit` | number 0-1 | Is the decision tied to the consumer's stated rule or rubric? |
| `risk_visibility` | number 0-1 | Are downside, irreversibility, or safety concerns visible when relevant? |
| `outcome_attachability` | number 0-1 | Can a later outcome be attached without reconstructing context from chat or run logs? |
| `review_need` | short label | `none`, `spot-check`, `human-review`, or `block-until-reviewed`. This is a review recommendation, not a gate. |

The first five scores are Clerk-native. `review_need` is a recommendation for later gate design, not an enforcement action in v0.

## Contract

Scoring v0 should receive a Clerk entry and optional context supplied by the consumer.

```python
result = scorer.score(entry, context={...})
```

It should return a new Clerk entry, not mutate the original entry:

```json
{
  "agent": "clerk-scorer",
  "action_type": "decision-accountability-review",
  "input": {"ref": "<parent entry id>"},
  "parent_id": "<parent entry id>",
  "decision": "reviewed",
  "reason": "The decision names the source tier and proposal path, but does not define the later outcome window.",
  "scores": {
    "rationale_clarity": 0.8,
    "provenance_sufficiency": 0.9,
    "criterion_fit": 0.8,
    "risk_visibility": 0.6,
    "outcome_attachability": 0.4,
    "review_need": "spot-check"
  }
}
```

Appending a separate review entry preserves the ledger. It also lets multiple reviewers or scoring versions disagree without rewriting history.

For consumer-facing decision shape, see `docs/decision-contract.md`. The recommended fields `risk`, `reversibility`, `outcome_window`, and `reviewer_question` are accountability fields, not domain judgments.

## Memex Compatibility

Memex trajectory entries should map into Clerk without Clerk understanding Memex's domain rules.

Memex source fields:

| Memex trajectory field | Clerk field |
|---|---|
| `source` | `input.ref` |
| `tier` | `input.tier` or `scores.source_tier` if Memex wants tier as a domain score |
| `disposition` | `decision` |
| `pages_read` | `provenance` |
| `proposal` | `proposal_path` |

Clerk should not validate whether a Tier 3 source is allowed to update a synthesis page. That rule belongs in Memex. Clerk can score whether the decision record makes the tier constraint visible and reviewable.

## What Not To Build Yet

- No gate implementation.
- No review UI.
- No x-growth integration.
- No Memex runtime integration.
- No domain-specific scoring rules inside Clerk.
- No outcome database beyond append-only entries.

## Current Implementation

Scoring v0 is implemented as `clerk.scoring.score(entry, context=None)`.

It is deliberately lightweight:

- pure library function,
- no file writes,
- no gate enforcement,
- no consumer integration,
- no domain-specific correctness checks.

It returns a separate `decision-accountability-review` entry that can be logged with `clerk.log()`.
When dimensions are weak, the review reason names concrete missing accountability fields where possible, such as missing `risk`, `reversibility`, or `outcome_window`.

## Next Implementation Step

Run a second controlled Memex-style dry run using `docs/decision-contract.md`, then compare whether review entries become more focused without adding Memex-specific scoring rules.
