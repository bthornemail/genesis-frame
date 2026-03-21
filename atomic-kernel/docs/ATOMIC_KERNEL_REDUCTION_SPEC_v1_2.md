# Atomic Kernel
## A Reduction-Based Formal Specification

**Version**: 1.2 (Algorithmic Form)  
**Status**: Proof-Oriented Draft  
**Authority**: Algorithms only. All representations are projections.

---

# 0. Preamble — The Reduction Principle

The system is defined by a single test:

> **Quotient Test**  
> What structure can be removed while the same canonical unfold / replay / projection still results?

A structure is **foundational** iff removing it changes the canonical output.

Everything else is:

- projection
- convenience
- or artifact

---

# 1. Minimal Core: The Kernel Law

## Definition 1.1 — State Space

Let:

```text
x ∈ ℤ₂ⁿ   (fixed-width bitspace, e.g. n = 16)
```

## Definition 1.2 — Rotation Operators

```text
rotl(x, k) = ((x << k) | (x >> (n - k))) mod 2ⁿ
rotr(x, k) = ((x >> k) | (x << (n - k))) mod 2ⁿ
```

## Definition 1.3 — Delta Law

```text
Δ(x) = rotl(x,1) ⊕ rotl(x,3) ⊕ rotr(x,2) ⊕ C
```

Where:

- `⊕` = bitwise XOR
- `C ∈ ℤ₂ⁿ` is constant
- result masked to width n

## Algorithm 1 — Step

```python
def step(x, C, n):
    mask = (1 << n) - 1
    def rotl(v, k): return ((v << k) | (v >> (n - k))) & mask
    def rotr(v, k): return ((v >> k) | (v << (n - k))) & mask
    return (rotl(x,1) ^ rotl(x,3) ^ rotr(x,2) ^ C) & mask
```

---

## Theorem 1 — Deterministic Replay

For fixed `(C, n, x₀)`:

```text
xₖ = Δ⁽ᵏ⁾(x₀)
```

is uniquely determined.

**Proof**: Δ is a total function on a finite set. ∎

---

## Theorem 2 — Bounded Orbit

```text
∃ p ≤ 2ⁿ such that Δ⁽ᵖ⁾(x₀) = x₀
```

**Proof**: Pigeonhole principle on finite state space. ∎

---

## Empirical Result (n = 16)

Observed:

```text
period = 8
```

This is **not chosen**, but derived.

---

# 2. Derived Numeric Structure

## Definition 2.1 — Repeating Decimal Period

For prime `p`, the decimal period of `1/p` is the multiplicative order of 10 mod p.

## Observation

```text
ordₚ(10) = 8  →  p = 73 (smallest)
```

## Definition 2.2 — Block

```text
1/73 = 0.(01369863)
B = [0,1,3,6,9,8,6,3]
```

## Definition 2.3 — Weight

```text
W = sum(B) = 36
```

---

## Theorem 3 — Orbit-Compatible Decomposition

Given position `k`:

```text
orbit, offset = divmod(k, W)
```

This yields a valid coordinate system over replay.

**Reason**: W is invariant under derived sequence. ∎

---

# 3. Basis / Coordinate Law

This is the **first non-trivial extension beyond the kernel**.

## Definition 3.1 — Mixed Radix Encoding

Given:

```text
radices = [r₀, r₁, ..., rₖ₋₁]
```

## Algorithm 2 — mixed_encode

```python
def mixed_encode(v, radices):
    coords = []
    for r in radices:
        coords.append(v % r)
        v //= r
    coords.append(v)
    return coords
```

## Algorithm 3 — mixed_decode

```python
def mixed_decode(coords, radices):
    v = coords[-1]
    for i in reversed(range(len(radices))):
        v = coords[i] + radices[i] * v
    return v
```

---

## Theorem 4 — Reversibility

```text
mixed_decode(mixed_encode(v, r), r) = v
```

**Proof**: Standard mixed radix expansion. ∎

---

## Algorithm 4 — Projection

```python
def project_value(v, basis_spec):
    if basis_spec.kind == "mixed":
        return mixed_encode(v, basis_spec.radices)
    if basis_spec.kind == "16":
        return hex(v)
    if basis_spec.kind == "10":
        return str(v)
    ...
```

## Algorithm 5 — Interpretation

```python
def interpret_value(repr, basis_spec):
    if basis_spec.kind == "mixed":
        return mixed_decode(repr, basis_spec.radices)
    ...
```

---

## Theorem 5 — Projection Law

```text
interpret(project(v, b), b) = v
```

for all valid `basis_spec`.

---

# 4. Codepoint Space as Basis

## Definition 4.1 — Unicode Decomposition

```text
value = plane × 65536 + offset
```

## Representation

```text
radices = [65536]
coords = [offset, plane]
```

---

## Theorem 6 — Unicode is Mixed Radix

Unicode codepoints are a special case of Algorithm 2.

---

# 5. Structural Control Law

Define four projections:

```text
FS — context
GS — grouping
RS — record
US — unit
```

## Algorithm 6 — Structural Projection

```python
def project_artifact(node, plane):
    if plane == "FS":
        return context(node)
    if plane == "GS":
        return group(node)
    if plane == "RS":
        return record(node)
    if plane == "US":
        return unit(node)
```

---

## Theorem 7 — Structural Completeness

Any artifact interaction can be reduced to repeated application of:

```text
select → project_artifact → select
```

---

# 6. Escape / Scoped Interpretation

## Definition

A bounded stack:

```text
push(scope)
pop(scope)
```

## Constraint

- no unbounded recursion
- deterministic return

---

# 7. Artifact / Carrier Law

## Definition — Canonical Package

```json
{
  "type": "artifact_package",
  "payload": "bytes",
  "fingerprint": "sha256(payload)"
}
```

## Algorithm 7 — Verify

```python
def verify(pkg):
    return sha256(pkg.payload) == pkg.fingerprint
```

---

## Theorem 8 — Transport Non-Authority

If verification fails, payload MUST NOT be applied.

---

# 8. Reduction Result

We now test removal:

| Component | Removable? | Reason |
| --- | --- | --- |
| Δ law | ❌ | breaks replay |
| mixed radix | ❌ | breaks coordinate recovery |
| projection law | ❌ | breaks reversibility |
| FS/GS/RS/US | ❌ | breaks structural access |
| artifact verify | ❌ (for sharing) | breaks integrity |

---

# 9. Final Minimal System

The irreducible system is:

```text
1. Δ(x)              — state evolution
2. mixed_encode      — coordinate decomposition
3. mixed_decode      — coordinate reconstruction
4. project/interpret — reversible projection
5. FS/GS/RS/US       — structural access
6. verify()          — transport integrity
```

---

# 10. Final Statement

> The system consists of a deterministic state transformation over a finite space, a reversible coordinate decomposition, a projection/interpretation equivalence, a four-plane structural access law, and a verified transport boundary.

---

# 11. Important Clarification

> The algorithms define the invariant.  
> Artifacts are verifiable instances of those algorithms.  
> All other representations are projections.
