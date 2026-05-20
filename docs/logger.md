# Logger

The logger is the smallest component of clerk: it accepts an entry, validates it, and appends one JSONL line to a log file. That's the whole contract.

## What it does

1. Accepts an entry as a dict (Python) or JSON object (CLI / stdin).
2. Validates required fields per `schema.md`.
3. Auto-fills `schema`, `id`, and `ts` if they are missing.
4. Appends one JSONL line to the configured log file. Append is atomic at the OS level (single `write` syscall to a file opened with `O_APPEND`).
5. Returns the written entry (with auto-filled fields) or raises an error.

## What it does not do

- No scoring. That's the scoring framework's job.
- No gating. That's the gate's job.
- No reading. Reading the log is a separate concern (a query/replay tool, future).
- No editing or deleting prior entries. Ever.

## Interface

### Python

```python
from clerk import logger

entry = {
    "agent": "research-agent",
    "action_type": "ingest-classify",
    "input": {"ref": "raw/inbox/paper-X.md"},
    "decision": "ingest-new",
    "reason": "No existing coverage of this topic in the wiki.",
    "provenance": ["wiki/INDEX.md"],
    "scores": {"tier": 1},
}

written = logger.log(entry, log_path="runs/2026-05-13/trajectory.jsonl")
# `written` includes auto-filled schema, id, ts
```

### CLI

```sh
echo '{"agent":"research-agent","action_type":"ingest-classify","input":{"ref":"x.md"},"decision":"discard","reason":"duplicate"}' \
  | clerk log --to runs/2026-05-13/trajectory.jsonl
```

Stdin accepts one JSON object. Stdout returns the written entry (with auto-filled fields) for capture. Exit nonzero on validation failure with a message to stderr.

## Auto-filled fields

If absent, the logger fills:

- `schema` → `clerk/v1`
- `id` → UUIDv7 generated at write time
- `ts` → current UTC time in ISO8601 with `Z` suffix

If present, the logger preserves the caller's values without modification. (Useful for tests and replays.)

## Validation

The logger refuses to write if any required field is missing or wrong-typed (per `schema.md`). Refusal is an exception in Python, exit code 2 in CLI. The log file is not touched on validation failure.

Validation does NOT check:
- Whether `decision` values are sensible for the given `action_type` (that's domain-specific; enforce in the agent or the gate)
- Whether `scores` values are within expected ranges (same — domain-specific)
- Whether `provenance` references actually exist on disk (out of scope; reference is intent, not assertion)

## Concurrency

Multiple agents writing to the same log file concurrently is safe as long as each individual entry's serialized form fits in one POSIX atomic write (typically < 4 KiB). Entries larger than that should be split into multiple entries or have large payloads moved into `proposal_path` files. The logger does not implement explicit file locking.

## Errors

| Condition | Behavior |
|---|---|
| Required field missing | Refuse; raise / exit 2; do not write. |
| Required field wrong type | Refuse; raise / exit 2; do not write. |
| Entry exceeds atomic write size | Refuse; raise / exit 2; suggest splitting. |
| Log path does not exist | Create parent directories if needed; create file. |
| Log path is not writable | Raise / exit 1 with OS error. |

## Out of scope for the logger

- Querying / aggregating entries (separate tool)
- Replaying past entries (separate tool)
- Compressing or rotating old logs (operations concern, not logger concern)
- Streaming to remote storage (future, not v1)
