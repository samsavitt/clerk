---
schema: repo-state/v1
repo_type: lab_experiment
capabilities: [testing]
environment: Lab
---

# Clerk

## Durable rules

- Keep Clerk domain-neutral.
- Preserve backward compatibility with existing consumers unless a consumer contract explicitly changes.
- Treat logs, schemas, scoring, outcomes, and ledger reports as primitives; consumers own domain policy.

## Ownership boundary

This repo owns the append-only judgment logger and reviewable ledger primitives. It does not own auth-infra replay logic, Gauntlet arena rules, Memex substrate policy, or consumer-specific gates.
