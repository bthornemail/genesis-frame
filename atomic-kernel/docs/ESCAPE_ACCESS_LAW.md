# Escape Access Law

## Canonical Entry, Literalization, Scope, and Return for In-Band Control in the Atomic Kernel

**Status:** Normative Draft  
**Authority:** Extension - Control / Artifact Access Layer  
**Depends on:** `CONTROL_PLANE_SPEC.md`, `kernel.py`, `AtomicKernelCoq.v`, `AZTEC_ARTIFACT_SPEC.md`  
**Date:** 2026

---

## Abstract

This specification defines the lawful mechanism by which a canonical artifact stream may temporarily leave default payload interpretation and enter control, extension, or context-changing interpretation without losing replay determinism.

Escape is finite, typed, literalizable, and fail-closed. It is not an unbounded meta-language layered over payload.

---

## 1. First Principle

> A stream cannot escape itself implicitly.

If a stream carries both data and in-band control, escape must be explicit and bounded, otherwise decoders diverge.

---

## 2. Core Definitions

- **Default payload interpretation:** normal data mode.
- **Escape introducer:** reserved control symbol entering escape-pending mode.
- **Literalization:** lawful way to emit reserved symbols as data.
- **Scope:** finite extent of interpretive override.
- **Return:** deterministic restoration to default mode.
- **Infinite escape stream:** forbidden recursive-unbounded escape regime.

---

## 3. Design Goals

- **G1** Single-channel compatibility  
- **G2** Literal transparency  
- **G3** Finite scope  
- **G4** Deterministic return  
- **G5** Fail-closed behavior

---

## 4. Canonical Escape Symbol

`ESC` is the canonical access introducer.

It is structural, not advisory.

---

## 5. Core Validity Rule

> An escape is valid only if it is locally recognizable, explicitly literalizable, finitely scoped, and deterministically closed.

---

## 6. Literal Escape Rule

```text
ESC ESC  => literal ESC payload
```

No other doubled control token is implicitly literalized unless separately specified.

---

## 7. Allowed Escape Scopes

- next-unit
- next-record
- next-group
- next-file
- explicit quoted-literal
- explicit structural region

---

## 8. Forbidden Scope Forms

- implicit infinite persistence
- time-based closure
- external-state closure
- recursive unbounded self-opening

All are non-canonical.

---

## 9. Decoder State Model

```text
S = (channel, lane, numsys, mode, scope_stack)
S0 = (FS, lane0, default_numsys, DATA, ∅)
```

No hidden decoder state is allowed.

---

## 10. Required Modes

- `DATA`
- `ESCAPE_PENDING`
- `CONTROL`
- `QUOTED_LITERAL`

Extensions are allowed only if explicitly scoped.

---

## 11. Normative Transition Rules

Let:

```text
δ : (S, token) -> (S', output?)
```

Required rules:

- **E1** DATA + non-control payload -> emit payload
- **E2** DATA + ESC -> ESCAPE_PENDING
- **E3** ESCAPE_PENDING + ESC -> emit literal ESC, return DATA
- **E4** ESCAPE_PENDING + next-unit control target -> bounded CONTROL
- **E5** ESCAPE_PENDING + structural-scope target -> bounded CONTROL
- **E6** ESCAPE_PENDING + QUOTE_OPEN -> QUOTED_LITERAL
- **E7** QUOTED_LITERAL + QUOTE_CLOSE -> pop quoted scope, return prior mode
- **E8** ESCAPE_PENDING + unknown target -> reject
- **E9** Scope completion -> deterministic pop and return

---

## 12. Return-to-Default Law

Every valid escape carries its own explicit closure condition.

No heuristic return is permitted.

---

## 13. Scope Stack Discipline

- nested explicit scopes: allowed
- invalid overlap: reject
- dangling scopes at end-of-stream: reject
- implicit auto-healing: forbidden

---

## 14. Structural Control Interaction

`FS/GS/RS/US` are structural controls, not escapes.

They may close bounded escape scopes when the scope law says so.

---

## 15. Numeric-System Interaction

Numeric changes under escape are projection-law changes, not value mutation.

After scope closure, prior/default interpretation is restored.

---

## 16. Custom Codepoint Interaction

Escape may scope custom codepoint interpretation, provided finite scope + deterministic return are preserved.

---

## 17. Framing Interaction

COBS/framing and escape access are distinct layers:

- framing resolves packet boundaries
- escape resolves in-band interpretation boundaries

No implementation may collapse them into one ambiguous mechanism.

---

## 18. Artifact Graph Interaction

Escape scopes do not leak across node boundaries unless explicit structural edge law permits continuation.

---

## 19. Error Conditions (Reject)

- **R1** ESC at end-of-stream
- **R2** unknown escape target
- **R3** unterminated quoted-literal
- **R4** invalid overlapping scopes
- **R5** implicit persistence past lawful end
- **R6** scope underflow
- **R7** cross-node leakage without law

---

## 20. Security Rationale

Unbounded/ambiguous escape enables parser differentials, structure smuggling, context confusion, and replay divergence.

Finite typed escape with explicit closure removes this ambiguity class at law level.

---

## 21. Formal Laws

- **A1** Escape introducer law (`ESC`)
- **A2** Literalization law (`ESC ESC`)
- **A3** Finite scope law
- **A4** Deterministic return law
- **A5** Fail-closed law
- **A6** Bounded Non-Closure law

---

## 22. Runtime Integration Clarification

### 22.1 Canonical ESC vs Local Projection Pause

Canonical escape scope is stream-local and law-defined.

Local UI pause (for interaction/readability) is projection behavior and is non-authoritative.

### 22.2 Projection Pause Non-Authority Law

> A local UI pause, advisory panel dwell time, or transport latency may suspend projection refresh, but it does not define, extend, or close canonical escape scope.

Canonical escape scope is determined only by stream-local law and explicit structural closure.

### 22.3 Interaction Escape Subtype (Advisory Extension)

An interactive ESC window may collect advisory proposals and witness receipts, but canonical mutation occurs only through deferred lawful commit at frame boundary.

### 22.4 Bounded Non-Closure Law (A6)

> Interpretive openness is permitted only inside explicitly bounded escape scopes, and every such scope MUST terminate in deterministic return to canonical law.

This is the closure/non-closure boundary:

- closure is mandatory for law state and commit path,
- bounded non-closure is permitted for advisory interpretation and proposal formation.

---

## 23. Reduction Statement

The canonical stream may open temporary access to higher interpretation only under finite law.

Escape is lawful only when local, typed, replayable, literalizable, and closed.

---

## 24. Summary

- `ESC` introduces bounded access
- `ESC ESC` emits literal ESC
- every escape has finite scope
- every scope has deterministic closure
- malformed/unknown forms fail closed
- no time-based closure
- no implementation-defined closure
- no infinite escape stream
- bounded interpretive openness only inside explicit escape scope

```text
same stream
→ same control access transitions
→ same scope behavior
→ same return points
→ same canonical unfold
```
