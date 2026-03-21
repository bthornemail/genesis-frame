# Role -> Toolset Matrix v0

Status: Normative Draft
Authority: Advisory execution contract
Depends on: `docs/AGENT112_SPEC_v0.md`, `docs/WITNESS_PLANE_SPEC.md`, `docs/CANONICAL_EMBEDDED_ARTIFACT_v0.md`, `docs/HEADER8_STREAM_v0.md`

## Purpose

Formalize algorithm-first tool partitioning for the 112-role matrix:

- 8 role governors (Q1..Q8)
- 7 lane agents per role
- 2 proof assistants per lane

Formula: `8 x 7 x 2 = 112`

## Algorithm Families (Basis)

1. `carrier`
2. `header8`
3. `escape_control`
4. `chirality_fano`
5. `a14_scheduling`
6. `proposal_receipt`
7. `activation_projection`

Toolsets are derived from this law stack; tools are not the basis.

## MCP Surface Rule

- Bounded MCP tools only.
- Proposal-first mutation boundaries preserved.
- Projection tools remain advisory and non-authoritative.

The machine-readable matrix is:

- `narrative_data/contracts/role_toolset_matrix_112.v0.json`

Schema:

- `docs/schemas/role_toolset_matrix_112.v0.schema.json`

## Role Mapping

- `metatron` -> Q1
- `enoch` -> Q2
- `solomon` -> Q3
- `solon` -> Q4
- `asabiyah` -> Q5
- `writer` -> Q6
- `reader` -> Q7
- `composer` -> Q8

## Priority Bands

- `critical`: Q1, Q3, Q5, Q6, Q7
- `important`: Q2, Q4
- `expansive`: Q8

## Determinism

The matrix is generated from `agent_matrix_112.v0.json` and must be byte-stable for the same inputs.

Build/verify:

- `python3 tools/build_role_toolset_matrix_v0.py --write`
- `python3 tools/build_role_toolset_matrix_v0.py --verify`
