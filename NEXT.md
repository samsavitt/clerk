# Next

## Current state

- Clerk is the domain-neutral judgment logger for authorization infrastructure.
- Logger, decision-contract, scoring, outcome attachment, ledger report, and judgment schema v1 are operational.
- Existing Memex compatibility remains a constraint, but auth-infra is the primary active consumer path.
- Clerk should stay a primitive: append-only records in, replayable judgment ledger out.

## Next action

Do no standalone Clerk work until another consumer needs logger hardening. If a consumer change touches Clerk, run `python3 -m pytest` in `Lab/clerk/` and preserve backward compatibility.

## Open decisions

- Distribution model after two active consumers: pip package, vendored copy, or submodule.
- Whether future schema variants need a registry file or can stay documented in consumer contracts.

## Do not do

- Do not bake auth-infra, Gauntlet, Memex, or arena-specific assumptions into Clerk core.
- Do not build a review UI, streaming, log rotation, compression, or gate runtime here.
- Do not block authorization-infrastructure progress on Memex credit state.

## Vault context

- `wiki/synthesis/authorization-infrastructure-thesis.md` — thesis Clerk supports.
- `wiki/research/concepts/trajectory-eval-gate.md` — first authorization consumer.
- `wiki/research/concepts/agent-behavioral-calibration.md` — second consumer lens.

## Kill / graduation criteria

- Kill the shared-primitive path if schema variants cannot coexist without breaking existing consumers.
- Stay in Lab until at least one consumer needs Clerk as a stable package rather than a sibling repo.
- Graduate only when multiple consumers depend on Clerk as shared infrastructure.
