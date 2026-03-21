# Header8 Stream v0

Status: Normative Draft
Authority: Algorithms only
Depends on: `docs/HEADER8_CANONICAL_ALGORITHM.md`, `docs/CONTROL_PLANE_SPEC.md`, `docs/ESCAPE_ACCESS_LAW.md`

## Purpose

Define the atomic carrier stream used for deterministic control/payload interpretation.

Header8 is a bounded carrier layer for narrative/MCP/world-adjacent projections. It is not an authority override.

## Atomic Unit

Each unit is:

`(NULL, ESC, FS, GS, RS, US, byte_point, code_block)`

Fixed axis constants:

- `NULL = 0x00`
- `ESC  = 0x1B`
- `FS   = 0x1C`
- `GS   = 0x1D`
- `RS   = 0x1E`
- `US   = 0x1F`

## Stream Artifact

`header8_stream.v0` contains:

- `stream_id`
- fixed `basis`
- encoding rules (`packed16_endian`, domains)
- ordered unit list
- deterministic digest rollups

## Canonical Packing Rules

### `pack16(byte_point, code_block)`

Valid iff both are in `0x00..0xFF`.

Packed form is big-endian by meaning:

`packed16 = (byte_point << 8) | code_block`

### `unpack16(packed16)`

Returns `(byte_point, code_block)` with both in `0x00..0xFF`.

### Extended block domain

`interpret_header(byte_point, code_block)` may accept `code_block > 0xFF`.

If `code_block > 0xFF`, use extended transport (`pack32`), not `pack16`.

## Invariants

1. Fixed six-axis basis is immutable.
2. Unit order is deterministic and meaningful.
3. `unpack16(pack16(B,C)) = (B,C)` for valid `B,C` in byte domain.
4. Same ordered units => same rollup digest.
5. Header8 stream projection must not mutate canonical truth.

## Boundary

Header8 does not replace:

- escape scope automata (still in `ESCAPE_ACCESS_LAW.md`)
- chirality ordering law
- A14 scheduling law
- proposal/receipt governance

Header8 provides atomic carrier representation for bounded inspection and transformation.
