# Clerk Agent Rules

Read root `/Users/samsavitt/Lab/LAB.md`, then this repo's `README.md` and `NEXT.md`.

Clerk is a Lab prototype for the domain-neutral supervision primitive: log + grade + gate. Keep it small and library-shaped. The next code should validate the logger before scoring, gates, review UI, packaging, or integrations.

## Workflow

- Make the smallest useful change for the current next action.
- Keep domain-specific scoring rules out of Clerk; consumers own those.
- Update `NEXT.md` if state, next action, open decisions, Vault context, or kill/graduation criteria change.
- Do not create vault project bridges, context snapshots, or bridge packets.

## Verification

Run focused tests before claiming success. If verification is not possible, state what is missing.
## Support-Layer Scan

Default to support-first for material work: before material analysis, planning, implementation, review, or final reporting, use at least one relevant support layer unless there is a clear reason not to. Start with repo truth; use vault RAG for prior decisions, research, cross-domain context, or strategy; invoke 1-3 relevant skills or profiles for known procedures or review lenses; use subagents for independent research, review, or validation; use live web for current external facts. Do not invoke every skill; choose the smallest relevant slate and name deliberate skips. Final summaries must include `Support used: RAG=<...>; skills=<...>; subagents=<...>; live=<...>; skipped=<...>; changed=<what changed because of support>.`

## Safety

Do not commit, push, install dependencies, or perform destructive actions unless explicitly approved. Never stage `.env` or credentials.

## Vault context

At session start, search `vault:wiki/INDEX.md` for relevant material using these terms: accountability ledger, supervision primitive, agent decisions outcome tracking, behavioral economics. Read only matching sections that directly augment current work.

## Applied Learning

None yet.
