# Canonical Embedded Artifact v0

Status: Normative Draft
Authority: Canonical carrier law
Depends on: `docs/ARTIFACT_PACKAGE_SCHEMA.md`, `docs/AZTEC_ARTIFACT_SPEC.md`, `docs/WITNESS_PLANE_SPEC.md`

## Purpose

Define the dormant canonical artifact state as an uncompressed Aztec-embedded artifact carrier.

## Core Principle

The canonical artifact is the uncompressed Aztec-encoded embedded artifact in its inactive (dormant) state.
All runtime views are downstream activations/projections and carry no independent authority.

## Dormant State Requirements

A dormant canonical artifact MUST be:

- encoded via `artifact_package.v1`
- uncompressed at canonical payload level
- fingerprinted (`sha256`) over canonical payload bytes
- representable through an Aztec symbol projection
- immutable in meaning under lossless carrier transforms

## Canonical Layering

1. Canonical payload bytes (authoritative)
2. `artifact_package.v1` carrier (authoritative transport wrapper)
3. Aztec symbol projection (derived)
4. PNG/image rendering of Aztec (derived)

Authority does not move from layer 1/2 to layer 3/4.

## Invariants

1. Carrier decode + fingerprint verify MUST succeed before activation.
2. Re-encoding same canonical payload MUST reproduce identical canonical fingerprint.
3. Destroying/changing a projection MUST NOT mutate canonical artifact bytes.
4. Multiple projections MAY coexist for one canonical artifact without creating multiple canonical truths.

## Artifact Kind

`canonical_embedded_artifact.v0` payload fields:

- `type`: `canonical_embedded_artifact`
- `version`: `0`
- `authority`: `canonical`
- `carrier`: `artifact_package.v1`
- `transport_projection`: `aztec_png` (or equivalent lossless Aztec rendering)
- `fingerprint`: `sha256:<hex>`
- `dormant`: `true`

## Boundary

This specification defines canonical dormant state only.
Activation and local rendering are governed by:

- `docs/ARTIFACT_ACTIVATION_LAW_v0.md`
- `docs/ARTIFACT_PROJECTION_VIEW_v0.md`
