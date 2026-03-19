# Aztec Grid Coordinate Mapping
## Normative Appendix: 60 Canonical (Channel, Lane) States in the 27×27 Reference Symbol

**Status:** Normative  
**Authority:** Extension — Artifact Geometry  
**Depends on:** `AZTEC_ARTIFACT_SPEC.md`, `CONTROL_PLANE_SPEC.md`  
**Date:** 2026

---

## Purpose

This appendix derives and enumerates the exact module coordinates for all 60 canonical (channel, non-null-lane) runtime states in the 4-layer 27×27 reference Aztec symbol. These coordinates are normative: any compliant implementation must place and read the 60 canonical state modules at exactly these positions.

This turns the geometric mapping from a conceptual description into a deterministic specification.

---

## 1. Reference Symbol Parameters

```
Symbol type:      4-layer full Aztec symbol
Grid size:        27 × 27 modules
Center:           (13, 13)  (0-indexed, top-left origin)
Bull's-eye:       modules with Chebyshev distance r ≤ 2  (5×5 = 25 modules)
Mode ring:        modules with r = 3                      (24 modules)
Data layer 1:     modules with r ∈ {4, 5}                (72 modules) → US channel
Data layer 2:     modules with r ∈ {6, 7}                (104 modules) → RS channel
Data layer 3:     modules with r ∈ {8, 9}                (136 modules) → GS channel
Data layer 4:     modules with r ∈ {10, 11}              (168 modules) → FS channel
```

Where the Chebyshev distance from center is defined as:

```
r(x, y) = max(|x − 13|, |y − 13|)
```

---

## 2. Coordinate System

The coordinate origin is the top-left corner of the symbol grid:

```
(0, 0) = top-left module
(26, 0) = top-right module
(0, 26) = bottom-left module
(26, 26) = bottom-right module
(13, 13) = center (bull's-eye center)
```

X increases rightward. Y increases downward.

---

## 3. Channel-to-Ring Assignment

Channels map to data layers by the containment principle: innermost scope maps to innermost data ring.

```
CH 0  US  Unit Separator      r ∈ {4,  5}   innermost data layer
CH 1  RS  Record Separator    r ∈ {6,  7}
CH 2  GS  Group Separator     r ∈ {8,  9}
CH 3  FS  File Separator      r ∈ {10, 11}  outermost data layer
```

---

## 4. Lane-to-Quadrant Assignment

The 16 lanes divide into four quadrant groups of four, aligned with the Klein four-group structure of the channel field:

```
Lane bits [3:2] = 00  lanes  0– 3   Q0/Q1 (right-side, FS-aligned)
Lane bits [3:2] = 01  lanes  4– 7   Q1/Q2 (bottom-side, GS-aligned)
Lane bits [3:2] = 10  lanes  8–11   Q2/Q3 (left-side, RS-aligned)
Lane bits [3:2] = 11  lanes 12–15   Q3/Q0 (top-side, US-aligned)
```

Quadrant definitions (half-open, covering the full ring boundary):

```
Q0  TR  top-right:     x ≥ 13 and y < 13
Q1  BR  bottom-right:  x > 13 and y ≥ 13
Q2  BL  bottom-left:   x ≤ 13 and y > 13
Q3  TL  top-left:      x < 13 and y ≤ 13
```

Lane 0 (binary 0000) is the null lane — the zero vector of GF(2)^4. It occupies a coordinate position in each channel layer but carries no data. Its position is the clockwise-start position of each channel layer (top-right corner).

Lanes 1–15 (the 15 non-zero vectors) occupy the remaining 15 evenly-spaced positions.

---

## 5. GF(2)^4 Lane Vector Structure

All 16 lanes as 4-bit vectors:

```
Lane  Binary  Hex  Status   bits[3:2]  bits[1:0]  Channel alignment
   0  0000    0x0  null     00=FS       00         Lane group 0 (FS-aligned)
   1  0001    0x1  data     00=FS       01
   2  0010    0x2  data     00=FS       10
   3  0011    0x3  data     00=FS       11
   4  0100    0x4  data     01=GS       00         Lane group 1 (GS-aligned)
   5  0101    0x5  data     01=GS       01
   6  0110    0x6  data     01=GS       10
   7  0111    0x7  data     01=GS       11
   8  1000    0x8  data     10=RS       00         Lane group 2 (RS-aligned)
   9  1001    0x9  data     10=RS       01
  10  1010    0xA  data     10=RS       10
  11  1011    0xB  data     10=RS       11
  12  1100    0xC  data     11=US       00         Lane group 3 (US-aligned)
  13  1101    0xD  data     11=US       01
  14  1110    0xE  data     11=US       10
  15  1111    0xF  data     11=US       11
```

Lane bits[3:2] encodes which channel group the lane is aligned with.  
Lane bits[1:0] encodes the position within that group (0–3).  
Lane 0 (0000) is the null lane — the identity element, zero vector.

---

## 6. Normative Coordinate Table

The following table is normative. Each row specifies the exact grid coordinates of one canonical (channel, lane) runtime state in the 27×27 reference symbol.

All 60 entries have been verified: no coordinate collisions, all within grid bounds, all Chebyshev distances match ring assignments.

```
 CH  CHAN  LANE  BITS    X    Y    R  QUAD   Notes
───────────────────────────────────────────────────────
  0    US     1  0001   17   13    4    BR
  0    US     2  0010   16   17    4    BR
  0    US     3  0011   11   17    4    BL
  0    US     4  0100    9   15    4    BL
  0    US     5  0101    9   11    4    TL
  0    US     6  0110   12    9    4    TL
  0    US     7  0111   18    8    5    TR
  0    US     8  1000   18   12    5    TR
  0    US     9  1001   18   16    5    BR
  0    US    10  1010   15   18    5    BR
  0    US    11  1011   10   18    5    BL
  0    US    12  1100    8   16    5    BL
  0    US    13  1101    8   12    5    TL
  0    US    14  1110    9    8    5    TL
  0    US    15  1111   14    8    5    TR
───────────────────────────────────────────────────────
  1    RS     1  0001   19   13    6    BR
  1    RS     2  0010   18   19    6    BR
  1    RS     3  0011   11   19    6    BL
  1    RS     4  0100    7   17    6    BL
  1    RS     5  0101    7   11    6    TL
  1    RS     6  0110   10    7    6    TL
  1    RS     7  0111   17    7    6    TR
  1    RS     8  1000   20   10    7    TR
  1    RS     9  1001   20   16    7    BR
  1    RS    10  1010   17   20    7    BR
  1    RS    11  1011   10   20    7    BL
  1    RS    12  1100    6   18    7    BL
  1    RS    13  1101    6   12    7    TL
  1    RS    14  1110    7    6    7    TL
  1    RS    15  1111   14    6    7    TR
───────────────────────────────────────────────────────
  2    GS     1  0001   21   13    8    BR
  2    GS     2  0010   20   21    8    BR
  2    GS     3  0011   11   21    8    BL
  2    GS     4  0100    5   19    8    BL
  2    GS     5  0101    5   11    8    TL
  2    GS     6  0110    8    5    8    TL
  2    GS     7  0111   17    5    8    TR
  2    GS     8  1000   22    8    9    TR
  2    GS     9  1001   22   16    9    BR
  2    GS    10  1010   19   22    9    BR
  2    GS    11  1011   10   22    9    BL
  2    GS    12  1100    4   20    9    BL
  2    GS    13  1101    4   12    9    TL
  2    GS    14  1110    5    4    9    TL
  2    GS    15  1111   14    4    9    TR
───────────────────────────────────────────────────────
  3    FS     1  0001   23   13   10    BR
  3    FS     2  0010   22   23   10    BR
  3    FS     3  0011   11   23   10    BL
  3    FS     4  0100    3   21   10    BL
  3    FS     5  0101    3   11   10    TL
  3    FS     6  0110    6    3   10    TL
  3    FS     7  0111   17    3   10    TR
  3    FS     8  1000   24    6   11    TR
  3    FS     9  1001   24   16   11    BR
  3    FS    10  1010   21   24   11    BR
  3    FS    11  1011   10   24   11    BL
  3    FS    12  1100    2   22   11    BL
  3    FS    13  1101    2   12   11    TL
  3    FS    14  1110    3    2   11    TL
  3    FS    15  1111   14    2   11    TR
```

**Verification:** 60 entries, 60 unique (x,y) positions, 15 per channel, all within 0–26 bounds, all r values match channel layer assignment.

---

## 7. Null Lane Positions (Informational)

The null lane (lane 0) position for each channel is the clockwise-start position of the channel's inner ring. These positions are not data-carrying but are structurally significant as origin points for the clockwise traversal:

```
CH 0  US  lane 0  (13,  9)   r=4   top edge, inner ring
CH 1  RS  lane 0  (13,  6)   r=7   top edge, inner ring
CH 2  GS  lane 0  (13,  4)   r=9   top edge, inner ring
CH 3  FS  lane 0  (13,  2)   r=11  top edge, inner ring
```

---

## 8. Pattern Properties

The coordinate table exhibits four structural patterns that can be used for quick verification:

**1. Lane 1 (0001) is always on the right-center axis:**  
All four CH, lane 1 entries have Y = 13 (center row) and increasing X: (17,13), (19,13), (21,13), (23,13).

**2. Lane 15 (1111) is always on the top edge:**  
All four CH, lane 15 entries have Y decreasing from center with increasing radius: (14,8), (14,6), (14,4), (14,2).

**3. Lane 7 (0111) is always on the top edge opposite:**  
All four CH, lane 7 entries have Y decreasing and X right of center: (18,8), (17,7), (17,5), (17,3).

**4. Symmetric quadrant distribution:**  
Each channel has 3 modules in Q0 (TR) and 4 each in Q1/Q2/Q3. This is the result of the 15 non-null lanes not dividing evenly into 4 quadrants (15 = 4+4+4+3). Lane 15 (1111) is always the 4th TR module — the only lane that shares a quadrant with lanes 7 and 8.

---

## 9. Compact Formula

For implementations that prefer to compute coordinates rather than look them up, the position of lane `L` in channel `CH` follows this formula:

```
r_base = 4 + 2 * CH           (inner ring radius for this channel)
r      = r_base + (L >= 8)    (outer ring if lane >= 8)

θ_index = L mod 8             (position within the ring half)

ring_circumference = 8 * r_base - 4  (modules in the inner ring)
step = ring_circumference / 8

base_angle_index = θ_index * step
```

Then traverse the ring clockwise from (13+r_base, 13-r_base) by `base_angle_index` positions to find (x, y).

The table in Section 6 takes precedence over this formula. The formula is provided as an implementation aid for verification.

---

## 10. JSON Machine-Readable Form

```json
[
  {"channel":0,"channel_name":"US","lane":1,"lane_bits":"0001","x":17,"y":13,"r":4,"quadrant":1,"quadrant_name":"BR"},
  {"channel":0,"channel_name":"US","lane":2,"lane_bits":"0010","x":16,"y":17,"r":4,"quadrant":1,"quadrant_name":"BR"},
  {"channel":0,"channel_name":"US","lane":3,"lane_bits":"0011","x":11,"y":17,"r":4,"quadrant":2,"quadrant_name":"BL"},
  {"channel":0,"channel_name":"US","lane":4,"lane_bits":"0100","x":9,"y":15,"r":4,"quadrant":2,"quadrant_name":"BL"},
  {"channel":0,"channel_name":"US","lane":5,"lane_bits":"0101","x":9,"y":11,"r":4,"quadrant":3,"quadrant_name":"TL"},
  {"channel":0,"channel_name":"US","lane":6,"lane_bits":"0110","x":12,"y":9,"r":4,"quadrant":3,"quadrant_name":"TL"},
  {"channel":0,"channel_name":"US","lane":7,"lane_bits":"0111","x":18,"y":8,"r":5,"quadrant":0,"quadrant_name":"TR"},
  {"channel":0,"channel_name":"US","lane":8,"lane_bits":"1000","x":18,"y":12,"r":5,"quadrant":0,"quadrant_name":"TR"},
  {"channel":0,"channel_name":"US","lane":9,"lane_bits":"1001","x":18,"y":16,"r":5,"quadrant":1,"quadrant_name":"BR"},
  {"channel":0,"channel_name":"US","lane":10,"lane_bits":"1010","x":15,"y":18,"r":5,"quadrant":1,"quadrant_name":"BR"},
  {"channel":0,"channel_name":"US","lane":11,"lane_bits":"1011","x":10,"y":18,"r":5,"quadrant":2,"quadrant_name":"BL"},
  {"channel":0,"channel_name":"US","lane":12,"lane_bits":"1100","x":8,"y":16,"r":5,"quadrant":2,"quadrant_name":"BL"},
  {"channel":0,"channel_name":"US","lane":13,"lane_bits":"1101","x":8,"y":12,"r":5,"quadrant":3,"quadrant_name":"TL"},
  {"channel":0,"channel_name":"US","lane":14,"lane_bits":"1110","x":9,"y":8,"r":5,"quadrant":3,"quadrant_name":"TL"},
  {"channel":0,"channel_name":"US","lane":15,"lane_bits":"1111","x":14,"y":8,"r":5,"quadrant":0,"quadrant_name":"TR"},
  {"channel":1,"channel_name":"RS","lane":1,"lane_bits":"0001","x":19,"y":13,"r":6,"quadrant":1,"quadrant_name":"BR"},
  {"channel":1,"channel_name":"RS","lane":2,"lane_bits":"0010","x":18,"y":19,"r":6,"quadrant":1,"quadrant_name":"BR"},
  {"channel":1,"channel_name":"RS","lane":3,"lane_bits":"0011","x":11,"y":19,"r":6,"quadrant":2,"quadrant_name":"BL"},
  {"channel":1,"channel_name":"RS","lane":4,"lane_bits":"0100","x":7,"y":17,"r":6,"quadrant":2,"quadrant_name":"BL"},
  {"channel":1,"channel_name":"RS","lane":5,"lane_bits":"0101","x":7,"y":11,"r":6,"quadrant":3,"quadrant_name":"TL"},
  {"channel":1,"channel_name":"RS","lane":6,"lane_bits":"0110","x":10,"y":7,"r":6,"quadrant":3,"quadrant_name":"TL"},
  {"channel":1,"channel_name":"RS","lane":7,"lane_bits":"0111","x":17,"y":7,"r":6,"quadrant":0,"quadrant_name":"TR"},
  {"channel":1,"channel_name":"RS","lane":8,"lane_bits":"1000","x":20,"y":10,"r":7,"quadrant":0,"quadrant_name":"TR"},
  {"channel":1,"channel_name":"RS","lane":9,"lane_bits":"1001","x":20,"y":16,"r":7,"quadrant":1,"quadrant_name":"BR"},
  {"channel":1,"channel_name":"RS","lane":10,"lane_bits":"1010","x":17,"y":20,"r":7,"quadrant":1,"quadrant_name":"BR"},
  {"channel":1,"channel_name":"RS","lane":11,"lane_bits":"1011","x":10,"y":20,"r":7,"quadrant":2,"quadrant_name":"BL"},
  {"channel":1,"channel_name":"RS","lane":12,"lane_bits":"1100","x":6,"y":18,"r":7,"quadrant":2,"quadrant_name":"BL"},
  {"channel":1,"channel_name":"RS","lane":13,"lane_bits":"1101","x":6,"y":12,"r":7,"quadrant":3,"quadrant_name":"TL"},
  {"channel":1,"channel_name":"RS","lane":14,"lane_bits":"1110","x":7,"y":6,"r":7,"quadrant":3,"quadrant_name":"TL"},
  {"channel":1,"channel_name":"RS","lane":15,"lane_bits":"1111","x":14,"y":6,"r":7,"quadrant":0,"quadrant_name":"TR"},
  {"channel":2,"channel_name":"GS","lane":1,"lane_bits":"0001","x":21,"y":13,"r":8,"quadrant":1,"quadrant_name":"BR"},
  {"channel":2,"channel_name":"GS","lane":2,"lane_bits":"0010","x":20,"y":21,"r":8,"quadrant":1,"quadrant_name":"BR"},
  {"channel":2,"channel_name":"GS","lane":3,"lane_bits":"0011","x":11,"y":21,"r":8,"quadrant":2,"quadrant_name":"BL"},
  {"channel":2,"channel_name":"GS","lane":4,"lane_bits":"0100","x":5,"y":19,"r":8,"quadrant":2,"quadrant_name":"BL"},
  {"channel":2,"channel_name":"GS","lane":5,"lane_bits":"0101","x":5,"y":11,"r":8,"quadrant":3,"quadrant_name":"TL"},
  {"channel":2,"channel_name":"GS","lane":6,"lane_bits":"0110","x":8,"y":5,"r":8,"quadrant":3,"quadrant_name":"TL"},
  {"channel":2,"channel_name":"GS","lane":7,"lane_bits":"0111","x":17,"y":5,"r":8,"quadrant":0,"quadrant_name":"TR"},
  {"channel":2,"channel_name":"GS","lane":8,"lane_bits":"1000","x":22,"y":8,"r":9,"quadrant":0,"quadrant_name":"TR"},
  {"channel":2,"channel_name":"GS","lane":9,"lane_bits":"1001","x":22,"y":16,"r":9,"quadrant":1,"quadrant_name":"BR"},
  {"channel":2,"channel_name":"GS","lane":10,"lane_bits":"1010","x":19,"y":22,"r":9,"quadrant":1,"quadrant_name":"BR"},
  {"channel":2,"channel_name":"GS","lane":11,"lane_bits":"1011","x":10,"y":22,"r":9,"quadrant":2,"quadrant_name":"BL"},
  {"channel":2,"channel_name":"GS","lane":12,"lane_bits":"1100","x":4,"y":20,"r":9,"quadrant":2,"quadrant_name":"BL"},
  {"channel":2,"channel_name":"GS","lane":13,"lane_bits":"1101","x":4,"y":12,"r":9,"quadrant":3,"quadrant_name":"TL"},
  {"channel":2,"channel_name":"GS","lane":14,"lane_bits":"1110","x":5,"y":4,"r":9,"quadrant":3,"quadrant_name":"TL"},
  {"channel":2,"channel_name":"GS","lane":15,"lane_bits":"1111","x":14,"y":4,"r":9,"quadrant":0,"quadrant_name":"TR"},
  {"channel":3,"channel_name":"FS","lane":1,"lane_bits":"0001","x":23,"y":13,"r":10,"quadrant":1,"quadrant_name":"BR"},
  {"channel":3,"channel_name":"FS","lane":2,"lane_bits":"0010","x":22,"y":23,"r":10,"quadrant":1,"quadrant_name":"BR"},
  {"channel":3,"channel_name":"FS","lane":3,"lane_bits":"0011","x":11,"y":23,"r":10,"quadrant":2,"quadrant_name":"BL"},
  {"channel":3,"channel_name":"FS","lane":4,"lane_bits":"0100","x":3,"y":21,"r":10,"quadrant":2,"quadrant_name":"BL"},
  {"channel":3,"channel_name":"FS","lane":5,"lane_bits":"0101","x":3,"y":11,"r":10,"quadrant":3,"quadrant_name":"TL"},
  {"channel":3,"channel_name":"FS","lane":6,"lane_bits":"0110","x":6,"y":3,"r":10,"quadrant":3,"quadrant_name":"TL"},
  {"channel":3,"channel_name":"FS","lane":7,"lane_bits":"0111","x":17,"y":3,"r":10,"quadrant":0,"quadrant_name":"TR"},
  {"channel":3,"channel_name":"FS","lane":8,"lane_bits":"1000","x":24,"y":6,"r":11,"quadrant":0,"quadrant_name":"TR"},
  {"channel":3,"channel_name":"FS","lane":9,"lane_bits":"1001","x":24,"y":16,"r":11,"quadrant":1,"quadrant_name":"BR"},
  {"channel":3,"channel_name":"FS","lane":10,"lane_bits":"1010","x":21,"y":24,"r":11,"quadrant":1,"quadrant_name":"BR"},
  {"channel":3,"channel_name":"FS","lane":11,"lane_bits":"1011","x":10,"y":24,"r":11,"quadrant":2,"quadrant_name":"BL"},
  {"channel":3,"channel_name":"FS","lane":12,"lane_bits":"1100","x":2,"y":22,"r":11,"quadrant":2,"quadrant_name":"BL"},
  {"channel":3,"channel_name":"FS","lane":13,"lane_bits":"1101","x":2,"y":12,"r":11,"quadrant":3,"quadrant_name":"TL"},
  {"channel":3,"channel_name":"FS","lane":14,"lane_bits":"1110","x":3,"y":2,"r":11,"quadrant":3,"quadrant_name":"TL"},
  {"channel":3,"channel_name":"FS","lane":15,"lane_bits":"1111","x":14,"y":2,"r":11,"quadrant":0,"quadrant_name":"TR"}
]
```

---

## 11. Relation to the Aztec Specification

This coordinate table is a **projection convention**, not an Aztec decoding requirement. Standard Aztec decoders do not know about (channel, lane) semantics — they decode a byte stream. The coordinate table specifies which bytes in the decoded stream correspond to which (channel, lane) canonical states when the stream is interpreted as a kernel artifact.

The Aztec ECC operates on all data bytes uniformly. The coordinate-to-state mapping is applied after successful ECC verification, during the kernel's structural parsing of the decoded byte stream. This is consistent with the principle that Aztec is context-neutral (Section 4 of `AZTEC_ARTIFACT_SPEC.md`).
