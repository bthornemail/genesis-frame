# Genesis Frame v1.2 — Immediate Use Release

Genesis Frame v1.2 is now ready for immediate use.

## Core Result

- deterministic kernel + replay invariants remain stable
- bounded escape access law is enforced
- witness/proposal model is active with deferred next-frame commit
- incidence collapse/divergence resolution is deterministic
- past/present/future reconciliation is deterministic and receiptable
- first-class artifact carrier now includes `header8_artifact`

Strict validation status:

```text
140/140 passed
```

## One-Command Walkthrough

From repo root:

```bash
./start-walkthrough
```

Optional custom port:

```bash
./start-walkthrough 8080
```

## Canonical Reading Path

1. `atomic-kernel/docs/ESCAPE_ACCESS_LAW.md`
2. `atomic-kernel/docs/ALGORITHM_A13_ESC_DEPTH_MIXED_RADIX.md`
3. `atomic-kernel/docs/HEADER8_CANONICAL_ALGORITHM.md`
4. `atomic-kernel/docs/WITNESS_PLANE_SPEC.md`
5. `atomic-kernel/docs/112_PROOFS_MATRIX.md`

## Publication Statement

Genesis Frame v1.2 is a law-first release: algorithms define invariants, artifacts carry projections, witness surfaces advise without hidden authority, and all accepted change is bounded, receipted, and replayable.
