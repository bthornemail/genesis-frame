# Atomic Kernel

A deterministic timing and identity substrate.
Everything in the world observes the crystal. Nothing adds to it.

Mission:

> Build a navigable artifact map so collaborators can co-create worlds that evolve independently yet interoperate at any shared replay step in time.

## What this is

A CPU crystal doesn't compute anything — it oscillates and everything
else uses it as a reference. This is that crystal, in software.

From that one crystal, every object in the world gets:
- a **position** in time (orbit + offset)
- a **stable identity** (SID — what it is, forever)
- an **unforgeable occurrence chain** (OID — when it happened)

No wall-clock time. No random numbers. No network needed.
Same seed + same tick = identical output on any machine, always.

## Decentralized Collaboration Bridge

Decentralized collaboration in this system means:

- no central authority required to declare truth,
- truth anchored in canonical, replay-verifiable artifacts,
- contributors can join at any shared timeline index,
- projections can differ while canonical state law remains shared.

## Files

```
atomic-kernel/
  crystal.py      — the timing law (THE foundation)
  identity.py     — CLOCK + SID + OID (deterministic identity)
  observer.py     — one object reading the crystal
  world.py        — 16 observers sharing one crystal
  incidence_projection.py — deterministic Fano-triplet projection law
  world.html      — open in any browser, no server needed
  tests/
    test_all.py   — run this to verify everything works
  README.md       — this file
```

## Run it

```bash
# Verify everything works (kernel + transport + runtime + narrative pipeline)
python3 tests/test_all.py

# Build/rebuild narrative chapter data from markdown corpus
python3 tools/build_narrative_ndjson.py --write
python3 tools/build_narrative_ndjson.py --verify

# Build WordNet 5WN browser index + winkNLP bundle
npm run build:nlp
npm run verify:wordnet

# Open the live world viewer
open world.html          # macOS
xdg-open world.html      # Linux
# or just drag world.html into any browser
```

## World.html modes

- `Story Mode`: playable bootstrap sequence (`boot_cinematic -> hub -> chapter_scene`) with cross-world artifact gates.
- `Editor Mode`: drag/drop artifact toolkit (primitive + city kit components + one-click city presets: starter/downtown/walled/low-rise + starter GLB/SVG + dropped GLB/SVG + remote GLB URL import).
- Save system: 3 slots + autosave + JSON import/export backup.
- Timeline replay: event log scrubber with step/play/pause/rewind and NDJSON export.
- Future workflow is explicit and bounded:
  - `Preview Future` computes forecast projection from current timeline + pending branch events.
  - `Inject Branch` queues typed future-directed events (artifact grant, chapter enter, control codepoint, control basis).
  - `Materialize Fork` preserves queued branch events as `fork_artifact.v1`; mainline canonical replay is unchanged.
- City presets are projection helpers that emit canonical `artifact_emitted` events (`source: city_preset`) and then replay; geometry is rendered from emitted artifacts.
- Webhook lanes: outbound event POST + inbound JSON polling for bounded proposals.
- Semantic projection: scene triples rendered as in-scene node/edge graph in story mode.
- Semantic artifacts are first-class runtime state: saved/exported, event-logged (`semantic_graph_materialized`), replay-rebuilt, and inspectable in the Semantic frame.
- Projection sharing: export/import/copy projection packages (JSON) including frame, control-plane state, semantic artifact, and scene layout.
- Aztec carrier sharing: projection packages can be wrapped as `artifact_package.v1` and exported/imported as Aztec-encoded lossless PNG carriers (no extra optimization pass) with fingerprint verification.
- Allowed carrier `artifact_kind` values are explicit and fail-closed:
  - `projection_package`
  - `semantic_graph_artifact`
  - `progression_template`
  - `control_diagram_artifact`
- Canonical package schema: `docs/ARTIFACT_PACKAGE_SCHEMA.md`.
- Control-plane UML/XML builder: XML-style or line-style node/edge specs extruded into 3D control-plane geometry.
- Recursive 4-plane node GUI: every selected artifact is projected through exactly `FS`/`GS`/`RS`/`US`.
- Frame pairing law: active reference frame is `frame = (plane, basis)`.
- Plane meanings are fixed:
  - `FS` context/frame
  - `GS` grouping/relations
  - `RS` single selected record (identity view)
  - `US` units (properties/actions)
- Basis selector is bounded and projection-only: `2`, `10`, `16`, `codepoint`, `mixed`.
- Basis is algorithmic via explicit `basis_spec` artifacts (shareable in projection packages).
- Canonical pair: `project(value, plane, basis_spec)` / `interpret(representation, plane, basis_spec)`.
- Basis proof checks are part of the test suite: canonicalization stability and reversibility for default specs.
- Incidence projection checks are part of the test suite: deterministic Fano triplet schedule + collapse/divergence continuation surface.
- Recursion rule: selecting an item inside any plane re-selects that artifact and recomputes the same four planes.
- Global plane rail in stage header keeps FS/GS/RS/US switching available even in simple mode.
- Panel convergence (same law across tools):
  - `FS`: mode/saves, timeline replay, webhook lanes
  - `GS`: artifact catalog, navigator graph, semantic/template registry
  - `RS`: control-plane record editors (UML/XML + frame controls)
  - `US`: transform/snap/layout unit actions
- Scene-first onboarding: starts with scene visible and toolbox collapsed; core menus are in-world 3D artifacts (`Toolbox`, `Mode`, `Frame`, `Cycle`) with live cycle label.
- Menu ring is configurable from spec (XML or line mode) and rendered as in-world 3D menu nodes.
- NLP bridge: winkNLP + WordNet 5WN Prolog-derived noun index (`nlp/wordnet_5wn_index.json`) for person/place/thing extraction and SPO hints.
- Frame switcher (projection-only): `World`, `Control`, `Codepoint`, `Aztec`, `Semantic`, `Replay` views over the same canonical state.
- Semantic schema doc: `docs/SEMANTIC_GRAPH_SCHEMA.md` (node kinds, edge kinds, transitions, runtime artifact shape).
- Narrative build emits semantic records per scene: `semantic_node`, `semantic_edge`, `semantic_transition`.
- Character progression templates are artifact-encoded and reusable: `narrative_data/templates/character_progression_templates.json`.
- Companion diagram doc: `docs/CHARACTER_PROGRESSION_TEMPLATES.md`.
- Runtime template picker can instantiate one template into Semantic, Control/UML, and World projections.
- Templates are first-class share units: import/export JSON and clone as projection package.
- Debug API in browser console:
  - `startNewGame(slot)`
  - `loadGame(slot)`
  - `saveGame(slot)`
  - `jumpToChapter(chapterId)`
  - `grantArtifact(artifactId)`
  - `jumpToEvent(index)`
  - `exportEventLog()`
  - `previewFuture(horizon)`
  - `injectFuture(kind, value)`
  - `clearFutureBranch()`
  - `acceptFutureBranch()` (alias of fork materialization)
  - `materializeFutureFork()`
  - `listForkArtifacts()`
  - `loadForkIntoBranch(forkId)`
  - `exportSemanticGraph()`
  - `registerDocument(documentId, text, source='uploaded')`
  - `listDocuments()`
  - `analyzeDocument(request)`
  - `exportProjection()`
  - `importProjection(pkg)`
  - `exportArtifactPackage(artifactKind, payload?)`
  - `verifyArtifactPackage(pkg)`
  - `listProgressionTemplates()`
  - `instantiateTemplate(id, opts)`
  - `importTemplate(rawOrObj)`
  - `exportTemplate(id)`
  - `cloneTemplateAsProjection(id)`
  - `projectArtifact(idOrNode, plane)`
  - `setUIPlaneTab(plane)`
  - `setUIBasis(basis)`
  - `listBasisSpecs()`
  - `registerBasisSpec(spec)`
  - `projectValue(value, plane, basisSpecId?)`
  - `interpretValue(representation, plane, basisSpecId?)`
  - `setPlaySpeed(speed)`
  - `setUIFrame(frame)`

## Truth boundary

Not every generated output is authoritative.

An artifact is authoritative only if it is canonicalized, deterministic for identical inputs, replay-reconstructible, and independently verifiable.

Practical split:
- Foundational: kernel law, bounded control/escape law, canonical artifacts.
- Projection/advisory: frame visuals, NLP extraction, WordNet typing, transient scene objects.

Formal reduction spec:
- HTML formal view: `docs/formal_spec.html`
- Pure algorithms (single-file minimal form): `dev-docs/PURE_ALGORITHMS.md`
- Normative core: `dev-docs/ATOMIC_KERNEL_NORMATIVE_CORE_v1_2.md`
- Proof notes: `dev-docs/ATOMIC_KERNEL_PROOF_NOTES_v1_2.md`
- Combined draft: `dev-docs/ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md`
- Law/code traceability: `dev-docs/LAW_TO_CODE_TRACEABILITY.md`

Recommended reading path:
- Read the Normative Core first, then the Proof Notes, then the Combined Draft only if full derivational context is needed.

## The algorithm

```
crystal tick n
    → state    = oscillate(seed XOR B[n%8])   — where in the cycle
    → position = cumsum(B)[n]                  — how far from origin
    → orbit    = position // 36               — coarse time (minute hand)
    → offset   = position %  36               — fine time   (second hand)

identity
    → CLOCK = "orbit.phase.offset"            — when, in crystal time
    → SID   = sha256("world.object:0xSEED")   — what this object is
    → OID   = sha256(clock:sid:prev_oid)      — this specific occurrence

observer
    → reads (state, orbit, offset) from crystal
    → derives (x, y, color, symbol) for the world
    → has SID + OID chain for identity

world
    → 16 observers, same crystal, same tick
    → frame(n) is identical on every machine
    → frame(n) can be computed without running 0..n-1
```

## Why it works

The block B = [0,1,3,6,9,8,6,3] comes from 1/73.
73 is the smallest prime whose decimal repeats every 8 digits.
The generator has period 8 — so 73 is forced by the math, not chosen.
sum(B) = 36, which is the orbit weight for position recovery.

The OID chain cannot be forged: changing any occurrence breaks
every OID that follows it. Any observer can verify any claim
by recomputing the chain from scratch.

## Requirements

Python 3.8+, standard library only. No dependencies.
The browser viewer needs no server — just open world.html.
