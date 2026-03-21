# Artifact Projection View v0

Status: Normative Draft
Authority: Projection contract
Depends on: `docs/CANONICAL_EMBEDDED_ARTIFACT_v0.md`, `docs/ARTIFACT_ACTIVATION_LAW_v0.md`, `docs/ATOMIC_PROJECTION_LAW.md`

## Purpose

Standardize derived local views rendered from canonical dormant artifacts.

## View Model

A projection view is a deterministic, non-authoritative rendering descriptor:

- source: canonical artifact fingerprint
- target: `3d|2d|workflow|graph|document|minimap|stream`
- loader: implementation ID/version
- local context: camera/frame/layout/runtime params
- output descriptor: addresses/instance IDs/runtime handles

## Projection Artifact Type

`artifact_projection_view.v0` fields:

- `type`: `artifact_projection_view`
- `version`: `0`
- `authority`: `advisory`
- `source_fingerprint`: `sha256:<hex>`
- `projection_target`: enum target
- `loader_id`: string
- `context_hash`: `<hex>`
- `output_descriptor`: object
- `replay_hash`: `<hex>`

## Non-Authority Rule

Projection views MUST NOT be treated as canonical truth.
Changing/deleting a projection view MUST NOT alter source artifact canonical bytes.

## Coexistence Rule

Multiple projection views MAY coexist for one source fingerprint.
They represent different local interpretations of the same canonical carrier.

## Determinism Scope

Determinism is required for the projection descriptor contract.
Pixel-perfect identity is optional unless a stricter renderer policy is declared.
