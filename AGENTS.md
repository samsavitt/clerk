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
