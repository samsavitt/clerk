# Entry schema

An *entry* is one supervised decision. Clerk's log is a sequence of entries — one JSON object per line, append-only.

## File format

JSONL (one JSON object per line). One log file per agent or per agent-instance, configurable. Default path convention: `runs/<run-id>/trajectory.jsonl`.

Append-only. Never edit or delete entries. If an entry is wrong, append a correcting entry that references the original via `parent_id`.

## Required fields

| Field | Type | Description |
|---|---|---|
| `schema` | string | Schema version. Currently `clerk/v1`. Allows future evolution. |
| `id` | string | Unique entry identifier. UUIDv7 recommended (timestamped, sortable). |
| `ts` | string | ISO8601 timestamp with timezone, e.g., `2026-05-13T19:42:11Z`. |
| `agent` | string | Identifier for the agent that produced this entry. Convention: `<project>-<role>`, e.g., `research-agent`, `content-scorer`. |
| `action_type` | string | What kind of decision this is. Convention: kebab-case verb, e.g., `ingest-classify`, `content-score`, `trade-rationale`. |
| `input` | object | What the agent was operating on. Free-form JSON; agent-specific shape. Minimum convention: include a `ref` field pointing at the source artifact (file path, URL, identifier). |
| `decision` | string | What was decided. Domain-specific value. Convention: enumerated set per `action_type`, e.g., `discard`, `ingest-new`, `approve`, `reject`. |
| `reason` | string | One or two sentences explaining why. Plain prose. |

## Recommended fields

| Field | Type | Description |
|---|---|---|
| `provenance` | array of strings | References the agent consulted before deciding. File paths, URLs, prior entry IDs. |
| `scores` | object | Named scores attached to the decision. Values are numbers or short labels. See examples. |
| `gate_outcome` | string | What the gate decided: `auto-approve`, `held`, `auto-reject`. Absent if no gate ran. |
| `proposal_path` | string | Pointer to a proposal artifact if one was generated (e.g., a markdown file describing the change to apply). |

## Optional fields

| Field | Type | Description |
|---|---|---|
| `parent_id` | string | If this entry follows from or corrects an earlier one, its `id`. |
| `tags` | array of strings | Free-form grouping/filtering labels. |
| `human_review` | object | If a human reviewed this entry, an object with `reviewer`, `verdict` (`approve` / `reject`), `verdict_ts`, optional `note`. |

## Example entries

### Knowledge ingestion agent

```json
{"schema":"clerk/v1","id":"01957a2d-...","ts":"2026-05-13T17:25:00Z","agent":"research-agent","action_type":"ingest-classify","input":{"ref":"raw/inbox/paper-example.md"},"decision":"ingest-and-update","reason":"Novel paper fills three structurally explicit slots in existing coverage.","provenance":["wiki/INDEX.md","wiki/synthesis/example.md"],"scores":{"tier":1,"coverage":1.0},"gate_outcome":"held","proposal_path":"runs/2026-05-13/proposals/paper-example.md"}
```

### Content scoring agent

```json
{"schema":"clerk/v1","id":"01957a2e-...","ts":"2026-05-13T17:30:00Z","agent":"content-scorer","action_type":"content-score","input":{"ref":"drafts/2026-05-13/post-003.md","topic":"AI evals"},"decision":"approve","reason":"High calibrated surprise; productive-anxiety arousal class; trending half-life.","scores":{"calibrated_surprise":0.82,"arousal_class":"productive-anxiety","half_life":"trending"},"gate_outcome":"auto-approve"}
```

### Trade rationale agent

```json
{"schema":"clerk/v1","id":"01957a2f-...","ts":"2026-05-13T17:35:00Z","agent":"trade-agent","action_type":"trade-rationale","input":{"ref":"signals/2026-05-13/aapl.json","instrument":"AAPL","direction":"long"},"decision":"approve","reason":"Signal strength + low-uncertainty residual; passes risk filter.","provenance":["signals/vgrsi/aapl.parquet","residuals/2026-05-13.parquet"],"scores":{"signal_strength":0.74,"uncertainty":0.21,"factor_loading":"momentum-dominant"},"gate_outcome":"held"}
```

### Outcome attachment

Outcome entries are separate entries with `action_type:"decision-outcome"` and `parent_id` pointing at the original decision. They record later results such as `accepted`, `rejected`, `later-useful`, or `reversed` without editing the original entry. See `docs/outcomes.md`.

## Conventions to keep stable

- `schema` field is mandatory and versioned. Future field additions are minor; field removals or type changes are major.
- `decision` values are agent-specific but should be an enumerated set per `action_type` — not free text. Enumeration enables aggregation across entries.
- `scores` values should be numbers or short labels. Avoid arbitrary nested objects in scores; complex shapes belong in `input` or `proposal_path`.
- Timestamps are always UTC ISO8601 with explicit `Z` suffix.
