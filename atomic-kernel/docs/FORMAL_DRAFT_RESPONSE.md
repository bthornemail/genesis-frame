# Atomic Kernel — Formal Draft v1.0 Response
## What Each Core Idea Maps To in the Running System

**Status:** Implementation Audit  
**Authority:** Tests, golden vectors, and Coq proof — not this document  
**Rule:** This document describes the current artifact state. Disagreements are resolved by running `python3 tests/test_all.py` and comparing to `tests/golden_parity.json`.

---

## Preamble: The Reduction Principle

The formal draft asks the right question:

> What structure can be removed while the same canonical unfold, replay, and projection still results?

The answer is already in the code. This document maps each core idea in the draft to exactly where it lives in the implementation, what is proven, and what three things remain pending before Section 12 is satisfied.

---

## Core Idea 1 — The Kernel Is One Bounded State Law

**Draft definition:**
```
delta(n, x) = mask(n, rotl(x,1) XOR rotl(x,3) XOR rotr(x,2) XOR C)
```

**Where it lives:** `kernel.py` — the function `delta(n, x)`.

The constant C is `constant_of_width(n)`: the byte 0x1D repeated for each byte of width n. For n=16: `C = 0x1D1D`. The choice of 0x1D is the GS (Group Separator) byte — the same value used as Channel 1 in the control plane. The transport and computation layers share the same primitive marker.

**Theorem 1.1 (Determinism) — verified:**
```python
delta(16, 0x5D17) == delta(16, 0x5D17)   # True, always
```
Proven in Coq as `delta_deterministic`: `∀ n x y, x = y → delta n x = delta n y`.

**Theorem 1.2 (Boundedness) — verified across all 5 widths:**
```
delta(16,  0xFFFF)   = 0xE2E2    < 2^16   ✓
delta(32,  0xFFFFFFFF) = 0xE2E2E2E2 < 2^32  ✓
delta(64,  max)      = 0xE2E2... < 2^64   ✓
delta(128, max)      = 0xE2E2... < 2^128  ✓
delta(256, max)      = 0xE2E2... < 2^256  ✓
```
The mask is the last operation; the output is always in range. Proven in Coq by construction.

**The draft states:** "This is the only generative law. Everything else must be derived from it or projected from it." This is correct and already expressed in `FROM_FIRST_PRINCIPLES.md`. The derivation chain is:

```
delta law (chosen)
  → period = 8 (property of the law on 16-bit space)
    → prime 73 (smallest p with ord_p(10) = 8)
      → block B = [0,1,3,6,9,8,6,3] (digits of 1/73)
        → W = 36 (sum(B))
          → orbit/offset = divmod(position, 36)
```

Nothing after the first line was chosen. The law chose everything else.

---

## Core Idea 2 — Replay Is the Only Canonical Time

**Draft definition:**
```
x₀ = seed
x_{t+1} = delta(n, x_t)
replay(seed, t) = x_t
```

**Where it lives:** `kernel.py` — the function `replay(n, seed, steps)`.

**Theorem 2.1 (Uniqueness) — verified:**
```python
replay(16, 0x0001, 8) == replay(16, 0x0001, 8)   # True, always
```
Proven in Coq as `replay_deterministic`.

**Theorem 2.2 (Eventual repetition) — verified:**
```
Period of delta(16) from seed 0x0001 = 8
```
The state space has size 2^16 = 65,536. A deterministic function on a finite set must revisit. Period 8 is the observed period for the 16-bit law from seed 0x0001. It is a property of the law, not a choice.

**Full golden sequence (16-bit, seed 0x0001):**
```
t=0: 0x0001    t=1: 0x5D17    t=2: 0x98CC    t=3: 0xCCD3
t=4: 0x1110    t=5: 0xB3F9    t=6: 0x89DD    t=7: 0x223D
```
Frozen in `tests/golden_parity.json` for all five widths.

**The draft's consequence** — "canonical temporal structure without any external clock" — is the entire motivation for the system. The crystal does not drift. It does not require NTP, GPS, or hardware. Same seed, same tick, same output, everywhere, always.

---

## Core Idea 3 — Equality Is Exact Bit Identity

**Draft definition:** `x = y iff their n-bit representations are identical`.

**Where it lives:** Every test in `tests/test_all.py`. The comparison is always `==` on integers or exact string comparison on hex representations. There is no fuzzy matching, no tolerance, no "approximately equal."

**The golden parity vectors** in `tests/golden_parity.json` are exact hex strings. A mismatch of one bit in any of the 40 stored values causes test failure. The Coq proof compares exact values. The conformance hash is `sha3_256` of the canonical byte sequence — a hash function with no tolerance for bit differences.

**The draft's consequence** — "'close' is not valid" — is enforced structurally. The system has no mechanism for approximate comparison. Agreement is binary.

---

## Core Idea 4 — Change Is Differential, Not Interpretive

**Draft definition:** `E2(x_t, x_{t-1}) = x_t XOR x_{t-1}`.

**Where it lives:** The differential is computable from any two consecutive states. It is not currently a named function in the codebase — it is used implicitly in the OID chaining in `identity.py` (the OID chain XORs previous state into the next seed, which is a differential operation).

**Theorem 4.1 (Zero differential iff no change) — verified:**
```
0x0001 XOR 0x0001 = 0x0000   (no change → zero differential)
0x0001 XOR 0x5D17 = 0x5D16   (change → nonzero differential)
```

**Theorem 4.2 (Differential is reproducible) — follows from Theorem 1.1:** since replay is deterministic, the states are deterministic, and the XOR of two deterministic values is deterministic.

**The admitted differentials for the golden 16-bit sequence:**
```
E2(t=1, t=0) = 0x5D16
E2(t=2, t=1) = 0xC5DB
E2(t=3, t=2) = 0x541F
E2(t=4, t=3) = 0xDDC3
E2(t=5, t=4) = 0xA2E9
E2(t=6, t=5) = 0x3A24
E2(t=7, t=6) = 0xABE0
```
Frozen in `tests/admitted_invariants.json`.

---

## Core Idea 5 — Normalization Requires Invariants, Not Opinions

**Draft definition:** `normalize: byte[] → byte[]` — classify bytes as STRUCTURE or PAYLOAD, remove structural bytes, reversibly unstuff escape forms, emit canonical payload ordering.

**Where it lives:** `CONTROL_PLANE_SPEC.md`. The classifier is the FLAG bit:

```
Bit 7 = 0 → PAYLOAD   (range 0x01–0x7F after COBS encoding)
Bit 7 = 1 → STRUCTURE  (range 0x80–0xFF, control words)
0x00       → DELIMITER  (COBS packet boundary)
```

The three ranges are disjoint and exhaustive. No byte is ambiguous. Classification requires reading one bit.

**The invariant that is preserved:** FS/GS/RS/US retain their Unicode canonical identities (U+001C–U+001F) regardless of which NUMSYS is active. Context changes interpretation of payload bytes. It never changes the meaning of structural bytes.

**Theorem 5.1 (Normalization is representation reduction):** two encoded streams with the same canonical payload under the admitted normalization rules normalize to the same byte sequence. This holds because the classifier and rewrite rules are fixed (in the spec) and deterministic.

**Theorem 5.2 (No normalization without invariants):** the invariant comes first. The FLAG bit classifier is the invariant. Normalization is its operational consequence — apply the classifier, separate STRUCTURE from PAYLOAD, the result is canonical.

---

## Core Idea 6 — Boundaries and Relations Must Be Explicit

**Draft definition:**
```
FS = 28 (0x1C), GS = 29 (0x1D), RS = 30 (0x1E), US = 31 (0x1F)
E3(xs) = { i | xs[i] ∈ {FS, GS, RS, US} }
E5(boundary_events) = DAG
```

**Where it lives:** `CONTROL_PLANE_SPEC.md` (boundary encoding) and `AZTEC_ARTIFACT_SPEC.md` (DAG construction).

The four separator bytes are the top four values in the Unicode C0 control range — the only C0 codes where bits [4:2] = 111. Their values (28–31) match the draft exactly.

**Theorem 6.1 (Concatenation is not enough) — stated and proven in `AZTEC_ARTIFACT_SPEC.md` §7.1:** `A ++ B` does not encode whether B is sibling, child, continuation, or unrelated to A. A typed FS/GS/RS/US edge does.

**Theorem 6.2 (Explicit relation is sufficient) — implemented:** a DAG with labeled edges and deterministic traversal rules (depth-first, FS < GS < RS < US at each node) defines a unique reconstruction order. The traversal is deterministic because the edge types form a total order and depth-first traversal on a DAG is deterministic.

---

## Core Idea 7 — Observation Is Invariant Projection

**Draft definition:**
```
E1(x) = x mod 7
E9(x) = x mod 37
J(x) = (E1(x), E9(x))
```

**Where it lives:** `observer.py` currently exposes orbit, offset, position, color, and symbol as projections of state. The specific projections E1 and E9 from the formal draft are not yet in the observer.

**Admitted invariant values (frozen in `tests/admitted_invariants.json`):**
```
t=0  state=0x0001  E1=1   E9=1
t=1  state=0x5D17  E1=3   E9=3
t=2  state=0x98CC  E1=0   E9=7
t=3  state=0xCCD3  E1=5   E9=6
t=4  state=0x1110  E1=0   E9=2
t=5  state=0xB3F9  E1=6   E9=8
t=6  state=0x89DD  E1=6   E9=32
t=7  state=0x223D  E1=1   E9=33
```

**Theorem 7.1 (Observation does not alter replay):** `E1` and `E9` are pure functions from state to integer. They have no effect on `delta` or `replay`. The proof is structural — the functions take state as input and return a value; they do not modify any mutable state.

**Theorem 7.2 (Composability as products):** `J(x) = (E1(x), E9(x))` is deterministic since both components are deterministic. Admission requires artifact agreement — the values above are the artifact.

**The draft's note on 73:** "Numbers such as 73 are not foundational unless derived reproducibly from replay and frozen as artifacts." The derivation is reproducible and frozen:

```
Step 1: period of delta(16) from seed 0x0001 = 8  (computed from replay)
Step 2: smallest prime p with ord_p(10) = 8 → p = 73  (number theory)
Step 3: digits of 1/73 = [0,1,3,6,9,8,6,3] = block B  (long division)
Step 4: sum(B) = 36 = W  (arithmetic)
```

73 is now frozen in `tests/admitted_invariants.json` under `73_derivation`. It is derived, not foundational. Its derivation is reproducible by any implementation.

---

## Core Idea 8 — Agreement Is the Only Validator

**Draft definition:** agreement holds iff normalize, replay, admitted invariants, artifact, and hash all match between independent implementations A and B.

**Current status:**

```
normalize_A = normalize_B    ✓  (single Python implementation, spec is normative)
replay_A    = replay_B       ✓  (Python kernel.py matches Coq AtomicKernelCoq.v
                                 golden vectors for all 5 widths × 8 steps)
I_A         = I_B            ◐  (E1/E9 frozen in artifact; not yet in test suite)
artifact_A  = artifact_B     ✓  (58/58 tests, sha3_256 hash matches)
hash_A      = hash_B         ✓  (conformance result verified)
```

**Theorem 8.1 (Bit mismatch falsifies):** if any agreed artifact differs at the bit level, at least one implementation is invalid. This is enforced by the test suite — a single bit mismatch in any golden vector causes test failure.

**Theorem 8.2 (Agreement replaces external authority):** the artifact comparison itself decides acceptance. No external semantic authority. This is operational — the system accepts or rejects by hash comparison, not by argument.

---

## Derived Principles (Section 9)

**9.1 Binary basis:** the operational base is 2. The state is a bounded binary integer. All operations (rotl, rotr, XOR, mask) are binary. This follows from the delta law definition.

**9.2 E1 = x mod 7:** admitted. Values frozen above. Smallest nontrivial modular surface — 7 is the smallest prime that divides 2^3 - 1 and appears naturally in the Fano plane (7 points, 7 lines). Admitted as a scalar introspection surface.

**9.3 E9 = x mod 37:** admissible. Values frozen above. Note: 37 is related to the decimal period structure — 1/37 = 0.027027... with period 3. The derivation from the kernel is not as direct as 73's derivation; it is admitted as an extension surface pending a tighter derivation argument.

**9.4 73 is derived, not foundational:** confirmed. The derivation is now frozen as an artifact (see above). 73 satisfies the draft's condition: "derived reproducibly from replay and frozen as artifacts."

---

## Composability of Closed Systems (Section 10)

**Definition:** a closed system is `(Law, State, Equality, Diff, Normalize, Boundary, Invariants, Agreement)`.

The Atomic Kernel system, filling this tuple:

```
Law         = delta(n, x)
State       = bounded n-bit integer
Equality    = exact bit identity
Diff        = XOR of consecutive states
Normalize   = FLAG-bit classifier + COBS unstuffing
Boundary    = FS/GS/RS/US typed edges (E3, E5)
Invariants  = E1 (x mod 7), E9 (x mod 37), J = (E1, E9)
Agreement   = sha3_256 artifact comparison
```

**Theorem 10.1 (Parallel composition preserves determinism):** two independent kernel instances running different seeds produce independent deterministic orbits. Their product is deterministic because each component is deterministic. An observer reading both streams sees two independent canonical sequences.

**Theorem 10.2 (Coupled composition):** coupling via shared state (e.g., the OID chain XORs previous state into the next seed) is deterministic because XOR is deterministic. The coupling law `seed_{t+1} = seed XOR state_t` is deterministic.

**Theorem 10.3 (Shared invariants require compatibility):** if two systems share an invariant (e.g., both expose E1), the composed system's closure requires that E1 be preserved by both transitions. This is satisfied because E1 is a pure read from state — it does not participate in the transition law.

---

## Completion Checklist (Section 12) — Current Status

```
KERNEL COMPLETENESS
  ✓  delta defined                    kernel.py
  ✓  boundedness proven               Theorem 1.2 + Coq
  ✓  replay uniqueness proven         Theorem 2.1 + Coq replay_deterministic
  ✓  eventual repetition acknowledged period=8, Theorem 2.2

NORMALIZATION COMPLETENESS
  ✓  classifier fixed                 FLAG bit, CONTROL_PLANE_SPEC.md
  ✓  escape/unstuff rules fixed       COBS + control word parser
  ◐  normalization artifacts frozen   PENDING: canonical stream hash

ARTIFACT COMPLETENESS
  ✓  canonical serialization fixed    CONTROL_PLANE_SPEC.md encoding table
  ✓  hash procedure fixed             sha3_256(canonical_bits)
  ✓  golden vectors frozen            tests/golden_parity.json

AGREEMENT COMPLETENESS
  ◐  two independent implementations  Python + Coq; runtime #2 needed
  ◐  all admitted invariants agree    E1/E9 frozen; not yet in test suite
  ✓  artifacts match bit-for-bit      58/58 tests

SCOPE COMPLETENESS
  ✓  no ungrounded extension claims   EXTD = explicit gateway
```

**Done: 11/14. Pending: 3.**

**The three pending items:**

1. **Normalization artifacts frozen.** The CONTROL_PLANE_SPEC normalization rules are defined. The frozen artifact is the sha3_256 hash of a canonical stream produced by a compliant encoder. This requires writing the reference encoder and producing the first frozen canonical stream.

2. **Two independent runtime implementations.** Python (`kernel.py`) and Coq (`AtomicKernelCoq.v`) agree on the delta law. A second runtime implementation — in a different language (Haskell, C, Rust, JavaScript) — that reads the same parity vectors and produces matching output would satisfy this.

3. **Admitted invariants in the test suite.** E1 and E9 values are frozen in `tests/admitted_invariants.json`. Adding test assertions that verify these values against `kernel.replay` output would close this item in two dozen lines.

Items 1 and 3 are straightforward. Item 2 is the work that takes time but is not architecturally complex — the delta law is simple enough to implement in any language in under 50 lines.

---

## What Is Outside Scope (Section 11)

The draft correctly identifies these as outside scope:

- Geometric ontology (Fano plane as metaphysics vs. as finite field geometry — the latter is in the spec, the former is not)
- E8 literal equivalence (noted in docs as a numerical coincidence, not a normative claim)
- Metaverse semantics (a projection layer above the kernel, not part of it)
- Operator metaphysics (the spiritual framework in the Speaker documents is advisory, not foundational)

Any of these may become admitted extensions. None are admitted now. The gate is: provide a function, an artifact, and a falsifier. The EXTD mechanism in the control plane is the explicit admission gate.

---

## The Diff Rule (Section 15)

Accepted. This document is a versioned response to the formal draft. Future changes proceed by diff. The canonical artifacts are:

```
tests/golden_parity.json          (kernel law, 5 widths × 8 steps)
tests/admitted_invariants.json    (E1, E9, E2, 73 derivation — frozen)
docs/AtomicKernelCoq.v            (Coq proof — compiled)
```

Arguments that do not produce a diff against one of these files are advisory, not foundational.
