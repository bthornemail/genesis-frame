# Canonical Control Plane Specification
## UTF-EBCDIC Channel Basis, 1-Bit Control Codes, 4-Channel / 16-Lane In-Band Signaling, and Unicode Codepoint Escape

**Project:** Atomic Kernel  
**Status:** Normative — Transport Layer  
**Depends on:** `kernel.py`, `AtomicKernelCoq.v`, COBS framing layer  

---

## Abstract

This specification defines the canonical in-band control signaling protocol for the Atomic Kernel transport layer. It establishes four channels derived from the Unicode / UTF-EBCDIC separator control codes (U+001C–U+001F), extends them to sixteen addressable lanes per channel via a custom mask byte, and defines four context modes including numerical system shift and full Unicode codepoint escape. The protocol is orthogonal to COBS packet framing: COBS eliminates ambiguity at packet boundaries; this specification eliminates ambiguity within packet payloads. Together they form a self-synchronizing, fail-closed, deterministic transport substrate.

---

## 1. Foundation: The UTF-EBCDIC Control Code Basis

### 1.1 Why UTF-EBCDIC

UTF-EBCDIC (RFC 2640) maps Unicode code points into EBCDIC byte sequences. The property we use is that the four ISO/IEC 6429 information separator characters — FS, GS, RS, US — occupy their canonical Unicode code points and pass through UTF-EBCDIC encoding at their natural byte values.

These characters were defined by ISO in the 1960s for exactly this purpose: structured in-band stream demarcation. They encode no printing glyph. Their sole function is structural. This specification adopts that function without inheriting any legacy encoding dependency. We use UTF-EBCDIC as the grounding reference because it establishes that these code points have a defined, stable, cross-platform byte representation that predates and survives all modern encoding debates.

### 1.2 The Four Canonical Channel Codes

| Byte | Unicode | Name | Full Name | Atomic Kernel Role |
|------|---------|------|-----------|-------------------|
| `0x1C` | U+001C | FS | File Separator | Channel 0 — World / outermost boundary |
| `0x1D` | U+001D | GS | Group Separator | Channel 1 — Group / mid-level boundary |
| `0x1E` | U+001E | RS | Record Separator | Channel 2 — Record / ordered transition |
| `0x1F` | U+001F | US | Unit Separator | Channel 3 — Unit / atomic boundary |

These four values are fixed. They are canonical Unicode code points. This specification uses them as-is.

**The kernel constant alignment:** The Atomic Kernel transition law uses `C = 0x1D1D...1D` (the byte `0x1D` repeated to the required bit width). `0x1D` is GS — the Group Separator — which in the semantic hierarchy marks the group-level boundary. The kernel's mixing constant is structurally aligned with the control plane's group channel. This is not coincidence; it is the same principle operating at two different layers.

### 1.3 The 1-Bit Control Code Principle

In a 1-bit alphabet every symbol is either structure or content. This is the deepest expression of the principle COBS applies to packet framing:

> Reserve exactly one value for structure. Make all other values content.

For packet boundaries, COBS reserves `0x00`. Within the packet payload, this specification reserves **the bit pattern `11` in bits 1:0** as the marker that a byte is a control mask rather than data.

```
data byte:    xxxxxxx0  (bit 0 = 0)
control byte: xxxxxx11  (bits 1:0 = 11)
```

The pattern `11` is chosen because:

1. Cannot be confused with a UTF-8 continuation byte (`10xxxxxx`)
2. Cannot be confused with ASCII data (`0xxxxxxx`)
3. Cannot be confused with the COBS packet delimiter (`0x00`)
4. Leaves bits 3:2 free for context type encoding

This is the 1-bit control code expressed as a 2-bit reserved marker: the minimal distinguisher between "I am a control event" and "I am data."

---

## 2. Control Sequence Format

A control event is a two-byte sequence:

```
[CHANNEL BYTE]  [MASK BYTE]
```

Extended sequences (CT=10, CT=11) add additional bytes after the mask byte.

### 2.1 Channel Byte (Byte 1)

The channel byte is one of the four canonical UTF-EBCDIC separator codes:

```
0x1C = FS   →   Channel 0
0x1D = GS   →   Channel 1
0x1E = RS   →   Channel 2
0x1F = US   →   Channel 3
```

This byte is fixed, canonical, and unambiguous. The receiver identifies the channel from this byte alone.

### 2.2 Mask Byte (Byte 2)

The mask byte encodes lane address and context mode:

```
  Bit:  7    6    5    4    3    2    1    0
        ┌────┬────┬────┬────┬────┬────┬────┬────┐
        │ L3 │ L2 │ L1 │ L0 │ CT1│ CT0│  1 │  1 │
        └────┴────┴────┴────┴────┴────┴────┴────┘

  L3:L0  =  lane address     (4 bits, lanes 0–15)
  CT1:CT0 = context type     (2 bits, types 0–3)
  bits 1:0 = 11              (control marker, mandatory)
```

| Field | Bits | Width | Values |
|-------|------|-------|--------|
| Lane | 7:4 | 4 bits | 0–15 |
| Context | 3:2 | 2 bits | 0–3 |
| Marker | 1:0 | 2 bits | always `11` |

**Mask byte formula:**
```
mask_byte = (lane << 4) | (context << 2) | 0b11
```

### 2.3 Address Space

```
4 channels × 16 lanes × 4 context types = 256 control addresses
```

Every control event has a unique two-byte address. The full canonical address is:

```
canonical_address = (channel_code << 8) | mask_byte
```

Where `channel_code` ∈ {0x1C, 0x1D, 0x1E, 0x1F}.

---

## 3. Context Types

The CT field (bits 3:2 of the mask byte) specifies how the receiver interprets the payload that follows the control sequence.

### CT = `00` — Default

Normal mode. Payload bytes for this channel and lane use the current numeral system and interpretation context.

```
[0x1D] [0x03]   →   GS, lane 0, default
[0x1D] [0x73]   →   GS, lane 7, default
[0x1C] [0xF3]   →   FS, lane 15, default
```

### CT = `01` — Numerical System Shift

The next value on this channel/lane is interpreted in a different numeral system. The system is encoded in bits L3:L2 of the mask byte. Bits L1:L0 carry the lane address within the new context.

**Numeral system table (L3:L2 when CT=01):**

| L3:L2 | Code | Base | Description |
|-------|------|------|-------------|
| `00` | DEC | 10 | Decimal — standard UTF-EBCDIC digit encoding |
| `01` | BIN | 2  | Binary — raw bit stream |
| `10` | HEX | 16 | Hexadecimal — compact encoding |
| `11` | B36 | 36 | Base-36 — alphanumeric compact form |

The shift applies to **the next value only**. After that value, context reverts. This is stateless — each control event is fully self-contained.

**Mask byte formula for CT=01:**
```
mask_byte = (numeral_system << 6) | (lane_within_ctx << 4) | (0b01 << 2) | 0b11
```

**Examples:**

Switch to HEX for next value on FS/lane 0:
```
[0x1C] [0x17]
  FS    L3:L2=10(HEX), L1:L0=00(lane 0), CT=01, marker=11
```

Switch to binary on RS/lane 5:
```
[0x1E] [0x57]
  RS    L3:L2=01(BIN), L1:L0=01(lane 1→actual lane 5 calc), CT=01, marker=11
```

### CT = `10` — Unicode Codepoint Escape

The mask byte is followed by a UTF-8 encoded Unicode codepoint. This allows any of the 1,114,112 Unicode code points to be signaled in-band on any channel/lane combination.

**Extended sequence format:**
```
[CHANNEL] [MASK with CT=10] [UTF-8 bytes for one codepoint]
```

**Why this is unambiguous:**

The mask byte has bits 1:0 = `11`. UTF-8 encoding guarantees:
- Single-byte U+0000–U+007F: `0xxxxxxx` — bit 7 = 0, distinct
- Two-byte lead: `110xxxxx` — bits 7:5 = `110`, distinct from `xxxxxx11`
- Three-byte lead: `1110xxxx` — bits 7:4 = `1110`, distinct
- Four-byte lead: `11110xxx` — bits 7:3 = `11110`, distinct
- Continuation bytes: `10xxxxxx` — bits 7:6 = `10`, distinct from `xx11` in low bits

The receiver reads UTF-8 bytes until one complete codepoint is consumed. The length is determined by the UTF-8 lead byte. No delimiter or length prefix needed.

**Example — signal U+2202 (∂) on RS/lane 3:**
```
[0x1E] [0x3B] [0xE2] [0x88] [0x82]
  RS   lane=3, CT=10   ←— UTF-8 for U+2202 (3 bytes) —→
```

**This is the gateway from the finite control basis to the full Unicode space.** The control plane has 256 addresses. The Unicode space has 1,114,112 code points. CT=10 bridges them: any Unicode codepoint can be signaled in-band on any of the 64 channel/lane combinations.

### CT = `11` — Extended / Algorithm-Defined Mask

The mask byte is followed by a second byte whose interpretation is defined by the Atomic Kernel's crystal state at the current tick.

**Extended sequence format:**
```
[CHANNEL] [MASK with CT=11] [ALGORITHM MASK BYTE]
```

**Algorithm mask byte layout:**
```
  Bit:  7    6    5    4    3    2    1    0
        ┌────┬────┬────┬────┬────┬────┬────┬────┐
        │ A3 │ A2 │ A1 │ A0 │ X3 │ X2 │ X1 │ X0 │
        └────┴────┴────┴────┴────┴────┴────┴────┘

  A3:A0  =  algorithm selector (from crystal phase)
  X3:X0  =  algorithm-specific parameter
```

The algorithm selector is derived from the crystal's periodic differential block B:

```python
B        = [0, 1, 3, 6, 9, 8, 6, 3]   # digits of 1/73
algorithm = B[tick % 8]                 # 0–9, bounded to 4 bits: B[t] & 0x0F
```

Any observer with the same seed and tick number independently computes the same algorithm selector. The CT=11 context is therefore deterministic and replayable — no out-of-band agreement, no shared secret, no external state.

---

## 4. Complete Mask Byte Table

All 64 (lane × context) combinations. Bits 1:0 = `11` always.

```
mask_byte = (lane << 4) | (context << 2) | 0b11
```

| Lane | Default (CT=00) | NumSys (CT=01) | Unicode (CT=10) | Extended (CT=11) |
|------|----------------|----------------|-----------------|-----------------|
| 0    | `0x03`         | `0x07`         | `0x0B`          | `0x0F`          |
| 1    | `0x13`         | `0x17`         | `0x1B`          | `0x1F`          |
| 2    | `0x23`         | `0x27`         | `0x2B`          | `0x2F`          |
| 3    | `0x33`         | `0x37`         | `0x3B`          | `0x3F`          |
| 4    | `0x43`         | `0x47`         | `0x4B`          | `0x4F`          |
| 5    | `0x53`         | `0x57`         | `0x5B`          | `0x5F`          |
| 6    | `0x63`         | `0x67`         | `0x6B`          | `0x6F`          |
| 7    | `0x73`         | `0x77`         | `0x7B`          | `0x7F`          |
| 8    | `0x83`         | `0x87`         | `0x8B`          | `0x8F`          |
| 9    | `0x93`         | `0x97`         | `0x9B`          | `0x9F`          |
| 10   | `0xA3`         | `0xA7`         | `0xAB`          | `0xAF`          |
| 11   | `0xB3`         | `0xB7`         | `0xBB`          | `0xBF`          |
| 12   | `0xC3`         | `0xC7`         | `0xCB`          | `0xCF`          |
| 13   | `0xD3`         | `0xD7`         | `0xDB`          | `0xDF`          |
| 14   | `0xE3`         | `0xE7`         | `0xEB`          | `0xEF`          |
| 15   | `0xF3`         | `0xF7`         | `0xFB`          | `0xFF`          |

This table applies to all four channels (FS/GS/RS/US). The channel byte selects the channel; the mask byte selects the lane and context from this table.

---

## 5. Relationship to COBS Framing

COBS and this specification are orthogonal. They solve different problems at different scopes.

| Layer | Mechanism | Reserved value | Problem solved |
|-------|-----------|----------------|----------------|
| COBS | Overhead byte + hop chain | `0x00` | Packet boundary ambiguity |
| This spec | Channel + mask byte | bits 1:0 = `11` | In-payload control ambiguity |

**Why they cannot interfere:**

COBS only modifies bytes that equal `0x00`. The channel bytes (`0x1C`–`0x1F`) are never zero. The mask bytes have bits 1:0 = `11`, so their minimum value is `0x03` — also never zero. COBS passes all control sequence bytes through unchanged.

The complete COBS-framed packet:

```
COBS_encode(
  [channel, mask, payload...]+   ← control sequences and data
) + 0x00                         ← COBS packet delimiter
```

Inside the COBS payload: control sequences use the `11` marker for unambiguous identification.  
At the packet boundary: COBS uses `0x00` for unambiguous framing.  
The two mechanisms share no reserved values.

---

## 6. Relationship to Full Unicode Codepoint Space

The channel codes are Unicode code points. The CT=10 escape provides access to the full Unicode codepoint space. The relationship is:

```
finite control basis (4 channels × 16 lanes × 4 contexts = 256 addresses)
             ↓  CT=10 escape
full Unicode space (U+0000–U+10FFFF, 1,114,112 codepoints)
             ↓  UTF-8 encoding
byte stream (deterministic, self-synchronizing, no ambiguity)
```

**Algorithmically keyed Unicode signals:**

The crystal's state at tick N with seed S determines a unique position:

```python
state         = state_at(seed, N)
position      = position_at(N)
orbit, offset = divmod(position, 36)   # W = 36
phase         = N % 8
```

A CT=10 escape on channel/lane X at tick N can be algorithmically keyed so that `state XOR orbit XOR offset` maps to a Unicode codepoint. Any observer with the same seed and tick independently derives the same codepoint. The in-band Unicode signal is deterministic and replayable.

---

## 7. Fail-Closed Invariants

### 7.1 Missing or invalid mask byte

A channel byte (0x1C–0x1F) not followed by a byte with bits 1:0 = `11` is a protocol violation. The receiver fails closed and discards to the next COBS delimiter.

### 7.2 Invalid CT=10 UTF-8 sequence

If the bytes following a CT=10 mask byte do not form a valid UTF-8 codepoint (invalid lead, truncated sequence, overlong encoding, surrogate pair), the receiver fails closed.

### 7.3 CT=11 algorithm mismatch

If the algorithm mask byte does not match the expected crystal state at the current tick, the receiver treats the control event as tampered or replayed and fails closed.

### 7.4 No silent degradation

There is no fallback mode. Every ambiguity is a protocol violation. This is the same principle COBS applies at the packet level: either the stream is deterministically interpretable, or it is rejected.

---

## 8. Annotated Example Packet

```
Raw payload (before COBS encoding):

  0x1C  0x03                     ← FS / lane 0 / CT=00 default
  0x48  0x65  0x6C  0x6C  0x6F  ← "Hello" (ASCII data, bit-0=0 for all)
  0x1D  0x73                     ← GS / lane 7 / CT=00 default
  0xDE  0xAD                     ← group payload bytes
  0x1E  0x3B                     ← RS / lane 3 / CT=10 Unicode escape
  0xE2  0x88  0x82               ← U+2202 (∂ partial differential) UTF-8
  0x1F  0x17                     ← US / lane 0 / CT=01 NumSys shift, L3:L2=10=HEX
  0x4A  0x2F                     ← unit data in HEX context
  0x1D  0x0F                     ← GS / lane 0 / CT=11 extended
  0xA3                           ← algorithm mask byte

After COBS encoding:

  [overhead bytes interspersed — only zeros are stuffed]
  ... [all above bytes] ...
  0x00                           ← packet delimiter

No 0x00 inside. Delimiter is unambiguous.
All control sequences identified by channel byte (0x1C-0x1F) + mask marker (bits 1:0 = 11).
```

---

## 9. Summary Table

| Concept | Value | Source |
|---------|-------|--------|
| Channel codes | 0x1C, 0x1D, 0x1E, 0x1F | Unicode U+001C–U+001F (ISO 6429) |
| Channel names | FS, GS, RS, US | File / Group / Record / Unit Separator |
| Channels | 4 | Fixed |
| Lanes per channel | 16 | 4-bit L field in mask byte |
| Context types | 4 | 2-bit CT field in mask byte |
| Control marker | bits 1:0 = `11` | 1-bit principle: reserve one pattern for structure |
| Total addresses | 256 | 4 × 16 × 4 |
| COBS delimiter | `0x00` | Orthogonal; never appears in control sequences |
| Unicode escape | CT=10 + UTF-8 | Full 1,114,112 codepoint space in-band |
| NumSys shift | CT=01 + L3:L2 | DEC / BIN / HEX / B36 per value |
| Extended mode | CT=11 + crystal | Algorithmically keyed, deterministic, replayable |
| Kernel constant C | `0x1D1D...1D` | GS byte repeated — structurally aligned with Channel 1 |

---

## 10. Boundary

This specification defines the transport control plane only. It does not redefine the kernel transition law (`delta`), the crystal timing law, or the identity chain. The control plane is a projection surface over the kernel. It cannot alter canonical state. It signals boundaries and context shifts to receivers who share the same kernel law.
