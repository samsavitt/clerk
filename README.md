# Clerk

A supervision layer for AI work.

Clerk is a small library that wraps AI agents with three primitives: a log (every decision recorded), a scoring framework (every decision made reviewable), and a gate (every decision approved, held, or rejected before it acts on the world). It does not generate; it supervises. It is the supervisor, not the worker.

Other projects (Memex, Catalyst, Sentinel, Cortex) are downstream consumers — each plugs in its own scoring rules and gate policies. Clerk itself is domain-neutral.

## Status

Logger v0, scoring v0, and outcome attachment v0 are implemented and tested. Scoring is decision-accountability review, not domain evaluation. Outcomes record what happened later without mutating the original decision. Gates are not implemented yet. See `docs/schema.md`, `docs/logger.md`, `docs/scoring.md`, `docs/outcomes.md`, and `NEXT.md`.

## Why this exists

Most AI products today have a powerful worker (the LLM) and no editorial process around it. The opportunity is to be the editorial process. Clerk is the smallest standalone version of that editorial process — log + review + gate — built so any agent can plug in.
