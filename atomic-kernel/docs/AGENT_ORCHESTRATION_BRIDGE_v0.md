# Agent Orchestration Bridge v0

Status: Normative Draft  
Authority: Algorithms First / Tools Second

## Purpose

Define a bounded bridge for external agent providers (`openclaw`, `opencode`, `ollama`) to participate in the capability kernel without crossing authority boundaries.

## Boundary

External providers are advisory participants only.

- Canonical truth is not mutated by this bridge.
- All outputs are proposal artifacts.
- Canonical mutation remains proposal+receipt gated by lawful acceptance flows.

## Provider Classes

Allowed provider identifiers:

- `mock`
- `ollama`
- `opencode`
- `openclaw_adapter`

Unknown providers MUST reject fail-closed.

## Output Contract

Bridge output is `agent_action_proposal.v0`.

Mandatory constraints:

- `authority` MUST be `advisory`
- `mutation_boundary` MUST be `proposal_only`
- `canonical_tick` MUST be explicit
- `proposal_id` MUST be deterministic from stable inputs
- `receipt_stub.accepted` MUST be `false`

## Determinism

Determinism is guaranteed in `mock` mode.

External providers may be non-deterministic, but bridge framing must remain deterministic:

- stable envelope keys
- stable digest rules
- fail-closed validation

## MCP Position

This bridge is suitable for MCP exposure as a bounded toolset once contract checks are in place:

- request in
- proposal artifact out
- no direct canonical commit

## Security / Trust

The bridge does not add a new authority layer.

- provider output is untrusted input
- proposal envelope is validated
- malformed payloads reject
- acceptance remains outside bridge scope
