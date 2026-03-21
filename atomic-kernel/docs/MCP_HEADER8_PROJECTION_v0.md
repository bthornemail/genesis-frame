# MCP -> Header8 Projection v0

Status: Advisory Draft
Authority: Advisory projection contract
Depends on: `docs/HEADER8_STREAM_v0.md`, `docs/WITNESS_PLANE_SPEC.md`

## Purpose

Define deterministic projection from MCP request/receipt payloads to `header8_stream.v0` for audit/replay inspection.

## Scope

Applies to bounded MCP surfaces only. The MCP JSON-RPC contract remains primary authority.

## Projection Rules

- Request projection:
  - `GS` request envelope
  - `RS` method section
  - `US` key/value units for arguments
- Receipt projection:
  - `GS` receipt envelope
  - `RS` decision/status section
  - `US` lineage fields (`proposal_id`, `receipt_id`, `tick`, `decision`)

## Constraints

- Proposal/receipt boundary must remain explicit
- Projection cannot mark a proposal accepted
- Projection cannot mutate canonical state
- Deterministic serialization required for digest stability

## Output Contract

Output artifact shape:

- `v: "header8_stream.v0"`
- `authority: "advisory"`
- `source_kind: "mcp_rpc"`
- deterministic unit sequence + digest
