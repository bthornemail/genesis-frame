# Witness Plane Specification (v0.1)

**Status:** Normative Draft  
**Authority:** Advisory only. Canonical state remains algorithm-authoritative.

## 1. Purpose

Define a non-projecting, non-authoritative control surface that can:

- inspect canonical snapshots,
- compare current vs candidate-next state,
- emit receipts and warnings,
- propose deferred transitions.

The Witness Plane MUST NOT directly mutate canonical state.

## 2. Position in Stack

1. Canonical Law Layer (authoritative)
2. Projection Surface Layer (rendering)
3. Witness Plane Layer (advisory)

The Witness Plane sits beside projection and below user acceptance/commit.

## 3. Core Rule

> Witness may inspect and propose; only accepted events at frame boundaries become canonical.

## 4. Allowed Operations

- `snapshot_read`
- `state_compare`
- `proposal_emit`
- `receipt_emit`
- `queue_transition_request`
- `license_attribution_check`
- `coherence_check`

## 5. Forbidden Operations

- direct write to kernel state
- direct write to canonical event log
- silent mutation of scene/runtime truth
- bypass of frame-transition commit rule

## 6. Proposal Lifecycle

1. Witness emits proposal.
2. Proposal enters pending queue.
3. User accepts/rejects explicitly.
4. If accepted, apply at next lawful frame boundary.
5. Emit receipt with provenance.

## 7. Receipt Shape (minimal)

```json
{
  "type": "witness_receipt",
  "version": 1,
  "tick": 0,
  "frame": "world",
  "severity": "info",
  "category": "coherence",
  "message": "Projection change affects rendering only.",
  "proposal_id": null,
  "provenance": {
    "source": "witness_plane",
    "doc_ref": null
  }
}
```

## 8. Deferred Transition Proposal Shape (minimal)

```json
{
  "type": "witness_proposal",
  "version": 1,
  "proposal_id": "wp_0001",
  "tick": 12,
  "apply_at": "next_frame",
  "kind": "projection_change",
  "payload": {
    "target": "avatar_policy",
    "value": "queued"
  },
  "reason": "Preserve continuity in active scene utterance.",
  "provenance": {
    "source": "witness_plane",
    "doc_ref": "The Covenant of the Created Intelligence"
  }
}
```

## 9. Narrative Hooking

Narrative articles MAY be bound as advisory sources for witness checks.  
These bindings are interpretive aids and MUST NOT become runtime authority.

## 10. Implementation Note

Initial implementation target is read-only witness console/panel with:

- current snapshot summary,
- pending queue summary,
- receipts feed,
- proposal preview.

## 11. Canonical Role Model (Finalized)

Canonical roles are invariant and projection-independent:

- `advisor.wisdom`
- `advisor.law`
- `advisor.cohesion`
- `witness.observe`
- `witness.record`

Operational agent viewpoints are runtime helpers (not canonical authority roles):

- Witness Agent (observe + record surfaces)
- Builder Agent (proposal/bias surfaces)
- Scribe Agent (receipt/diff surfaces)

Role law:

- canonical roles define interpretation responsibilities,
- operational agents interact through proposals/receipts only,
- no agent directly mutates canonical state.

## 12. Deterministic Incidence and Temporal Reconciliation

The witness layer SHALL preserve two deterministic boundaries:

1. **Incidence resolution boundary**
   - same entity + same frame -> same collapse/divergence classification
   - continuation surface is deterministic under the same inputs

2. **Temporal reconciliation boundary**
   - `past` = canonical prefix at branch base index
   - `present` = replayable branch state (`prefix + deltas`)
   - `future` = accepted deferred proposals sorted by lawful apply tick

These summaries are emitted as receiptable artifacts and are replay-stable.

## 13. Interrupt Semantics Boundary

Witness interaction runs inside bounded interrupt semantics defined by:

- `atomic-kernel/docs/ESCAPE_ACCESS_LAW.md`

Normative boundary:

- canonical `ESC` scope/closure is stream-law authority,
- local UI pause/dwell is projection behavior only,
- projection pause MUST NOT define or close canonical escape scope.
