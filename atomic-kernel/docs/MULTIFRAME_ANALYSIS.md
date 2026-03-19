# Multi-Frame Systems and the Canonical Foundation
## How SLIP, PLIP, PPP, and Multilink PPP Lead to the Atomic Kernel Artifact Model

**Author:** Brian Thorne et al.  
**Project:** Atomic Kernel  
**Status:** Technical Analysis / Architecture Rationale  
**Date:** 2026

---

## Abstract

A single frame must answer one question: where does this unit begin and end? A multi-frame system must answer four harder questions: where does each frame begin and end, which frames belong together, in what relation do they stand, and how do we reconstruct the same canonical object from them every time?

This document traces the progression from SLIP's minimal boundary marking through PLIP's physical staging, PPP's typed transport, and Multilink PPP's forced reconstruction law — to the Atomic Kernel's artifact model, which replaces linear sequence with typed structural edges in a directed acyclic graph. Each step in the progression is a quotient: removing structure that turned out to be incidental, retaining only what is required for identical canonical unfold.

The argument concludes with the irreducible core: the five laws that cannot be quotiented away without losing canonical reconstruction.

---

## 1. The Quotient Question

Before examining any specific protocol, the right question to ask is:

> What structure can be removed while the same canonical unfold, replay, and projection still results?

This is a quotient question. Not "what features does this system have?" but "what is the smallest set of laws whose outputs are identical?"

The answer defines the true foundation. Everything else is derivable consequence or incidental convention.

The Atomic Kernel has already answered this question for its computation layer. There was one design decision:

```
delta(n, x) = mask(n,  rotl(x, 1)
                   XOR rotl(x, 3)
                   XOR rotr(x, 2)
                   XOR C)
```

Four choices inside that: rotations not shifts (no bits fall off the edge), XOR (reversible, symmetric), a constant C (breaks the zero fixed point), mask to width (keeps state bounded). That is the entire design of the transition law.

Everything else was computed:

| Value | Source |
|-------|--------|
| Period = 8 | Property of the delta law on 16-bit space |
| Prime 73 | Smallest prime whose decimal repeats with period 8 |
| Block B = [0,1,3,6,9,8,6,3] | Digits of 1/73 |
| W = 36 | sum(B) |
| Orbit/offset recovery | divmod(position, 36) |

Nobody chose 73. The law has period 8. The smallest prime with decimal period 8 is 73. The system found it.

The same question applies to the transport layer. Multi-frame systems are where that question gets forced into the open.

---

## 2. Why a Single Frame Hides the Problem

In a single-frame system, hidden assumptions survive unnoticed because nothing challenges them. The frame arrives in order, in one stream, from one source, in one piece. Any implicit convention — "bytes mean what they mean because of their position," "context is inferred from sequence," "proximity implies relation" — goes untested.

The moment you introduce multiple frames, every hidden assumption breaks.

- If meaning depends on position in a single stream, what happens when fragments arrive out of order across multiple streams?
- If context is inferred from sequence, what happens when fragments are delayed, dropped, or reordered?
- If reconstruction means "put bytes in order," what happens when two fragments have equal precedence?
- If relation is implied by proximity, what happens when physically adjacent symbols have no structural relationship?

Multi-frame systems force you to make the implicit explicit. They are the proof by stress test of whether a canonical foundation actually exists.

---

## 3. SLIP — The Minimal Quotient

**RFC 1055. Serial Line Internet Protocol.**

SLIP solves exactly one problem: how to mark the boundary between packets in a byte stream.

The mechanism is direct. Reserve one byte value as the frame delimiter (END = 0xC0). If that value appears in the payload, replace it with a two-byte escape sequence (ESC 0xDB followed by ESC_END 0xDC). If the escape byte itself appears in the payload, replace it with another escape sequence (ESC 0xDB followed by ESC_ESC 0xDD).

```
Reserved values: 2  (END = 0xC0, ESC = 0xDB)
Escape sequences: 2  (ESC ESC_END, ESC ESC_ESC)
```

Example: encoding the payload `[0x11, 0x22, 0x00, 0x33, 0xDB, 0x44]`:

```
SLIP:  0x11 0x22 0x00 0x33 0xDB 0xDD 0x44 0xC0   (8 bytes)
```

Note that 0x00 passes through unchanged — SLIP does not reserve zero. Only 0xC0 and 0xDB are structural. The 0xDB in the payload becomes the two-byte sequence 0xDB 0xDD.

**What SLIP provides:** boundary law only.

**What SLIP does not provide:** integrity (no checksum), type (no protocol field), sequence (no numbering), graph relation (no structure beyond start/end), canonical reconstruction (no law beyond "put bytes in this order").

**What SLIP's minimalism reveals:** everything except the boundary law can be quotiented away and the system still frames. SLIP is the lower bound — the least structure that a framing protocol can have while remaining functional.

SLIP is not a weakness. It is the clearest possible statement of what framing actually requires: one structural value, one escaping rule. Everything else is added by layers above.

---

## 4. COBS — The More Minimal Quotient of SLIP

COBS (Consistent Overhead Byte Stuffing) solves the same problem as SLIP but with fewer reserved values. Where SLIP reserves two byte values and requires escape sequences, COBS reserves exactly one (0x00) and eliminates escape sequences entirely.

The mechanism: break the payload into blocks of at most 254 non-zero bytes. Prepend each block with a single overhead byte whose value is the number of bytes in the block plus one. This overhead byte is the distance to the next zero in the stream. The zeros in the original data are absorbed by these overhead bytes — they are never written to the output. Append 0x00 as the unambiguous packet delimiter.

```
Reserved values: 1  (NULL = 0x00)
Escape sequences: 0
```

Same payload: `[0x11, 0x22, 0x00, 0x33, 0xDB, 0x44]`:

```
COBS:  0x03 0x11 0x22 0x04 0x33 0xDB 0x44 0x00   (8 bytes)
```

The 0x00 in the payload becomes the value 0x03 (the overhead byte for the first block: 2 non-zero bytes + 1 = 3). The 0xDB passes through unchanged — COBS does not reserve it. Every 0x00 in the stream is a packet boundary. No scanning required.

COBS is the more minimal quotient of SLIP's boundary problem:

| | SLIP | COBS |
|---|---|---|
| Reserved values | 2 | 1 |
| Escape sequences | 2 | 0 |
| Overhead | +1–2 bytes | +2 bytes (always) |
| Overhead variability | Yes (zeros cost extra) | No (constant regardless of content) |
| Recovery from corruption | Find next END | Find next 0x00 |

The "consistent overhead" in COBS's name is the key property: a payload with 100 zeros and a payload with zero zeros both cost exactly 2 bytes overhead. Content does not affect framing cost. This is what allows COBS to fit cleanly into the Atomic Kernel's transport layer: the overhead is bounded and predictable regardless of what the payload contains.

**The central inversion:** COBS inverts the relationship between the reserved value and the payload. Before COBS, 0x00 was ordinary data and boundaries needed special treatment. After COBS, 0x00 is the only structural byte and everything from 0x01 to 0xFF is pure content. The forbidden value becomes the only structural value. This is the same inversion principle that appears in the delta law's constant, in the FLAG bit of the control plane, and in the FS/GS/RS/US separator assignment to the top of the C0 space.

---

## 5. PLIP — Transport Below the Semantic Unit

**Parallel Line Internet Protocol.**

PLIP reveals a different aspect of the quotient problem: **physical transfer can be subdivided below the semantic payload without changing the payload's meaning.**

PLIP transmits data over a parallel port by splitting each byte into two nibbles of four bits each. The nibble is the transport handshake unit. It is not the semantic unit. The byte is reassembled from the two nibbles before any higher layer sees it. The split is invisible to the protocol above.

This is directly analogous to the Aztec artifact model. Two Aztec symbol nodes in a semantic graph are not two semantic objects. They may together represent one semantic unit, with the graph edge defining their relationship. The physical separation of the symbols into two PNG files on disk, two prints on paper, or two transmissions across a network does not define what they mean. Only the structural edge — the typed FS/GS/RS/US relation — defines the meaning.

PLIP's lesson: **transport subdivision does not define semantic structure.** The semantic unit exists at the level of the reconstruction law, not at the level of the physical carrier.

---

## 6. PPP — Adding Type, Integrity, and Phases

**RFC 1661. Point-to-Point Protocol.**

PPP is "better engineered" than SLIP (RFC 1055's own words) because it adds three things SLIP lacks:

**Protocol typing.** The Protocol field identifies the payload type (0x0021 for IP, 0x003D for Multilink, etc.). A receiver knows what kind of data follows the header without inspecting the payload. Type is explicit, not inferred.

**Integrity.** The Frame Check Sequence (FCS) is a CRC computed over the frame contents. Corruption is detectable. SLIP had no such mechanism.

**Link phases.** PPP defines a state machine: Link Dead → Link Establishment → Authentication → Network-Layer Protocol → Link Termination. The connection has a lifecycle that must be explicitly managed.

PPP frame structure:

```
Flag     0x7E    (1 byte)   frame boundary
Address  0xFF    (1 byte)   broadcast (compressible)
Control  0x03    (1 byte)   unnumbered data (compressible)
Protocol 2 bytes            type identifier
Data     variable           payload
FCS      2 bytes            CRC integrity check
Flag     0x7E    (1 byte)   frame end
```

What PPP adds over SLIP in terms of the quotient analysis:

| Layer | SLIP | PPP |
|-------|------|-----|
| Boundary law | ✓ | ✓ |
| Integrity | ✗ | ✓ (FCS) |
| Type | ✗ | ✓ (Protocol field) |
| Link lifecycle | ✗ | ✓ (phases) |
| Sequence | ✗ | ✗ |
| Graph relation | ✗ | ✗ |

**What PPP still quotiented away:** the physical carrier (PPP runs over serial, ISDN, SONET, ATM, Ethernet — it does not care), the UART configuration (it negotiates these), and detailed modem behavior. PPP separated the protocol from its physical substrate.

**What PPP did not quotient away:** the assumption of a single ordered byte stream. PPP still thinks in frames in sequence on one link. This assumption only breaks when you add multiple links.

---

## 7. Multilink PPP — When Sequence Alone Fails

**RFC 1990. Multilink PPP.**

Multilink PPP is the protocol that proves why multi-frames matter.

The setup: traffic is spread across multiple distinct PPP connections simultaneously. A packet may be fragmented and its fragments sent over different links. The links have independent timing. Fragments arrive at the receiver in arbitrary order.

On a single PPP link, frames cannot arrive out of order. The ordering of the underlying byte stream is total. Reconstruction is trivial: read the frames in the order they arrive.

On multiple PPP links, this assumption fails completely. Fragment A may travel over link 1 and arrive before fragment B, which traveled over link 2, even if B was sent first. The receiver cannot reconstruct the original packet without knowing the correct order of the fragments.

Multilink PPP's solution: fragment numbering. Each fragment carries a sequence number in a mandatory header:

```
[B|E|sequence(22 bits)]   or   [B|E|F|C|sequence(12 bits)]

B = Begin fragment (this is the first fragment of the packet)
E = End fragment (this is the last fragment)
sequence = monotonic counter shared across all links
```

The sequence number is the explicit reconstruction law. Without it, the receiver cannot determine order. With it, all fragments can be reassembled correctly regardless of arrival order.

**The lesson Multilink PPP teaches:** once distribution exists, reconstruction law becomes part of the protocol. It cannot be implied by physical ordering. It must be stated explicitly in the bit stream.

This is the direct ancestor of the Atomic Kernel's typed structural edges. Multilink PPP needed a number to say "this fragment is fragment 47 of this packet." The Atomic Kernel's artifact model uses typed edges to say "this symbol is a GS-level child of that symbol." Both are explicit reconstruction laws. The difference is that a sequence number encodes only position in a linear order, while a typed edge encodes a structural relation in a graph.

PPP asked: what order do I reassemble these bytes in?  
The Atomic Kernel asks: what structure do these canonical surfaces inhabit such that the same unfold results?

That is a stronger and more general question.

---

## 8. The Quotient Progression

Reading the progression as a sequence of successive quotients:

```
SLIP
  Retained: boundary law only
  Quotiented away: everything except END/ESC

PPP
  Retained: boundary + integrity + type + link lifecycle
  Quotiented away: physical carrier, UART, modem specifics

Multilink PPP
  Retained: boundary + integrity + type + fragment identity + sequence + reassembly
  Quotiented away: single-stream assumption

Atomic Kernel Artifact
  Retained: boundary + integrity + type + graph relation + canonical bits + content addressing
  Quotiented away: linear sequence as primitive, physical proximity, byte order as reconstruction law
```

Each step removes something that turned out not to be fundamental while keeping what reconstruction actually requires. Multilink PPP had to make fragment sequence explicit because distribution broke the implicit ordering assumption. The Atomic Kernel goes further: even explicit linear sequence is quotiented away, replaced by typed structural edges that can express non-linear relationships.

---

## 9. Why Each Design Choice in the Delta Law Is Also a Transport Principle

The delta law's four internal choices each have exact analogs in the transport analysis above.

### Rotations, not shifts

```python
rotl(x, 1) XOR rotl(x, 3) XOR rotr(x, 2)
```

Rotations preserve all bits. A left shift by 1 destroys the most significant bit — it falls off the edge and is gone. A rotation by 1 moves that bit to the least significant position instead. No information is lost.

This is the same reason the artifact spec requires no-loss encoding at every layer:

- No JPEG (lossy compression destroys pixel values)
- No anti-aliasing (sub-pixel rendering loses module boundaries)
- No mode-switching in Aztec (boundary artifacts can destroy bit values)
- No partial decode after ECC failure (corrupted bits propagate as false data)

In every case: lost bits mean lost canonical recoverability. The rotation choice in the delta law and the no-loss encoding requirements in the artifact layer are the same design principle applied at different scales.

### XOR

XOR is reversible. Given `A XOR B = C`, you can recover `A` from `C XOR B` or `B` from `C XOR A`. No information is destroyed. The operation is also symmetric and associative — order does not matter in a chain of XORs.

This mirrors the control plane's context-change mechanism: the NUMSYS mask transforms how data bytes are interpreted, but the bytes themselves are unchanged. The transformation is lawful, not destructive. Context changes interpretation; it does not rewrite content.

### The constant C

Without the constant C = 0x1D...1D, `delta(n, 0) = 0`. Zero is a fixed point of the pure rotation-XOR law. The system would freeze if it ever reached the zero state. C breaks this symmetry by ensuring no state maps to itself.

Every framing protocol needs an analogous asymmetry:

- SLIP needs END (0xC0) to mark boundaries
- PPP needs Flag (0x7E)
- COBS needs NULL (0x00)
- The control plane needs the FLAG bit (bit 7 = 1)
- The Aztec spec needs the bull's-eye finder pattern

Without an asymmetric marker, boundaries and content become indistinguishable. The constant in the delta law and the delimiter in every framing protocol serve the same function: introducing the one special value that makes structure visible.

Note also: C = 0x1D is the GS byte — the Group Separator at U+001D, the same codepoint that defines Channel 1 in the control plane. The transport and computation layers share the same primitive marker.

### Mask to width

```python
mask(n, x) = x & ((1 << n) - 1)
```

The mask keeps the state bounded to n bits. Without it, the state space is infinite and the system cannot be replayed — an n-bit state from step k might have grown beyond n bits by step k+1.

This is the analog of bounded frame size in transport protocols. PPP negotiates a Maximum Transmission Unit. Aztec symbols have fixed capacity per layer count. The control plane defines 16 lanes (4 bits) and 4 channels (2 bits) — both fixed, finite, enumerable. Boundedness is what makes auditing, replay, and content-addressing possible. An unbounded system cannot be content-addressed because its state space has no finite description.

---

## 10. The Five Laws That Cannot Be Quotiented Away

Multi-frame systems expose hidden assumptions by breaking them. The assumptions that survive exposure — that remain necessary regardless of how the system is distributed, reordered, or physically embodied — form the irreducible core.

There are five:

### 1. A bounded state law

Something must define what constitutes one valid state transition, and that definition must be finite and deterministic. In the Atomic Kernel this is `delta(n, x)` — proven in Coq, verified against golden parity vectors at all five bit widths. The state space is bounded to n bits. The transition is deterministic.

Without a bounded state law there is no replay. Without replay there is no canonical reconstruction.

### 2. A reversible projection

No layer in the chain from canonical bits to physical representation may destroy information. Each projection must be recoverable:

```
canonical_bits → Aztec symbol → PNG → Aztec symbol → canonical_bits
              ↑                                     ↑
         identical                             identical
```

This is the no-loss requirement. It applies equally to the delta law (rotations not shifts), to the Aztec encoding (byte mode only), to the PNG format (lossless DEFLATE), and to the module rendering (pixel-exact, no anti-aliasing).

A single lossy step anywhere in the chain breaks canonical reconstruction. The chain is as strong as its weakest link.

### 3. An explicit boundary law

Something must unambiguously mark where one unit ends and another begins. This cannot be implied by position, proximity, or convention. It must be present in the bit stream itself.

SLIP uses END (0xC0). PPP uses Flag (0x7E). COBS uses NULL (0x00). The control plane uses FLAG bit = 1. Every protocol that has survived production use has an explicit boundary law. The ones that relied on implicit position (fixed-length records, position-dependent parsing) failed when data was corrupted, reformatted, or transmitted over a different medium.

The atomic kernel's boundary law is the FS/GS/RS/US typed boundary, encoded as a control word in the bit stream. It is never implicit.

### 4. An explicit relation law

This is what Multilink PPP discovered and what the Atomic Kernel's artifact model extends. Once you have more than one unit, you need a law that says how units join. A sequence number (Multilink PPP) is a minimal relation law: it says "unit 47 comes after unit 46." A typed structural edge (Atomic Kernel) is a richer relation law: it says "symbol B is a GS-level child of symbol A."

Without an explicit relation law, multi-unit reconstruction degrades to guessing. Even with explicit boundary marking, a receiver cannot know whether two correctly-bounded units are siblings, parent-child, sequential fragments of one object, or entirely unrelated, unless the relation is stated.

The relation law cannot be physical proximity. Physical proximity fails the moment symbols are rearranged, transmitted separately, or printed and scanned. The rule is: **structure must determine order, not physical proximity.**

### 5. Canonical reconstruction

Given the boundary law and the relation law, reconstruction must be deterministic — the same graph, traversed the same way, must always produce the same canonical bit sequence. This requires a fixed traversal order (the spec defines: depth-first, with edges visited in the order FS < GS < RS < US at each node), content addressing (the artifact ID is the hash of the canonical bits, not of any container), and explicit context (no implicit decoder state that varies between implementations).

Canonical reconstruction is what distinguishes an artifact from a file. A file can be reconstructed differently by different readers depending on their state, their assumptions, or their version. An artifact has one canonical form, derivable by any compliant implementation, in any order, on any machine.

---

## 11. What Multi-Frames Prove

Here is the cleanest statement of why multi-frame systems matter as a conceptual tool:

**Multi-frames make false foundations fail immediately.**

A single-frame system can rely on proximity, on stream order, on implicit context, on a fixed reader implementation — and work fine, because none of these assumptions are ever stressed. The moment you distribute frames across multiple links, reorder fragments, transmit them over different media, or physically separate the symbols, every false foundation breaks.

The five failure modes, one per hidden assumption:

| Hidden assumption | What multi-frames do to it |
|---|---|
| Proximity implies relation | Moving symbols breaks meaning |
| Sequence number is sufficient | Branching structures cannot be represented |
| External metadata carries context | Replay ceases to be self-contained |
| Lossy encoding is acceptable | Reassembly produces different bits each time |
| Implicit context from position | Different decoders reconstruct differently |

The progression from SLIP to PPP to Multilink PPP to the Atomic Kernel artifact model is the progression of discovering and eliminating these hidden assumptions, one by one, under the pressure of distribution.

---

## 12. Where 73 and the Artifact Geometry Fit

The same quotient logic applies to all the derived quantities in the system. None of them are primitives.

73 is not a foundational choice. The delta law has period 8. The smallest prime whose decimal expansion repeats with period 8 is 73. The block B = [0,1,3,6,9,8,6,3] is the digits of 1/73. W = 36 is sum(B). Orbit/offset recovery is divmod(position, W). These are computed consequences of the single design decision: the delta law.

The 60 canonical (channel, lane) states are not a foundational choice. They are the product of 4 channels (the Klein four-group V₄, forced by the 2-bit channel field) and 15 non-null lanes (the non-zero vectors of GF(2)^4, forced by the 4-bit lane field). 4 × 15 = 60.

The 27×27 Aztec coordinate table is not a foundational choice. It is a deterministic projection of the 60 states onto the ring-and-quadrant geometry of a 4-layer Aztec symbol. The coordinates are computed from the channel-to-ring and lane-to-quadrant mapping rules; they are not invented.

All of these belong to the same category: derived regularities. They are downstream structure generated by the foundational laws. They can be computed from the laws and verified against the computation. They are not part of the foundation.

The clean three-way split, which applies equally to the computation layer and the transport layer:

**Foundational laws** — what must exist for identical outputs: the delta law, the no-loss requirement, the explicit boundary law, the explicit relation law, canonical reconstruction.

**Derived regularities** — what the laws generate: period 8, prime 73, block B, W = 36, 60 states, Aztec ring positions, quadrant distributions.

**Advisory projections** — what can vary without changing identity: PNG byte layout, DEFLATE compression level, physical orientation of a printed symbol, transport carrier, file naming, storage location.

---

## 13. The Reduction Statement

The foundation is not the full visible symbol set, nor the incidental transport framing, nor the physical arrangement of artifact surfaces.

The foundation is the smallest lawful system whose bounded reversible state evolution, explicit boundary markers, and deterministic structural join relation yield the same canonical unfold, replay, and projection.

Everything else is consequence.

---

## 14. The Stack as Successive Quotients

The complete Atomic Kernel stack, read as a sequence of successive quotients from physical substrate to canonical artifact:

```
Physical carrier
  (quotiented away: specific medium, timing, encoding)
       ↓
COBS framing
  Retained: unambiguous boundary law, self-synchronization
  (quotiented away: escape complexity, multiple reserved values)
       ↓
Control plane (4-channel × 16-lane)
  Retained: type, context, scope, in-band signaling
  (quotiented away: external metadata, implicit context)
       ↓
Crystal / Identity layer
  Retained: deterministic state evolution, content-addressed identity
  (quotiented away: external clocks, trust authorities, hardware dependency)
       ↓
Artifact projection (Aztec → PNG)
  Retained: lossless representation, orientation invariance, physical embodiment
  (quotiented away: specific image format, compression details, medium)
       ↓
Semantic graph
  Retained: typed structural edges, deterministic reconstruction, content addressing
  (quotiented away: physical proximity, linear sequence as primitive, external order)
       ↓
Canonical bits
  The irreducible foundation.
  Everything above this line is a projection of this.
```

The canonical bits are not stored. They are computed by the delta law, verified by the Coq proof, content-addressed by the hash, and projected through the artifact stack. Any projection — any PNG, any Aztec symbol, any physical print — can be used to recover them. The projection is not the truth. The bits are the truth.

That is the reduction.
