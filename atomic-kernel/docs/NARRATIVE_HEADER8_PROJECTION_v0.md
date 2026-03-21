# Narrative -> Header8 Projection v0

Status: Advisory Draft
Authority: Advisory projection contract
Depends on: `docs/HEADER8_STREAM_v0.md`, `docs/CONTROL_PLANE_SPEC.md`, `narrative_data/chapters/*.ndjson`

## Purpose

Define deterministic projection from chapter NDJSON records to `header8_stream.v0`.

## Framing Map

- `FS` => chapter boundary
- `GS` => scene boundary
- `RS` => record boundary
- `US` => field/value unit boundary

## Deterministic Projection Rule

For each NDJSON record in file order:

1. emit `RS` record boundary unit
2. emit `US` key/value units in sorted key order
3. preserve explicit chapter/scene separators as control units
4. produce stable digest over resulting unit sequence

## Constraints

- No authority escalation: projection remains advisory
- No implicit field reordering except explicit sorted-key rule
- Unknown record shapes are fail-closed in strict mode

## Output Contract

Output artifact shape:

- `v: "header8_stream.v0"`
- `authority: "advisory"`
- `source_kind: "narrative_ndjson"`
- deterministic unit sequence
- deterministic digest
