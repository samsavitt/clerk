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

Before material analysis, planning, implementation, review, or final reporting, run the support-layer scan: repo truth first; vault RAG for prior decisions, research, or cross-domain context; skills for known procedures; subagents for independent research, review, or validation; live web for current external facts; otherwise state `none` with the reason. Include `Support used: ...` in material final summaries.

## Safety

Do not commit, push, install dependencies, or perform destructive actions unless explicitly approved. Never stage `.env` or credentials.

## Vault context

At session start, search `vault:wiki/INDEX.md` for relevant material using these terms: accountability ledger, supervision primitive, agent decisions outcome tracking, behavioral economics. Read only matching sections that directly augment current work.
