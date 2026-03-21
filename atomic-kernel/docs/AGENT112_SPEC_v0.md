# Agent112 Spec v0

Status: Advisory (operational stewardship surface)
Authority: Advisory
Depends on: `docs/112_PROOFS_MATRIX.md`, `docs/WITNESS_PLANE_SPEC.md`, `docs/PURE_ALGORITHMS.md`

## Purpose

Define 112 bounded steward agents mapped 1:1 to the 112 proof-cell obligations.

Model:
- 8 invariant questions
- 7 algorithm families
- 2 proof forms (constructive, falsification)
- total: 112 proof cells

Each steward agent maintains one proof cell. Agents never become authority.

## Core Rule

Proof matrix is canonical structure.
Agents are operational maintainers of proof obligations.

## Naming Convention

- Cell id: `Q{q}_A{a}_{proof}`
  - example: `Q4_A3_constructive`
- Agent id: `agent_{cell_id}`
  - example: `agent_Q4_A3_constructive`
- Role/lane/assistant projection ids:
  - role: `metatron|enoch|solomon|solon|asabiyah|writer|reader|composer`
  - lane agent: `{role}.{algorithm_slug}`
  - assistant: `{role}.{algorithm_slug}.{constructive|falsification}`

## Role Mapping (Q1-Q8)

- `Q1` -> `metatron`
- `Q2` -> `enoch`
- `Q3` -> `solomon`
- `Q4` -> `solon`
- `Q5` -> `asabiyah`
- `Q6` -> `writer`
- `Q7` -> `reader`
- `Q8` -> `composer`

Priority bands:
- `critical`: Q1, Q3, Q5, Q6, Q7
- `important`: Q2, Q4
- `expansive`: Q8

## Agent Contract

Each agent entry MUST include:
- `agent_id`
- `cell_id`
- `question_id`
- `algorithm_id`
- `proof_form`
- `expected_invariant`
- `must_reject_conditions`
- `proposal_lane`
- `receipt_lane`

## Allowed Agent Operations

- inspect assigned artifact/state
- run bounded proof check
- emit proposal on violation
- emit receipt
- project status for UI

## Forbidden Agent Operations

- direct write to canonical state
- direct write to canonical event log
- mark proposal as accepted
- bypass frame-boundary commit law

## Runtime Artifact Surfaces

- `narrative_data/agent112/proof_matrix_112.v0.json`
- `narrative_data/agent112/agent_registry_112.v0.json`
- `narrative_data/agent112/agent_matrix_112.v0.json`
- `artifacts/agent112-v0.normalized.json`
- `artifacts/agent112-v0.replay-hash`
- `docs/proofs/agent112-v0.latest.md`

## Determinism

For identical source matrix content, generated proof and agent registries must be byte-stable.

## Authority Boundary

All runtime outputs remain `authority: "advisory"`.
Acceptance/commit remains in witness + frame-boundary governance.
