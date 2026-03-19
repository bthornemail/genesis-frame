# Aztec-Encoded PNG Artifacts
## Canonical Bit Surfaces, Context Separation, and Semantic Graph Joining

**Status:** Normative Draft  
**Authority:** Extension — Artifact Projection Layer  
**Depends on:** `CONTROL_PLANE_SPEC.md`, `kernel.py`, `AtomicKernelCoq.v`  
**Date:** 2026

---

## Abstract

This specification defines how the Atomic Kernel uses Aztec barcode symbols rendered as PNG images as **canonical artifact surfaces** — not data containers. It establishes the no-loss encoding requirements, the separation of context from payload, the mapping of the 4-channel × 16-lane runtime onto the Aztec grid geometry, and the rule that multiple symbols are joined structurally as abstract semantic graphs, not concatenated as raw byte streams. The Klein four-group and projective geometry of GF(2)^4 underlie the numeric structure of the runtime dimensions.

---

## 1. First Principle: What an Artifact Is

A file is a mutable container. It is named, located, and its content changes.

An artifact is something different. An artifact is a **deterministic projection of a canonical bit sequence**. It is not stored — it is computed. It is not named — it is addressed by the hash of its bit content. It cannot change, because changing it produces a different artifact, not a modified version of the same one.

The Atomic Kernel artifact stack has three layers:

```
canonical_bits          ← the truth (authoritative)
    ↓ aztec_encode()
aztec_symbol_grid       ← the representation (derived)
    ↓ png_render()
png_bytes               ← the transport (projection of representation)
```

The PNG is not the artifact. The Aztec symbol is not the artifact. The canonical bit sequence is the artifact. PNG and Aztec are two successive projections of it.

This distinction has consequences:

- Two PNGs with different DEFLATE compression levels that decode to the same pixel grid represent the same artifact.
- One PNG rotated 90 degrees represents the same artifact if the Aztec decoder handles orientation (Aztec is orientation-invariant by design).
- A PNG printed on paper and rescanned represents the same artifact if the Aztec ECC recovers the bit sequence correctly.

The representation is irrelevant. Only the canonical bit sequence matters.

---

## 2. Why Aztec Specifically

Aztec codes are chosen over QR codes, Data Matrix, and other 2D symbologies for properties that align with the kernel's determinism requirements.

**No quiet zone.** Aztec symbols do not require a blank border region. The central bull's-eye provides all orientation information. This means symbols can be placed adjacent to each other without interference — a prerequisite for the structural graph layout described in Section 7.

**Byte mode encodes all 256 values.** In byte mode, any value from 0x00 to 0xFF is representable directly. There is no escaping, no substitution, no mode-switching overhead for control bytes. The kernel control codes FS (0x1C), GS (0x1D), RS (0x1E), US (0x1F), and NULL (0x00) are all encodable without special treatment.

**Deterministic layout.** Given the same input bytes, the same encoder version, and the same symbol size, the output module grid is always identical. This is a necessary condition for content addressing.

**Reed-Solomon error correction.** Aztec uses RS over GF(2^6), GF(2^8), GF(2^10), or GF(2^12) depending on symbol size. This provides integrity verification independent of the kernel's own hash layer. The two integrity checks are complementary: RS catches physical damage; the kernel hash catches tampering.

**Orientation invariance.** The bull's-eye pattern allows decoding from any of four rotations without additional markers. This matters when symbols are physically embodied (printed, displayed, photographed) and may arrive rotated.

---

## 3. No-Loss Encoding — Four Invariants

No-loss is not a single property. It is four distinct invariants that must all hold simultaneously.

### N1 — Aztec byte mode only

The Atomic Kernel never uses Aztec's internal text mode, digit mode, or upper/lower modes. All payload bytes are encoded in byte mode, which accepts any byte value without transformation.

Aztec's internal mode switching can introduce boundary artifacts: a mode transition at the boundary of a 254-byte chunk is an internal encoding detail that should not affect the decoded bit stream, but implementations vary. Using byte mode exclusively eliminates this class of ambiguity.

### N2 — PNG lossless compression only

PNG uses DEFLATE, which is lossless by specification. No information is discarded during compression or decompression. The pixel grid decoded from a PNG must be bit-for-bit identical to the pixel grid that was encoded into it.

Forbidden formats: JPEG (lossy by default), WebP lossy, AVIF lossy, any format with lossy transform options. These are forbidden not because they cannot sometimes be used losslessly, but because the risk of lossy encoding in an automated pipeline is not acceptable for canonical artifacts.

PNG filter selection (None, Sub, Up, Average, Paeth) does not affect the decoded pixel values. Any filter type is acceptable. Filter type 0 (None) is preferred because it maximizes reproducibility across different encoder implementations.

### N3 — Pixel-exact module rendering

Each Aztec module (one cell of the symbol grid) must map to exactly N×N pixels, where N is a positive integer (the module size). The module-to-pixel mapping must be exact:

```
module value 0 (dark)  → RGB(0, 0, 0)      or equivalent in other color modes
module value 1 (light) → RGB(255, 255, 255) or equivalent
```

No anti-aliasing. No sub-pixel rendering. No interpolation. No color depth reduction. The reason is that any pixel that is not exactly black or white requires a threshold decision during decoding, and different decoders may make different decisions at the same threshold value.

### N4 — Reed-Solomon verification before acceptance

Aztec ECC must verify successfully before any decoded bytes are passed to the kernel. A symbol that fails ECC is not a degraded artifact — it is not an artifact at all. Partial decoding of a symbol with failed ECC is forbidden. The entire symbol is rejected and recorded as a fault in the trace.

### The round-trip invariant

All four invariants together guarantee:

```
bits → encode → symbol → render → PNG → decode PNG → decode Aztec → bits
                                         (identical)              (identical)
```

Any break in this chain means the artifact is not canonical.

---

## 4. Separation of Context from Payload

A common encoding mistake is to intermix context with payload: to rely on the position of a byte within a stream to determine its meaning. This creates implicit context, which is fragile and non-replayable.

The Atomic Kernel separates three things that must never be conflated:

```
context    = how to interpret the following bytes (channel, lane, NUMSYS)
structure  = where scope boundaries fall (FS/GS/RS/US control words)
payload    = the content bytes being carried
```

Context and structure are explicit in the bit stream. They are encoded as control words (FLAG=1 bytes, as specified in `CONTROL_PLANE_SPEC.md`). A decoder reading a byte stream can always determine its current context by reading the control words encountered so far — it does not need to know the byte position, the stream length, or any external state.

This separation has a direct consequence for Aztec encoding: the payload bytes passed to the Aztec encoder already contain embedded context in the form of control words. The Aztec encoder treats all bytes identically (byte mode, no transformation). The Aztec decoder produces the same bytes. The kernel parser then interprets the control words to reconstruct context.

The Aztec symbol is **context-neutral**. Context lives in the bit stream, not in the encoding format.

---

## 5. The Geometric Structure of the 4-Channel × 16-Lane Runtime

The 4-channel × 16-lane dimensions are not arbitrary choices. They follow from two algebraic structures: the Klein four-group and the vector space GF(2)^4.

### 5.1 Four channels and the Klein four-group

The Klein four-group V₄ (also called the Vierergruppe) is the group:

```
V₄ = {e, a, b, ab}

where:  a² = e
        b² = e
        (ab)² = e
        ab = ba
```

Every non-identity element is self-inverse. The group has order 4. It is the smallest non-cyclic group.

The four channels map to V₄ exactly:

```
FS = e    identity (outermost scope, the "nothing applied" case)
GS = a    one flip
RS = b    another flip
US = ab   both flips
```

The consequence: the channel structure is not a linear sequence (1→2→3→4) but a group (each element is its own inverse, pairwise products give the fourth element). This is why a FS boundary closes all GS/RS/US scopes — FS is the identity element, and applying the identity cancels all group elements.

The kernel constant C = 0x1D (GS byte repeated to fill bit width n) occupies the `a` position in this group — one generator. This is not coincidental. The constant that prevents the zero fixed point in the transition law is drawn from the same algebraic structure that defines the channel hierarchy.

### 5.2 Sixteen lanes and GF(2)^4

16 = 2^4. The 16 lanes are the elements of the vector space GF(2)^4: all 4-bit binary vectors.

```
0000 = lane 0   (null lane — the zero vector)
0001 = lane 1
0010 = lane 2
...
1111 = lane 15
```

The 15 non-zero vectors form the points of PG(3,2), the projective 3-space over GF(2). PG(3,2) has exactly 15 points, 15 lines, and 15 planes, with 3 points per line, 3 lines through every point, and 7 points per plane.

The null lane (0000) occupies a special role: it is the zero vector, outside the projective space. In the runtime, lane 0 is the identity/default lane — the lane that is active when no explicit lane addressing has been performed.

### 5.3 The 60-state structure

The product of the four channels with the 15 non-null lanes gives 4 × 15 = **60** canonical (channel, non-null-lane) pairs. This is the number of states in the runtime that carry distinct structural meaning. The 60 null-lane states (channel × lane 0) represent channel-only boundaries without lane specificity.

This number 60 appears in several deep symmetry groups: the alternating group A₅ (even permutations of 5 elements), PSL(2,5) (projective special linear group), and the icosahedral symmetry group — all of order 60. The coincidence reflects that the 4 × 15 = 60 structure has rich symmetry.

### 5.4 Reference symbol capacity confirmation

The 4-layer Aztec symbol (27×27 modules) carries 60 data bytes at 40% error correction. This is exactly the number of (channel, non-null-lane) pairs. One byte per canonical runtime state. The data capacity of the reference symbol is determined by the runtime's algebraic structure.

---

## 6. Channel-Ring and Lane-Quadrant Mapping in the Aztec Grid

The Aztec symbol's concentric ring structure maps directly to the channel hierarchy.

### 6.1 Channel-to-ring mapping

Aztec data rings are numbered from the inside out, adjacent to the bull's-eye. The channel-to-ring mapping mirrors the containment hierarchy: inner rings correspond to inner scopes.

```
Ring 2 (innermost data ring)  →  US  (Unit, innermost scope)
Ring 3                         →  RS  (Record)
Ring 4                         →  GS  (Group)
Ring 5 (outermost data ring)   →  FS  (File, outermost scope)
```

Just as FS contains GS contains RS contains US in the scope hierarchy, ring 5 surrounds ring 4 surrounds ring 3 surrounds ring 2 in the symbol geometry.

### 6.2 Lane-to-quadrant mapping

Each ring is read clockwise starting from the top-right corner. The 16 lanes divide into four groups of four, one group per quadrant:

```
Quadrant 0 (top-right)     →  lane group 0  (lanes 0–3)
Quadrant 1 (bottom-right)  →  lane group 1  (lanes 4–7)
Quadrant 2 (bottom-left)   →  lane group 2  (lanes 8–11)
Quadrant 3 (top-left)      →  lane group 3  (lanes 12–15)
```

Lane position within a quadrant (0–3) corresponds to the module position along the quadrant arc.

This layout gives every (channel, lane) pair a unique geometric address in the symbol. A decoder who knows which ring and which quadrant position a module occupies knows exactly which (channel, lane) state it encodes — no additional table lookup required.

---

## 7. Joining Symbols as Semantic Graphs, Not Data Concatenation

This is the central architectural distinction of the Aztec artifact system.

### 7.1 What data concatenation does (and why it is wrong here)

Data concatenation produces a flat byte sequence:

```
[bytes_A] ++ [bytes_B] = [bytes_A  bytes_B]
```

This is ambiguous: it does not encode the relationship between A and B. A decoder cannot determine from the concatenated stream whether B follows A as a sibling, as a child, as a continuation, or as an unrelated sequence. The relationship must be inferred from external metadata or from implicit positional convention — both of which break determinism.

### 7.2 What structural joining does

Structural joining encodes the relationship as a typed edge in a graph:

```
A  --[edge_type]-->  B
```

Where `edge_type` is one of the four structural boundaries:

```
FS edge:  B is a file-level sibling of A (peer at the outermost scope)
GS edge:  B is a group-level child of A
RS edge:  B is a record within A's current group
US edge:  B is an atomic unit within A's current record
```

The edge type is not metadata. It is encoded directly in the bit stream as a control word at the point where A's content ends and B's content begins. This control word is part of the canonical bit sequence, which means it is part of the artifact itself.

### 7.3 The semantic graph

An artifact composed of multiple symbols is a **directed labeled graph**:

```
Nodes:  Aztec symbols (each a canonical bit surface)
Edges:  structural relations (FS/GS/RS/US typed boundaries)
Labels: active context at each edge (channel, lane, NUMSYS)
```

The graph is not a tree (multiple parents are possible via different edge types) but it is **acyclic** — a directed acyclic graph (DAG). An artifact cannot contain itself.

### 7.4 Graph reconstruction is deterministic

Given the graph, reconstruction follows the structural hierarchy:

1. Locate the root node(s): symbols that have no incoming FS edges.
2. Decode the root symbol's bit stream. Follow control words.
3. When a control word signals a boundary, follow the corresponding edge to the next node.
4. Decode that node's bit stream within the context established by the edge.
5. Continue until all nodes are decoded and all edges are traversed.

Because all context is explicit, there is exactly one valid reconstruction. No ambiguity, no contextual inference, no implicit conventions.

### 7.5 Physical embodiment

The graph structure allows artifacts to exist in physical space without losing their semantic structure. A set of Aztec symbols printed on paper, arranged spatially, carries its graph edges in the bit streams of the symbols themselves — not in their physical proximity. Rearranging the printed symbols does not change what they mean. Proximity implies nothing. Only explicit structural edges define relationships.

This is why the rule is stated as: **structure must determine order, not physical proximity**.

---

## 8. Content Addressing and Artifact Identity

The identity of an artifact is the hash of its canonical bit sequence:

```
artifact_id = H(canonical_bits)
```

This hash is stable across:
- Different PNG compression levels
- Different module sizes (as long as pixel-exact encoding is used)
- Different physical media (screen, paper, network)
- Different storage locations
- Different file names

Because the authoritative object is the bit sequence, not the container.

For a multi-symbol artifact (a semantic graph), the identity is the hash of the **serialized graph**: the canonical bit sequences of all nodes concatenated in a deterministic order (depth-first traversal of the DAG, with edges visited in the order FS < GS < RS < US for same-type edges at the same node).

---

## 9. Integrity Verification Layers

Integrity is verified in four layers from outermost to innermost:

```
Layer 1: PNG integrity
  PNG checksum (CRC32 per chunk) verifies the file is not corrupted in transit.
  Failure → reject the file before decoding.

Layer 2: Aztec ECC integrity
  Reed-Solomon error correction verifies the symbol can be decoded.
  Failure → reject the symbol. Do not attempt partial decode.

Layer 3: Canonical bit integrity
  Hash of decoded bytes matches the expected artifact_id.
  Failure → the bytes are not the canonical bits of this artifact.

Layer 4: Structural integrity
  Control words in the bit stream form a valid hierarchy.
  All PUSH operations are matched by POP.
  No reserved values appear.
  Failure → the artifact structure is malformed. Reject and trace.
```

All four layers must pass. Passing layers 1 and 2 but failing layer 3 means the PNG and Aztec are technically valid but the content has been substituted. This is a tamper signal, not a corruption signal.

---

## 10. Formal Statement of the Artifact Laws

Five laws govern the Aztec artifact system:

**Law 1 — Canonical primacy.** The canonical bit sequence is the artifact. The Aztec symbol and the PNG are projections. No projection has authority over the bit sequence.

**Law 2 — No-loss projection.** The projection chain `bits → Aztec → PNG` is lossless and reversible. Any break in reversibility invalidates the artifact.

**Law 3 — Context separation.** Context is explicit in the bit stream via control words. No implicit context from byte position, physical arrangement, or external metadata.

**Law 4 — Structural joining.** Multiple symbols are joined by structural edges (FS/GS/RS/US typed boundaries encoded in the bit streams). Data concatenation is not a valid join.

**Law 5 — Deterministic reconstruction.** Given a semantic graph and its edge types, there is exactly one valid reconstruction of the artifact. Any ambiguity in reconstruction is a structural error, not an interpretation choice.

---

## 11. Layer Position in the Atomic Kernel Stack

```
Layer 0  Kernel law          delta(n, x) — Coq-certified
Layer 1  Crystal             tick(state, t) — B injection
Layer 2  Identity            SID, OID, CLOCK — crystal-chained
Layer 3  COBS framing        packet delimiters
Layer 4  Control plane       4-channel × 16-lane, NUMSYS masking
Layer 5  Observer / World    observe(seed, n), frame(n)
Layer 6  Projection          color, symbol, position — advisory
         ↑
Layer 7  Artifact encoding   Aztec → PNG (this specification)
         Semantic graph      multi-symbol DAG joining
```

Layer 7 sits above the projection layer. It is how kernel world-states are committed to canonical artifact form for storage, transmission, or physical embodiment. Layer 7 cannot alter Layers 0–4; it can only read them and project them.

---

## Summary

Three structures, each a projection of the one below:

**Canonical bits** → defined by the kernel law. Authoritative. Immutable. Content-addressed.

**Aztec symbol** → a lossless visual encoding of the canonical bits. No-loss by four invariants. Grid geometry mirrors the channel-ring and lane-quadrant structure of the 4×16 runtime.

**PNG image** → a lossless pixel rendering of the Aztec symbol. Any valid lossless PNG encoding of the same symbol is the same artifact.

And one rule that distinguishes this system from data storage:

**Symbols are joined as semantic graphs (typed structural edges), not as byte stream concatenations.** The graph encodes relationships. The nodes carry bits. The edge types are the only valid basis for reconstruction order.
