# Atomic Kernel — Normative Core
## Reduction-Based Core Law (v1.2)

**Version**: 1.2  
**Status**: Normative Core  
**Authority**: Algorithms only. Representations are projections.

---

## 0. Reduction Test

A structure is foundational iff removing it changes canonical replay/projection output.

---

## 1. Kernel Evolution Law

State space:

```text
x ∈ ℤ₂ⁿ
```

Delta law:

```text
Δ(x) = rotl(x,1) ⊕ rotl(x,3) ⊕ rotr(x,2) ⊕ C
```

with width mask `2ⁿ-1`.

Normative requirements:

- deterministic replay for fixed `(C,n,x0)`
- bounded orbit on finite state space

---

## 2. Reversible Basis Law

A basis is either simple (`2`, `8`, `10`, `16`, `36`, `codepoint`) or mixed radix.

Mixed radix:

```text
radices = [r0, r1, ..., rk-1], ri >= 2
```

Algorithms:

- `mixed_encode(v, radices)` by repeated quotient/remainder
- `mixed_decode(coords, radices)` by reconstruction

Normative invariant:

```text
mixed_decode(mixed_encode(v, r), r) = v
```

Projection invariant:

```text
interpret(project(v, basis), basis) = v
```

---

## 3. Structural Plane Law

Four canonical structural planes:

- `FS` context
- `GS` grouping
- `RS` record
- `US` unit

Interaction is recursively reduced to:

```text
select -> project_artifact(plane) -> select
```

---

## 4. Frame Law

Minimal frame definition:

```text
frame = (plane, basis_spec)
```

Where:

- `plane ∈ {FS, GS, RS, US}`
- `basis_spec` is validated, versioned, and deterministic

Plane chooses structure. Basis chooses notation/coordinate interpretation.

---

## 5. Scoped Interpretation Law

Escape/control context changes must be bounded:

- explicit push/pop scope
- deterministic return
- no unbounded recursive context

---

## 6. Carrier Boundary Law

Canonical sharing wrapper:

```text
artifact_package.v1
```

Verification sequence is mandatory:

```text
decode -> parse -> validate kind/schema -> fingerprint verify -> apply
```

If verification fails, payload MUST NOT be applied.

---

## 7. Irreducible System

```text
1. Δ(x)               state evolution
2. mixed_encode       coordinate decomposition
3. mixed_decode       coordinate reconstruction
4. project/interpret  reversible basis projection
5. FS/GS/RS/US        structural access
6. verify()           transport integrity
```

---

## 8. Authority Statement

The algorithms define invariants.
Artifacts are verifiable instances of those algorithms.
All other forms are projections.
