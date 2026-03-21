# 112 Proofs Matrix

## 8 Invariant Questions × 7 Algorithms × 2 Proof Forms

**Status:** Normative Draft (Verification Framework)  
**Authority:** Algorithms define invariants; proofs demonstrate enforceability and failure boundaries.  
**Depends on:** `PURE_ALGORITHMS.md`, `CONTROL_PLANE_SPEC.md`, `ESCAPE_ACCESS_LAW.md`, `WITNESS_PLANE_SPEC.md`, `ATOMIC_KERNEL_NORMATIVE_CORE_v1_2.md`

---

## Formula

For each of the 8 invariant questions, each of the 7 algorithms must provide:

- one **constructive proof** (how the property is established)
- one **falsification proof** (how violation is detected/rejected)

Therefore:

```text
8 × 7 × 2 = 112 proofs
```

---

## Executable Lanes (Initial)

The following matrix cells are implemented as executable checks:

- **Q1 / Transition / Constructive**  
  `tests/test_all.py` check: `112 Q1 Transition constructive: deterministic replay receipt`
- **Q5 / Escape / Falsification**  
  `tests/test_all.py` check: `112 Q5 Escape falsification: time-based scope rejected`
- **Q5 / Projection / Falsification**  
  `tests/test_all.py` check: `112 Q5 Projection falsification: local pause non-authority`
- **Q6 / Proposal-Receipt / Constructive**  
  `tests/test_all.py` check: `112 Q6 Proposal/Receipt constructive: deferred next-tick commit`
- **Q7 / Branch-Reconciliation / Constructive**  
  `tests/test_all.py` check: `112 Q7 Branch/Reconciliation constructive: base+delta+return replayable`
- **Q4 / Projection / Constructive**  
  `tests/test_all.py` check: `112 Q4 Projection constructive: equivalent multi-projection receipts`
- **Q8 / Incidence / Constructive**  
  `tests/test_all.py` check: `112 Q8 Incidence constructive: deterministic collapse/divergence resolution`
- **Q7 / Branch-Reconciliation / Constructive (Temporal)**  
  `tests/test_all.py` check: `112 Q7 Branch/Reconciliation constructive: deterministic past/present/future reconciliation`

---

## The 7 Algorithms

1. **Transition Algorithm**  
   Advances canonical state under deterministic law.
2. **Control-Plane Algorithm**  
   Separates structural channels/lanes from payload.
3. **Projection Algorithm**  
   Derives text/graph/svg/3D/XR views from canonical state.
4. **Escape Algorithm**  
   Opens bounded interrupt scope and guarantees return.
5. **Fano Path Algorithm**  
   Selects active advisory/path emphasis over rolling horizon.
6. **Proposal/Receipt Algorithm**  
   Converts interventions into inspectable deferred artifacts.
7. **Branch/Reconciliation Algorithm**  
   Preserves canonical reference with persistent divergence + return.

---

## Q1. What is the source of truth?

**Answer:** The algorithm is the source of truth.

| Algorithm | Constructive Proof | Falsification Proof |
|---|---|---|
| Transition | Canonical state is derived only from deterministic transition over prior state + law constants. | Any direct manual state overwrite yields replay mismatch against law-derived trace. |
| Control-Plane | Interpretation state is explicit in canonical tuple `(channel,lane,mode,scope,numsys)`. | Hidden parser/control state not derivable from stream is non-canonical. |
| Projection | Views are generated from canonical state; projections are rebuildable. | Treating cached projection artifact as authority causes divergence from recomputed output. |
| Escape | Interrupt semantics are law-defined (ESC + bounded scope + return). | Implicit escape or unclosed interrupt breaks deterministic decoding and is rejected. |
| Fano Path | Path emphasis is derived from deterministic schedule + bounded bias queue. | Path-emphasis lane cannot alter canonical truth state; authority escalation is invalid. |
| Proposal/Receipt | Proposed changes are represented as artifacts before application. | Silent unreceipted mutation has no lawful proof trail and is invalid. |
| Branch/Reconciliation | Canonical trace remains reference; branch traces are explicitly anchored. | Branch overwrite of canonical reference without merge law is invalid. |

---

## Q2. How does the system move?

**Answer:** A bounded deterministic transition law moves the system.

| Algorithm | Constructive Proof | Falsification Proof |
|---|---|---|
| Transition | `delta/replay` yields same next state for same input. | Nondeterministic next-state function fails parity/replay vectors. |
| Control-Plane | Movement is encoded within bounded symbolic control substrate. | Out-of-band motion control not represented in stream is non-replayable. |
| Projection | Visual/story motion is rendered from evolving canonical index. | Projection-driven state movement without event/log support is invalid. |
| Escape | Interrupt scope returns to deterministic movement after closure. | Unterminated or time-closed escape causes movement ambiguity and is rejected. |
| Fano Path | Emphasis shifts are deterministic by tick + bounded queue. | Arbitrary non-lawful path jump outside scheduler is invalid. |
| Proposal/Receipt | Interventions move state only at lawful deferred commit points. | Mid-frame direct mutation bypassing defer/commit breaks motion law. |
| Branch/Reconciliation | Canonical and branch traces each move lawfully from explicit roots. | Untracked fork without base index/root cannot be replayed. |

---

## Q3. How does it distinguish payload from control?

**Answer:** A canonical control plane separates structural roles from payload.

| Algorithm | Constructive Proof | Falsification Proof |
|---|---|---|
| Transition | State machine update does not conflate parser mode with payload value. | Mixed undecidable token semantics causes undefined transition path. |
| Control-Plane | FS/GS/RS/US/ESC/NULL semantics are explicit and typed. | Ambiguous control token interpretation is rejected fail-closed. |
| Projection | Renderer consumes already-decoded state, not undecoded stream control. | Renderer-side guessing of control boundaries creates non-canonical views. |
| Escape | `ESC ESC` literalization preserves payload transparency of reserved token. | Unknown escape targets are rejected, preventing control/payload confusion. |
| Fano Path | Fano chooses emphasis only; it does not parse stream classes. | Using Fano as parser authority violates control-plane law. |
| Proposal/Receipt | Proposal artifacts are explicit objects, not hidden inline control bytes. | Inline hidden commands without artifact schema are invalid. |
| Branch/Reconciliation | Deltas are scoped by layer (canonical/branch/shared). | Cross-scope leakage of control intent is invalid without law. |

---

## Q4. How does it preserve meaning across projections?

**Answer:** Artifacts are projections of invariant state, not authorities.

| Algorithm | Constructive Proof | Falsification Proof |
|---|---|---|
| Transition | Same seed/tick reproduces same canonical basis for interpretation. | Same-input different-state outcome falsifies deterministic meaning anchor. |
| Control-Plane | Structural boundaries preserve semantic grouping across views. | Boundary loss merges scopes and breaks semantic invariants. |
| Projection | Text/graph/svg/3D/XR are generated from same source state. | Projection-specific ontology that cannot map back to source is invalid. |
| Escape | Interrupt affects interpretation window, not already-committed prior frame. | Escape mutating prior committed meaning violates replay boundary. |
| Fano Path | Emphasis selection changes focus, not truth value. | Fano promoted to semantic source breaks projection law. |
| Proposal/Receipt | Semantic changes are explicit proposals with receipts before commit. | Unreceipted semantic drift cannot be verified and is invalid. |
| Branch/Reconciliation | Branch meaning is diffable against canonical reference. | Unanchored branch semantics without base comparison is invalid. |

---

## Q5. How does it allow intervention without losing replay?

**Answer:** `ESC` provides bounded interrupt with deterministic return.

| Algorithm | Constructive Proof | Falsification Proof |
|---|---|---|
| Transition | Post-interrupt continuation resumes at lawful next frame. | Current-frame mutation bypassing transition causes replay drift. |
| Control-Plane | ESC is explicit structural access introducer. | Implicit interrupt access without ESC is rejected. |
| Projection | Local pause is projection-only and non-authoritative. | UI dwell time defining canonical scope is invalid by law. |
| Escape | Finite scope + deterministic closure + return-to-data are enforced. | Time-based closure or open-ended escape is rejected. |
| Fano Path | User/agent can bias next horizon, not overwrite current canonical frame. | Instant sovereign path replacement invalidates bounded interrupt model. |
| Proposal/Receipt | Intervention becomes deferred artifact, then accepted/rejected. | No proposal/receipt means no lawful intervention state transition. |
| Branch/Reconciliation | Interrupt can materialize a fork without mutating canonical trace. | Direct canonical overwrite via branch intent is invalid. |

---

## Q6. How does it permit collaboration without hidden authority?

**Answer:** Agents collaborate through proposals, receipts, and deferred commit.

| Algorithm | Constructive Proof | Falsification Proof |
|---|---|---|
| Transition | No collaborator can bypass law-defined transition mechanics. | Direct collaborator state write outside transition path is invalid. |
| Control-Plane | Scopes/roles are explicit in control context. | Private unshared control channel is non-canonical collaboration. |
| Projection | Collaborators read snapshots, not hidden renderer internals. | Projection-only scraped state cannot act as canonical authority. |
| Escape | Collaboration happens inside bounded interrupt window. | Permanent never-closing control mode is invalid. |
| Fano Path | Shared emphasis context is inspectable via envelope/readout. | Opaque prioritization without visible lane/queue is invalid. |
| Proposal/Receipt | Accept/reject/commit trail is receipted and auditable. | Silent acceptance or hidden commit path is invalid. |
| Branch/Reconciliation | Shared deltas are published as explicit artifacts. | Unscoped propagation to all traces without artifact law is invalid. |

---

## Q7. How does it branch and return without fragmentation?

**Answer:** Canonical trace, branch state, and shared deltas are distinct and returnable.

| Algorithm | Constructive Proof | Falsification Proof |
|---|---|---|
| Transition | Each trace follows same lawful transition semantics. | Branch state with undefined transition basis is invalid. |
| Control-Plane | Structural scopes preserve separation between layers. | Cross-layer scope leakage causes fragmentation and is invalid. |
| Projection | Return to canonical reference remains available from any branch view. | Projection-only branch identity without canonical anchor is invalid. |
| Escape | Branch creation is explicit bounded action within interrupt/commit path. | Never-closing branch mode without return path is invalid. |
| Fano Path | Horizon bias can steer branch emphasis while preserving origin. | Fano cannot erase canonical origin or fork root. |
| Proposal/Receipt | Branch differences are receipted and diffable. | Undiffable branch mutation without receipts is invalid. |
| Branch/Reconciliation | `base_index + deltas + return` remains explicit and replayable. | Untracked irreconcilable fork without lineage metadata is invalid. |

---

## Q8. How does it stay open in meaning while closed in law?

**Answer:** Closure belongs to law; openness belongs to interpretation.

| Algorithm | Constructive Proof | Falsification Proof |
|---|---|---|
| Transition | Law remains deterministic regardless of interpretive overlays. | Interpretive layer altering transition law falsifies closure. |
| Control-Plane | Structural boundaries are bounded while interpretation remains plural. | Unbounded parser ambiguity destroys legal closure. |
| Projection | Many projections map to one canonical source. | Any view elevated to source-of-truth is invalid. |
| Escape | Bounded non-closure is permitted only inside explicit escape scope. | Escape without deterministic return is invalid. |
| Fano Path | Advisory openness is bounded by lawful scheduler horizon. | Random sovereign chooser replacing law is invalid. |
| Proposal/Receipt | Differences are negotiable, receipted, and accountable. | Freeform mutation without artifacts/receipts is invalid. |
| Branch/Reconciliation | Multiplicity of worlds preserves canonical center and return. | Loss of canonical return path is fragmentation and invalid. |

---

## Compact Statement

> 8 questions ask what must remain true.  
> 7 algorithms provide enforceable lanes for each answer.  
> 2 proof forms per lane (constructive + falsification) make every claim both buildable and break-testable.  
> Therefore the framework targets **112 proofs**.
