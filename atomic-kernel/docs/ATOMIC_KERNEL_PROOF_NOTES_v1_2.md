# Atomic Kernel — Proof Notes and Derivations
## Companion to Normative Core v1.2

**Version**: 1.2  
**Status**: Proof/Derivation Notes  
**Role**: Explanatory, not normative by itself.

Related normative core:
- `ATOMIC_KERNEL_NORMATIVE_CORE_v1_2.md`

---

## 1. Quotient Framing

Primary question:

```text
What can be removed while preserving canonical unfold/replay/projection?
```

This document records rationale for why retained components survive that quotient test.

---

## 2. Deterministic Orbit Derivation

For fixed width `n`, `Δ` is a total map on finite `ℤ₂ⁿ`.

Consequences:

- replay determinism: repeated application yields unique trajectory
- eventual periodicity: finite-state recurrence

This supports bounded replay/state claims used by runtime and tests.

---

## 3. Period-8 Empirical Alignment and 73

Observed for `n=16` in current fixture lane:

```text
period = 8
```

Decimal periodicity note:

- multiplicative order `ord_p(10)=8`
- smallest such prime is `p=73`
- `1/73 = 0.(01369863)`

Derived block:

```text
B = [0,1,3,6,9,8,6,3], W = 36
```

Used for orbit/offset coordinate interpretation in replay projection.

---

## 4. Mixed-Radix Reversibility Sketch

Given radices `r0..rk-1` (`ri>=2`):

- encoding uses repeated division with remainders
- decoding reconstructs via nested multiplication/addition

This is canonical mixed-radix expansion, giving exact roundtrip identity:

```text
decode(encode(v,r), r) = v
```

Current test lane enforces this over default basis specs.

---

## 5. Frame Pair Interpretation

Frame is interpreted as:

```text
frame = (plane, basis_spec)
```

- structural role comes from plane (`FS/GS/RS/US`)
- representational coordinate law comes from `basis_spec`

This separates structure from notation and keeps projection reversible.

---

## 6. Scoped Interpretation Notes

Escape/control operations are constrained by bounded scope stack behavior.

Needed properties:

- no implicit infinite persistence
- explicit push/pop semantics
- deterministic return to prior context

These constraints prevent replay divergence from parser/context ambiguity.

---

## 7. Carrier Non-Authority Rationale

Carrier path:

```text
canonical payload
-> artifact_package.v1
-> Aztec
-> lossless PNG
-> decode
-> verify
-> apply
```

Why this preserves authority boundary:

- transport form is replaceable projection
- payload verification is algorithmic (`sha256`)
- unknown kinds / invalid fingerprints fail closed

Thus carrier convenience does not become truth authority.

---

## 8. Suggested Future Proof Lanes

- algebraic/property tests over larger sampled value domains
- basis-spec mutation tests (version drift rejection)
- carrier kind differential tests (allowlist enforcement)
- cross-runtime proof checks for basis projection equivalence

---

## 9. Clarification

Algorithms define invariants.
Artifacts instantiate algorithms.
UI, carriers, and render forms are projections over those invariants.
