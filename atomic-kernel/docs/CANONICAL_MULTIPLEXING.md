# Canonical Multiplexing via Infinitely Nestable Escape Streams
## In-Band Signaling, the Hayes-to-Kernel Genealogy, and Canonicalized Access

**Author:** Brian Thorne et al.  
**Project:** Atomic Kernel  
**Status:** Architecture — Transport Layer Signaling Model  
**Depends on:** `CONTROL_PLANE_SPEC.md`, `MULTIFRAME_ANALYSIS.md`  
**Date:** 2026

---

## Abstract

Every in-band signaling system faces the same foundational problem: one byte stream must carry both control and data without ambiguity. The historical progression from Hayes modem command/data modes, through SLIP's two-value escape system, to COBS's single-value elimination, reveals a convergent trajectory — toward fewer reserved values, simpler escaping, and more explicit structure.

This document describes what the Atomic Kernel provides: a canonicalized multiplexing architecture that uses a single reserved bit (FLAG) to partition the byte space into three non-overlapping ranges, then structures the control range as a finite hierarchical vocabulary with one explicit extension gateway (EXTD) that is infinitely nestable without ambiguity. The result is a method for multiplexing any number of simultaneously active interpretation contexts in a single byte stream, with no escape sequences, no timing dependencies, no external metadata, and no fixed depth.

---

## 1. The Core Tension in Every In-Band System

All communication has two categories of information: control (instructions about how to interpret what follows) and data (the content being communicated). When both travel on the same channel, the receiver must be able to tell them apart at every byte.

This is the in-band signaling problem. It has been solved and re-solved across sixty years of computing, always by some variant of the same mechanism: **reserve one or more byte values as control markers, then provide a rule for what to do when those values appear in legitimate data.**

The tension is permanent. You cannot eliminate it. You can only manage it more or less elegantly. The history of signaling protocols is the history of progressively more elegant management.

---

## 2. The Hayes Modem — Mode Switching as Signaling

The Hayes command set introduced the simplest possible form of in-band signaling: the modem operates in one of two modes, and mode transitions are the signaling mechanism.

**Command mode:** bytes from the computer are AT commands. `ATDT5551212` dials a number. The modem interprets every byte as command text.

**Data mode:** bytes from the computer are payload, transmitted to the remote party. The modem passes every byte through.

The same physical wire. The same byte values. What changes is the mode, and therefore the interpretation.

Switching from data mode back to command mode requires the **`+++` escape sequence**: a one-second pause, the three characters `+++`, another one-second pause. The timing gap is what makes it unambiguous — no data transmission can accidentally contain a 1-second silence followed by exactly `+++` followed by another 1-second silence.

This is timing-gated signaling. It is fragile in proportion to its simplicity. The Hayes command set explicitly acknowledges this: the `+++` escape may be disabled to prevent accidental triggering by legitimate data. Disabling the escape means you can no longer switch modes in-band at all.

The **DLE (Data Link Escape, 0x10)** mechanism was added for fax and voice modes to handle events that must be communicated regardless of current mode — a caller pressing a touch-tone key, the modem detecting a dropped connection. DLE is a prefix byte: when the modem sends DLE (0x10) followed by another byte, that two-byte sequence has special meaning. When the modem needs to send a literal 0x10 value as data, it doubles it: 0x10 0x10 = one literal 0x10.

DLE is depth-1 escaping. The prefix byte escapes into a one-level-deep interpretation layer. There is no depth-2 DLE escape. A DLE followed by another DLE followed by a third byte is not a nested escape — it is two literal 0x10 bytes followed by an ordinary byte.

The Hayes model teaches the problem perfectly:

```
one channel → two uses (control and data) → ambiguity → escape mechanism
```

---

## 3. SLIP — Two Reserved Values

SLIP (RFC 1055) operates on serial links with no modem command/data distinction. The entire byte stream is data, and the only problem is framing: where does one packet end and the next begin?

SLIP reserves two byte values:

```
END = 0xC0  (frame boundary)
ESC = 0xDB  (escape prefix)
```

When `END` appears in the data, it is replaced by the two-byte sequence `ESC ESC_END` (0xDB 0xDC). When `ESC` appears in the data, it is replaced by `ESC ESC_ESC` (0xDB 0xDD).

Encoding the payload `[0x11, 0x22, 0x00, 0x33, 0xDB, 0x44]`:

```
SLIP:  0x11 0x22 0x00 0x33 0xDB 0xDD 0x44 0xC0
```

Note that 0x00 passes through unchanged — SLIP does not treat zero as special. The 0xDB in the payload becomes 0xDB 0xDD (the ESC ESC_ESC sequence). The 0xC0 terminator marks the end.

**What SLIP requires:** 2 reserved byte values and 2 two-byte escape sequences. Overhead is variable — a payload dense with 0xC0 or 0xDB bytes expands significantly. No depth — SLIP has exactly one escape level.

---

## 4. COBS — One Reserved Value, No Escape Sequences

COBS (Consistent Overhead Byte Stuffing) eliminates the two-value, two-escape-sequence approach of SLIP in favor of a single reserved value with no escape sequences.

The mechanism: reserve only 0x00 as the packet delimiter. Break the payload into blocks of at most 254 non-zero bytes, each preceded by an overhead byte equal to (number of bytes in block + 1). The overhead byte encodes the distance to the next zero in the stream. The zeros in the payload are absorbed by the overhead bytes — they never appear in the output. Append 0x00 as the packet boundary.

Encoding the same payload `[0x11, 0x22, 0x00, 0x33, 0xDB, 0x44]`:

```
COBS:  0x03 0x11 0x22 0x04 0x33 0xDB 0x44 0x00
```

The 0x00 in the payload position is absorbed: the first overhead byte (0x03) says "the next zero is 3 positions ahead," which is exactly where the original zero was. The 0xDB passes through unchanged — COBS has no reason to reserve it.

| | SLIP | COBS |
|---|---|---|
| Reserved byte values | 2 | 1 |
| Escape sequences | 2 | 0 |
| Overhead (no reserved bytes in data) | +1 byte | +2 bytes |
| Overhead (high density of reserved bytes) | variable | constant (+2) |
| Recovery from corruption | find next 0xC0 | find next 0x00 |

COBS is the more minimal quotient: fewer reserved values, no escape sequences, constant overhead regardless of data content. The "consistent overhead" in its name describes this: a 100-byte payload with 100 zeros costs exactly the same as a 100-byte payload with zero zeros.

---

## 5. The Central Inversion

COBS performs a structural inversion that is worth naming explicitly because the Atomic Kernel extends it.

**Before COBS:** 0x00 is ordinary data. Packet boundaries require special non-zero values (SLIP's 0xC0). Data that contains those values must be escaped.

**After COBS:** 0x00 is the only structural byte. Every value from 0x01 to 0xFF is pure data in the payload. No escaping required. Any 0x00 anywhere in the stream is unambiguously a packet boundary.

The forbidden value becomes the only structural value. Everything else becomes content.

This inversion appears three times in the Atomic Kernel's architecture:

- **COBS:** 0x00 becomes the only structural byte
- **FLAG bit:** bit 7 = 1 becomes the only control classification
- **FS/GS/RS/US:** four bytes at the ceiling of C0 space (0x1C–0x1F) become the only structural hierarchy markers

Each is an inversion of the same form: one special value claims structure; everything else is content.

---

## 6. The FLAG Bit — One Bit, Three Ranges

The Atomic Kernel adds one more layer on top of COBS: a single bit (bit 7, the most significant bit of every byte) that partitions the byte space into three non-overlapping, exhaustive ranges.

```
0x00          COBS packet delimiter
0x01–0x7F     Data bytes   (FLAG = 0, content under current NUMSYS)
0x80–0xFF     Control words (FLAG = 1, structured control vocabulary)
```

Every byte in the stream falls into exactly one of these three categories. The classification requires reading one bit. No scanning, no state, no lookahead.

Compare this to DLE:

| | DLE (Hayes) | FLAG bit |
|---|---|---|
| Signal | Prefix byte 0x10 | Bit 7 of the byte itself |
| Ambiguity | 0x10 can appear in data, requires doubling | FLAG=0 bytes are never control |
| Escape cost | 2 bytes per signal (DLE + meaning) | 1 byte per boundary signal |
| Depth | 1 (no nesting) | Structured (see below) |

FLAG solves what DLE could not: the prefix byte itself can be data and requires escaping. A FLAG bit in the byte being classified requires no prefix at all. The classification is in the byte itself, not in the byte before it.

---

## 7. The Control Word Structure

Every byte with FLAG = 1 is a control word with the following field layout:

```
Bit:   7     6  5     4  3  2  1     0
       ┌─────┬─────┬──────────────┬──────┐
       │FLAG │  CH │     LANE     │ TYPE │
       │  1  │ 2b  │     4b       │  1b  │
       └─────┴─────┴──────────────┴──────┘
```

**FLAG (bit 7) = 1:** always, by definition of a control word.  
**CH (bits 6:5):** which of the four structural channels — 00=FS, 01=GS, 10=RS, 11=US.  
**LANE (bits 4:1):** which of the 16 lanes (0–15).  
**TYPE (bit 0):** 0 = structural boundary (1 byte total), 1 = context change (followed by 1 context byte).

A TYPE=0 control word is a complete signal in 1 byte: close or open a scope on this channel/lane.

A TYPE=1 control word is the first of a 2-byte sequence. The second byte is the context payload:

```
Bits 7:4 = NUMSYS    (which numerical system to apply)
Bits 3:0 = SCOPE     (how far the change extends)
```

Both bytes of the context-change sequence are in range [0x80–0xFF] for the control word and [0x00–0xFF] for the context byte — but the context byte after COBS encoding is guaranteed non-zero because it follows immediately after a non-zero control word with no zero bytes intervening.

---

## 8. Canonical Multiplexing

Traditional multiplexing takes N channels and interleaves them on one carrier. A multiplexer at the sender combines them; a demultiplexer at the receiver separates them. The demultiplexer requires a channel table — external metadata that describes which bytes belong to which channel.

The Atomic Kernel does not use external metadata. The stream is self-describing.

The control words specify, inline, which channel and lane each block of data belongs to, and what numerical system should be used to interpret it. The receiver needs only the stream itself to reconstruct the full multiplexed structure.

This is **canonical multiplexing**: a multiplexed stream that is self-describing, deterministic, and content-addressed. Any two streams with the same canonical bits are identical, regardless of when or where they were produced.

A multiplexed stream carrying three simultaneous contexts:

```
Byte(s)        Type    Meaning
────────────────────────────────────────────────────────────
0xA1           CTRL    GS/lane-0 context-change [10100001]
0xB1           CTX     NUMSYS=ATOM, SCOPE=BLOCK  [10110001]
0x5D 0x17      DATA    crystal state 0x5D17 in ATOM format
0x98 0xCC      DATA    crystal state 0x98CC in ATOM format
0xA0           CTRL    GS/lane-0 boundary (close) [10100000]

0xC7           CTRL    RS/lane-3 context-change  [11000111]
0x80           CTX     NUMSYS=UTF8, SCOPE=THIS   [10000000]
0x48 0x65...   DATA    "Hello" in UTF-8
0xC6           CTRL    RS/lane-3 boundary (close) [11000110]

0xEF           CTRL    US/lane-7 context-change  [11101111]
0xD1           CTX     NUMSYS=COBS, SCOPE=BLOCK  [11010001]
0x03 0x42 0x43 0x00    DATA    COBS-nested sub-packet [0x42, 0x43]
0xEE           CTRL    US/lane-7 boundary (close) [11101110]

0x00                   COBS packet delimiter
```

Three simultaneous contexts — ATOM (atomic kernel state hex), UTF8 (Unicode text), COBS (nested packet) — in one byte stream. Every byte is unambiguous. No reserved values except 0x00. No escape sequences. The contexts are independent: the UTF8 block does not know about the ATOM block; the COBS block can contain anything including further structured data.

---

## 9. The Fifteen Numerical Systems

The NUMSYS field (4 bits) defines how data bytes are interpreted in the current scope. Fourteen systems are defined in the fixed vocabulary; one (EXTD) is the extension gateway:

```
0x0  DEC    Decimal base 10
0x1  HEX    Hexadecimal base 16
0x2  OCT    Octal base 8
0x3  BIN    Binary base 2
0x4  B36    Base 36
0x5  B64    Base 64 (internet standard)
0x6  B256   Base 256 (raw bytes)
0x7  UNI    Unicode codepoints (U+XXXXXX)
0x8  UTF8   UTF-8 encoded
0x9  UTF16  UTF-16 encoded
0xA  EBCDIC UTF-EBCDIC mapping
0xB  ATOM   Atomic kernel state (crystal hex notation)
0xC  FRAC   Fixed-point fraction (orbit.offset)
0xD  COBS   COBS-encoded nested payload
0xE  EXTD   Extension gateway (next byte defines custom system)
0xF  RSVD   Reserved — fail-closed
```

The NUMSYS field does not change the bytes in the stream. It changes how those bytes are interpreted by the receiver. The bytes are canonical; the interpretation is a layer of context applied above the canonical bit sequence.

---

## 10. The Infinitely Nestable Escape — EXTD

Every prior in-band signaling system has a fixed escape depth:

- **Hayes `+++`:** depth 0 — mode switch only, no escaping into nested interpretation
- **Hayes DLE:** depth 1 — DLE escapes into one level of special meaning; no further nesting
- **SLIP ESC:** depth 1 — ESC escapes into one of two sequences; no further nesting
- **COBS overhead byte:** depth 1 — overhead encodes distance; the COBS structure does not nest

The Atomic Kernel introduces EXTD (NUMSYS = 0xE), which is an explicitly nestable escape. When EXTD is active on a channel/lane, the next byte defines a custom numerical system identifier. That custom system can itself define an EXTD escape for further extension.

```
Depth 0 (fixed vocabulary)
  DEC HEX OCT BIN B36 B64 B256 UNI UTF8 UTF16 EBCDIC ATOM FRAC COBS RSVD
  14 defined systems + 1 reserved

Depth 1 (EXTD)
  NUMSYS=EXTD → next byte = 8-bit custom system ID
  256 possible custom systems

Depth 2 (EXTD+EXTD)
  Custom system ID signals another EXTD → second extension byte
  256 × 256 = 65,536 possible systems

Depth N
  256^N possible custom systems reachable through N EXTD escapes
  Without modifying the kernel law
```

The core vocabulary is closed. No implementation needs to understand EXTD to use the 14 fixed systems. An implementation that encounters EXTD and does not support it fails-closed — it reports an unknown system and rejects the block. An implementation that supports EXTD can process custom systems and, if those systems define their own EXTD, recurse further.

**The depth is bounded only by the parser's willingness to follow the chain.** The encoding mechanism itself imposes no limit. Every escape is 1 byte (the EXTD marker in the NUMSYS field) plus 1 byte (the custom system ID). The overhead is constant regardless of depth.

This is what "infinitely escapable escape streams" means. Not that the system is infinite in practice — any specific implementation has a maximum depth it supports — but that the protocol's extension mechanism is not architecturally limited. The escape can always escape further.

---

## 11. The Unicode PUA Connection

When NUMSYS = UNI (0x7) or UTF8 (0x8) is active on a channel/lane, the stream is interpreted as Unicode codepoints. Within that interpretation layer, the Unicode Private Use Area (U+E000–U+F8FF) functions as the Unicode-level EXTD mechanism.

```
U+E000–U+E0FF   Kernel-reserved codepoints (ATOM law extensions)
U+E100–U+E1FF   Lane/channel addressing extensions
U+E200–U+E2FF   Numerical system extension definitions
U+E300–U+F8FF   User/application semantic space
```

A PUA codepoint in a data stream under NUMSYS=UNI is not content. It is a kernel semantic signal, exactly as EXTD is a kernel binary signal. The two are the same concept at different layers:

```
EXTD (binary level) ≡ PUA (Unicode level)
```

Both are lawful extension gateways. Both fail-closed for unrecognized values. Both allow unlimited extension without modifying the core vocabulary.

The full Unicode codepoint space — 1,114,112 codepoints across the Basic Multilingual Plane, supplementary planes, and PUA — is accessible through NUMSYS=UNI or UTF8, with the FS/GS/RS/US structural markers retaining their Unicode canonical identities (U+001C–U+001F) regardless of active NUMSYS.

---

## 12. Common Channel vs Channel-Associated Signaling

Telecommunications defines two fundamental architectures for mixing control and data:

**Common Channel Signaling (CCS):** control and data travel on separate channels. The SS7 network in telephony is CCS: voice calls travel on circuit-switched channels while signaling messages (call setup, teardown, routing) travel on a separate packet network. Control cannot corrupt data because they never share a byte stream.

**Channel-Associated Signaling (CAS):** control and data share the same channel. Embedded control information travels inline with the payload. Magic numbers in file headers, C string NULL terminators, markup language tags, terminal control codes, regex metacharacters — all CAS.

The Atomic Kernel is a CAS architecture. The choice is not accidental.

CCS requires more infrastructure: separate control channels, separate addressing, separate routing. It provides better isolation between control and data. It is the right choice for large-scale telephone networks where control volume is high and the infrastructure cost is justified.

CAS is simpler: one channel, one wire, one byte stream. It requires discipline in the encoding to prevent control from being mistaken for data. When that discipline is enforced correctly — explicit FLAG bit, non-overlapping byte ranges, fail-closed extension — it is safe and sufficient.

The discipline the Atomic Kernel enforces:

```
payload ≠ control    (FLAG bit partitions them)
structure ≠ payload  (FS/GS/RS/US are structural; data bytes are content)
framing ≠ structure  (COBS framing operates below structural grammar)
```

These three invariants hold simultaneously in the same byte stream. They hold because each operates on a different bit field or byte range that does not overlap with the others.

---

## 13. Why This Constitutes Canonicalized Access

The word "canonicalized" is precise. A canonical representation is one where every valid object has exactly one representation. Canonical access means: given a canonical stream, any compliant receiver reconstructs the same object.

Traditional multiplexing is not canonical in this sense. The external mux table is not part of the stream. Two streams that carry the same data with different mux tables may have different canonical representations — or none at all, if the mux table is lost.

The Atomic Kernel's canonicalized multiplexing has no external mux table. Every fact about interpretation is in the stream: which channel, which lane, which numerical system, which scope, which extension. The stream is its own mux table.

This has four consequences:

**1. The stream is content-addressable.** Hash the bytes and you hash the structure, the context, and the payload simultaneously. Two streams with the same hash are the same object — not just the same bytes, but the same structured, contextualized, multiplexed artifact.

**2. The stream is replayable.** Any machine, at any time, given the same canonical bytes, produces the same reconstruction. No external state is required. No mux table needs to be transmitted separately. No session context needs to be established first.

**3. The stream is self-synchronizing.** If a packet is corrupted, the receiver finds the next 0x00 (COBS delimiter) and resynchronizes. Within a packet, if a control word is unrecognized, the receiver fails-closed on that block and continues. The failure is local; the stream does not become permanently unreadable.

**4. The stream is physically embodiable.** Because the stream is its own description, it can be encoded in an Aztec symbol, printed on paper, scanned, re-decoded, and the same canonical object reconstructs. The Aztec grid coordinates (Section 6 of `AZTEC_COORD_TABLE.md`) are a projection of the canonical stream — they are deterministic, computable, and recoverable without any external reference.

---

## 14. The Escape Genealogy

Reading the full progression as an escape system:

```
Hayes command mode  (timing-gated, not byte-level, not nestable)
    ↓ quotient: remove timing dependency
Hayes DLE           (prefix-byte escape, depth 1, requires doubling)
    ↓ quotient: remove prefix byte, remove doubling
SLIP ESC            (reserved-value escape, depth 1, two reserved values)
    ↓ quotient: reduce reserved values, remove escape sequences
COBS overhead       (absorbed-zero, depth 1, one reserved value)
    ↓ quotient: reduce to one bit, extend to multiple named contexts
FLAG bit            (one-bit partition, depth N via EXTD, no reserved values)
```

Each step removes something that turned out not to be necessary while preserving what was essential. The essential thing, at every step, is the same: **the receiver must be able to tell control from data without ambiguity, at every byte, without external state.**

The final form achieves this with one reserved bit and one extension gateway. The escape is infinitely nestable but the core vocabulary is finite and closed. The stream is self-describing but requires no external description. The contexts are multiplexed but require no external mux table.

---

## 15. The Minimal Statement

This system provides: a method for multiplexing an unbounded number of simultaneously active interpretation contexts in a single byte stream, using one reserved bit for classification, four hierarchical channels for structure, sixteen parallel lanes for addressing, and one explicit extension gateway (EXTD) that is infinitely nestable, with no escape sequences, no timing dependencies, no external metadata, constant overhead, and deterministic canonical reconstruction.

The access it provides is canonicalized because the stream is its own description. What you receive is what was sent. What was sent is what was computed. What was computed is what the law produces.

One law. One stream. One reconstruction.
