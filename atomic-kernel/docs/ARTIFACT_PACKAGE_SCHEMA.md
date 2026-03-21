# ARTIFACT_PACKAGE_SCHEMA.md
## Canonical Artifact Carrier Package v1

`artifact_package.v1` is the canonical transport wrapper for sharing artifacts.
It is a carrier format, not source-of-truth law.

## Normative Fields

Required fields:

- `type`: must be `"artifact_package"`
- `version`: must be `1`
- `artifact_kind`: one of:
  - `projection_package`
  - `semantic_graph_artifact`
  - `progression_template`
  - `control_diagram_artifact`
  - `header8_artifact`
  - `canonical_embedded_artifact`
  - `artifact_activation_receipt`
  - `artifact_projection_view`
  - `artifact_projection_manifest`
- `payload_encoding`: must be `"utf8-json"`
- `payload_b64`: base64 of canonical UTF-8 JSON payload bytes
- `fingerprint_algo`: must be `"sha256"`
- `fingerprint`: `sha256:<hex>` of decoded payload bytes

Optional fields:

- `created_at`: ISO timestamp string

## Verification Law

A compliant implementation SHALL:

1. decode carrier bytes,
2. parse JSON package,
3. validate required fields and allowed `artifact_kind`,
4. decode `payload_b64`,
5. recompute `sha256` over payload bytes,
6. compare with `fingerprint`,
7. apply payload only if all checks pass.

Unknown `artifact_kind`, malformed payload, or fingerprint mismatch MUST fail closed.

## Canonical Payload Encoding

Payload bytes are produced from canonical JSON serialization (`sort_keys=true`, compact separators) encoded as UTF-8.

## Carrier Mapping

Approved carrier projection in runtime:

```text
canonical payload
→ artifact_package.v1
→ Aztec code
→ lossless PNG carrier
→ decode
→ verify
→ apply if valid
```

PNG/Aztec are transport projections only. The canonical artifact payload remains authoritative.
