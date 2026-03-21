# Changelog

## v1.3 - 2026-03-21

### Asset-pack runtime reliability
- hardened import manifest loader with deterministic fallback path resolution:
  - `/assets/imports/asset-manifest.json`
  - `./assets/imports/asset-manifest.json`
  - `/docs/imports/asset-manifest.json`
  - `./docs/imports/asset-manifest.json`
  - `../docs/imports/asset-manifest.json`
- startup scene now reports manifest source + loaded count via status channel
- retained fail-closed behavior when no manifest is available (built-in fallback assets only)

### Story gate diagnostics
- improved `Chapter Gate Blocked` output to include per-artifact unlock guidance
- added chapter-source lookup for missing artifact IDs based on chapter artifact/scene/choice grant records
- no authority model change; gating semantics remain deterministic and requirement-driven

## v1.2 - 2026-03-20

### Release readiness (immediate use)
- full strict suite green: `140/140` (`python3 atomic-kernel/tests/test_all.py`)
- A13 ESC-depth mixed-radix header wired and verified
- Header8 canonical algorithm added as first-class artifact
- runtime and schema aligned to accept `header8_artifact` carriers
- incidence collapse/divergence deterministic proof lane added
- deterministic past/present/future reconciliation proof lane added
- witness role model finalized (5 canonical roles, 3 operational agents)

### Presentation completion
- publish checklist added at repo root: `PUBLISH_IMMEDIATE_USE.md`
- one-command walkthrough launcher added: `./start-walkthrough`
- public release text added: `RELEASE_ANNOUNCEMENT.md`
- root `README.md` updated with current verified lane and publish path

## v1.1 - 2026-03-20

### Law and spec alignment
- froze pure-algorithm framing (seven core laws with eleven decomposed procedures)
- aligned normative core, proof notes, and combined reduction draft reading path
- clarified law vs witness boundary across docs and formal HTML summary
- added law-to-code traceability references in root documentation

### Runtime and verification
- full suite green: `113/113` (`python3 atomic-kernel/tests/test_all.py`)
- basis law formalized with canonicalization and reversibility checks
- incidence projection module integrated and validated
- carrier verification path aligned with allowed package-kind fail-closed behavior
- fork artifact workflow integrated for branch preservation

### UI convergence (attention-first)
- global strip refactor: always-visible `Mode / Frame / Attention`
- semantic panel reduced to minimal control model (`Narrow / Expand / More`)
- stage and sidebar now follow the same `More/Less` collapse rule
- scene-first path preserved while advanced tooling remains accessible on expand
- strict UI checks validated reachable controls and collapse behavior

### Sharing and transport
- projection package export/import stabilized
- fork artifact packing and replay path stabilized
- Aztec PNG carrier path retained with verification-before-apply boundary

### World/editor path
- city presets available in scene workflow
- remote GLB URL import path enabled
- camera framing and scene-first defaults improved
