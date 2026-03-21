# Header8 Canonical Algorithm

**Status:** Normative Draft  
**Authority:** Algorithms only  
**Depends on:** `CONTROL_PLANE_SPEC.md`, `PURE_ALGORITHMS.md`, `ESCAPE_ACCESS_LAW.md`  
**Date:** 2026

---

## Canonical Unit

Every encoded unit is represented as an 8-coordinate header:

```text
(NULL, ESC, FS, GS, RS, US, 0x&&, 0x??)
```

- First six coordinates are invariant interpretive axes.
- `0x&&` is the concrete local byte (`0x00..0xFF`).
- `0x??` is semantic block / namespace / expansion context.

---

## Axis Constants

```text
NULL = 0x00
ESC  = 0x1B
FS   = 0x1C
GS   = 0x1D
RS   = 0x1E
US   = 0x1F
```

These six values are fixed by law for Header8.

---

## A14 Algorithms

### A14.1 `make_header8(byte_point, code_block)`

```text
input:
  byte_point in [0x00..0xFF]
  code_block >= 0
output:
  Header8(
    NULL, ESC, FS, GS, RS, US,
    byte_point, code_block
  )
```

### A14.2 `classify_structural(byte_point)`

```text
0x1C -> FS
0x1D -> GS
0x1E -> RS
0x1F -> US
0x1B -> ESC
0x00 -> NULL
else -> PAYLOAD
```

### A14.3 `classify_block(code_block)`

```text
0x00               -> C0
0x20               -> BASIC_TEXT
0x80..0xEF         -> EXTENSION
0xF0..0xFF         -> CUSTOM
> 0xFF             -> CUSTOM_EXTENDED
otherwise          -> RESERVED
```

### A14.4 `interpret_header(byte_point, code_block)`

Deterministically returns:

- full 8-coordinate tuple,
- structural role,
- semantic block class.

### A14.5 `pack16(byte_point, code_block)` / `unpack16(value)`

Packed transport form:

```text
Packed16 = [byte_point][code_block]
```

`pack16` requires both inputs in `0x00..0xFF`.

---

## First-Class Artifact Form

`create_header8_artifact(byte_point, code_block)` yields:

```json
{
  "type": "header8_artifact",
  "version": 1,
  "basis": {
    "NULL": "0x00",
    "ESC": "0x1B",
    "FS": "0x1C",
    "GS": "0x1D",
    "RS": "0x1E",
    "US": "0x1F"
  },
  "byte_point": "0x1B",
  "code_block": "0x0",
  "packed16": "0x1B00",
  "structural_role": "ESC",
  "semantic_block": "C0"
}
```

This artifact kind is allowed by `artifact_package.v1` as `header8_artifact`.

---

## Invariants

1. Invariant axes are fixed: `(0x00, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F)`.
2. `byte_point` preserves local byte identity.
3. `code_block` preserves semantic block identity.
4. `unpack16(pack16(B,C)) = (B,C)` for valid byte-domain inputs.
5. `interpret_header(B,C)` is deterministic.
6. Same `(B,C)` always yields the same Header8 artifact payload.

---

## Reduction Boundary

Header8 does not replace control parsing or escape automata.

- Escape scope and deterministic return remain governed by `ESCAPE_ACCESS_LAW.md`.
- Header8 is canonical representation of one encoded unit after/by bounded control interpretation.
