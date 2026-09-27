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

None yet.

<!-- GIT-SYNC:START (identical in every repo; source: samsavitt/dotfiles claude/sync-rule.md) -->
## Git sync

GitHub is the single source of truth: any machine, cloud session or AI continues from what is pushed.

- **Start:** `git pull --ff-only` before changing anything; if it cannot fast-forward, sort that out first.
- **Finish:** before ending any task that changed files, commit and push — pre-approved, do not ask Sam. On a branch, open a PR and merge it once checks pass, then delete the branch.
- **Exception:** if merging deploys or publishes, or this repo's own instructions forbid it, open a draft PR and tell Sam.
- Never force-push, rewrite shared history, bypass repo gates, or commit secrets. Files kept out of git on purpose do not travel.
<!-- GIT-SYNC:END -->
