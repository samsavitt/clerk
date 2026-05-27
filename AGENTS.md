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

## Safety

Do not commit, push, install dependencies, or perform destructive actions unless explicitly approved. Never stage `.env` or credentials.

## Vault context

At session start, search `vault:wiki/INDEX.md` for relevant material using these terms: accountability ledger, supervision primitive, agent decisions outcome tracking, behavioral economics. Read only matching sections that directly augment current work.

## Applied Learning

When the same failure recurs, Sam has to re-explain something, or a workaround is found for a tool or platform limitation: add one bullet here. Max 15 words. No explanations. Only things that save time in future sessions.
