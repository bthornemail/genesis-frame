# Algorithm A13 — ESC-Depth Mixed-Radix Coordinate Header

**Status:** Normative Draft  
**Authority:** Algorithms only  
**Depends on:** `PURE_ALGORITHMS.md` (mixed encode/decode), `ESCAPE_ACCESS_LAW.md`, `CONTROL_PLANE_SPEC.md`  
**Date:** 2026

---

## Core Rule

The number of leading `ESC` symbols defines decode depth.

Depth determines the radix list used to decode the coordinate payload that follows.

```text
ESC^n -> use radices_for_depth(n) -> decode with mixed_decode
```

---

## Canonical 8-Symbol Basis

```text
NULL, ESC, FS, GS, RS, US, 0x&&, 0x??
```

- `NULL` is framing/reset anchor.
- `ESC` is depth/index axis.
- `FS/GS/RS/US` are structural axes.
- `0x&&` is byte/control fold axis.
- `0x??` is extended Unicode block axis.

---

## Depth Mapping

```text
depth 1 -> []                 (unary direct payload)
depth 2 -> [128]              (C0/C1 fold)
depth 3 -> [36, 8]            (orbit/offset timing frame)
depth 4 -> [256, 65536]       (full byte + Unicode block)
depth >4 -> extension law     (append one radix per depth)
```

Invariant:

```text
len(radices_for_depth(n)) = n - 1   for n >= 2
```

---

## A13 Algorithms

### A13a `esc_encode(value, depth)`

```text
prefix = [ESC] * depth
coords = mixed_encode(value, radices_for_depth(depth))   # depth>=2
stream = prefix ++ coords
```

Depth 1 emits direct payload after one `ESC`.

### A13b `esc_decode(stream)`

```text
depth  = count_leading_ESC(stream)
radix  = radices_for_depth(depth)
coords = next len(radix)+1 coordinates (or 1 direct unit at depth=1)
value  = mixed_decode(coords, radix)    # depth>=2
```

Roundtrip:

```text
esc_decode(esc_encode(v, d)).value = v
```

---

## A12 Consistency

`ESC ESC` remains literalization-compatible with A12:

- A12: `ESC ESC` resolves a literal escape payload path.
- A13: depth-2 prefix is valid and decodes via `[128]`.

Both rules are compatible under bounded scope and deterministic return.

---

## Transylvania/Fano Ticket Set (14)

Two 7-line ticket sets are used as coverage witnesses:

- low set includes `NULL` anchor relations,
- high set includes `0x&&` extension relations.

Normative witness checks:

- ticket count = 14
- `NULL` appears only in low set
- active symbol pair coverage is complete for:

```text
{ESC, FS, GS, RS, US, 0x&&, 0x??}
```

---

## Reduction Notes

- A13 is an indexing convention over existing mixed-radix law.
- A13 does not replace escape automaton rules in `ESCAPE_ACCESS_LAW.md`.
- A13 composes with A12 by keeping depth bounded and return deterministic.
