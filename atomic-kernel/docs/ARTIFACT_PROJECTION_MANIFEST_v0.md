# Artifact Projection Manifest v0

Status: Normative Draft
Authority: Projection policy contract
Depends on: `docs/ARTIFACT_PROJECTION_VIEW_v0.md`, `docs/DOCS_POLICY.md`

## Purpose

Declare allowed projection targets, loaders, and policy bounds for artifact activation.

## Manifest Type

`artifact_projection_manifest.v0` includes:

- `manifest_id`
- `version`
- `authority` (`advisory` by default)
- `allowed_targets`
- `loaders`
- `allowlist_policy`
- `resource_bounds`
- `attribution_policy`

## Policy Rules

1. Unknown target/loader => reject.
2. Non-allowlisted assets on public nodes => reject or fallback per explicit policy.
3. Attribution-required assets must surface attribution metadata in projections.
4. Resource bounds must be explicit and enforceable.

## Example Targets

- `3d_scene`
- `2d_canvas`
- `workflow_editor`
- `graph_view`
- `document_view`
- `minimap`
