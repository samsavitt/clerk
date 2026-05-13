# Clerk

A supervision layer for AI work.

Clerk is a small library that wraps AI agents with three primitives: a log (every decision recorded), a scoring framework (every decision graded), and a gate (every decision approved, held, or rejected before it acts on the world). It does not generate; it supervises. It is the supervisor, not the worker.

Other projects (Memex, Catalyst, Sentinel, Cortex) are downstream consumers — each plugs in its own scoring rules and gate policies. Clerk itself is domain-neutral.

## Status

Pre-implementation. Spec phase. See `docs/schema.md` and `docs/logger.md`.

## Why this exists

Most AI products today have a powerful worker (the LLM) and no editorial process around it. The opportunity is to be the editorial process. Clerk is the smallest standalone version of that editorial process — log + grade + gate — built so any agent can plug in.
