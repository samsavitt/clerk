# Ledger Usefulness Review — 2026-05-14

## Question

Does Clerk add anything useful beyond a Memex trajectory log?

## Setup

Input:

- `tests/fixtures/memex_compatibility.json`

Review method:

- Log-shaped Memex fixture entries were scored with `clerk.scoring.score()`.
- Context supplied Memex-relevant accountability terms, but Clerk did not import or enforce Memex disposition rules.
- Review entries were generated as separate `decision-accountability-review` entries with `parent_id` pointing at the original decision.

## Findings

Clerk is not useful if it merely restates the Memex disposition. The useful layer is meta-decision review:

- **Auditability:** Can someone later see what was decided, which source was involved, which pages were read, and where the proposal lives?
- **Review routing:** Does a decision look clean enough to pass, or does it need a spot-check/human review because a cross-domain accountability dimension is weak?
- **Outcome readiness:** Can a later accepted/rejected/later-useful signal attach to the decision without reconstructing chat context?

On the fixtures:

- `ingest-and-update` is cleanly accountable: clear rationale, strong provenance, proposal path, held gate outcome, and outcome attachability.
- `flag-for-review-low-grade` is also cleanly accountable because the risk/review reason is explicit.
- `discard` is legible but weaker on risk visibility; Clerk recommends `spot-check`. That is a useful distinction because a discard can silently remove future value if nobody reviews the class of discarded sources.

## What Clerk Adds

Memex answers: **Was this source disposition correct under the Memex rules?**

Clerk answers: **Will this decision still be reviewable, comparable, and learnable later?**

That difference matters. A Memex run could be domain-correct but operationally weak if the proposal path is missing, provenance is thin, the reason is generic, or no outcome can be attached later. Clerk makes those gaps visible without becoming the Memex evaluator.

## What Is Still Missing

Clerk does not yet prove outcome-grounded usefulness. The current loop can say "this decision is reviewable"; it cannot yet say "this kind of decision later worked." That requires attaching later outcomes such as:

- proposal accepted/rejected,
- later cited/useful,
- later reversed,
- caused correction,
- generated human disagreement.

## Recommendation

Continue Clerk, but keep the next loop narrow:

1. Use one real Memex dry-run trajectory as the first controlled trial.
2. Convert it to Clerk entries and score it.
3. Ask whether the review entries identify audit gaps that raw Memex logs did not.
4. Do not wire Clerk into Memex runtime until this manual trial is useful.
5. Do not involve x-growth yet.

## Candidate-Initialization Implication

Do not initialize Decision Ledger as a separate repo yet. Clerk is currently absorbing that shape. Reconsider Decision Ledger only after Clerk can attach outcomes to real decisions and answer cross-run questions that raw trajectory logs cannot.
