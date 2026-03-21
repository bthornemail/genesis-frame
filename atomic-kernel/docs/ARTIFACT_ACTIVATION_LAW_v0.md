# Artifact Activation Law v0

Status: Normative Draft
Authority: Activation boundary law
Depends on: `docs/CANONICAL_EMBEDDED_ARTIFACT_v0.md`, `docs/WITNESS_PLANE_SPEC.md`, `docs/ESCAPE_ACCESS_LAW.md`

## Purpose

Define bounded activation from dormant canonical carrier to local runtime form.

## Activation Equation

```text
canonical artifact
+ activation contract
+ local projection context
= local activated projection
```

This is a merge of carrier + interpreter + context, not a merge of authorities.

## Activation Preconditions

Before activation, runtime MUST verify:

1. carrier schema validity
2. fingerprint validity
3. allowed artifact kind
4. allowlisted loader/projection target
5. bounded resource policy

Any failure MUST reject activation (fail-closed).

## Proposal Boundary

Activation requests are proposal-first in governed environments:

- request -> proposal artifact
- acceptance -> receipt artifact
- apply at lawful boundary

Direct canonical mutation through activation UI is forbidden.

## Activation Result Types

Activation MAY yield:

- 3D scene instance
- 2D canvas node/graph element
- workflow template block
- document/minimap projection
- agent-readable stream

All outputs are advisory projections unless explicitly promoted by governance.

## Required Receipt

Each accepted activation emits `artifact_activation_receipt.v0` with:

- `activation_id`
- `artifact_fingerprint`
- `projection_target`
- `loader_id`
- `decision` (`accepted|rejected`)
- `tick` / boundary reference
- `replay_hash`

## Invariants

1. Same artifact + same activation contract + same context => deterministic output descriptor.
2. Rejection must preserve dormant canonical state unchanged.
3. Activation scope is bounded; no implicit persistent side effects.
4. Accepted activation must be traceable to receipt.
