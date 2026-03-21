# Documentation Policy

## Purpose

This repository maintains two documentation tiers:

- `atomic-kernel/docs/` for normalized, canonical-facing documentation.
- `atomic-kernel/dev-docs/` for working drafts, exploration, and speculative notes.

## Rule

If a document describes behavior that is normalized and expected for implementation, it belongs in `docs/`.

If a document is exploratory, provisional, or speculative, it belongs in `dev-docs/`.

## What Goes in `docs/`

- normative specifications
- stable laws and invariants
- implementation-facing reference docs
- finalized verification matrices and traceability maps
- canonical reading-path documents

## What Goes in `dev-docs/`

- drafts not yet reviewed/frozen
- alternative formulations under discussion
- speculative architecture notes
- brainstorming, transcripts, and scratch analyses

## Promotion Workflow

1. Draft in `dev-docs/`.
2. Validate consistency with current normalized laws/specs.
3. Promote a clean copy into `docs/`.
4. Update `README.md` links to point to `docs/`.
5. Keep `dev-docs/` as workspace/history unless explicitly retired.

## Authority Boundary

`docs/` is the canonical-facing documentation surface.

`dev-docs/` is a development surface and is not authoritative by default.
