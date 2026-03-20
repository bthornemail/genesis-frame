# Genesis Frame

**Genesis Frame** is the first public frame of the Atomic Kernel: a playable narrative world, artifact toolkit, and deterministic substrate packaged as a starting environment people can open, explore, test, and build on.

Mission:

> We build a navigable artifact map so collaborators can co-create worlds that evolve independently yet interoperate at any shared replay step in time.

This repository is a framed distribution built from my `atomic-kernel` work and expanded into a usable entrypoint for others. It combines:

- a deterministic replay/kernel layer
- a control-plane and artifact model
- a Three.js world interface
- a narrative chapter system compiled from markdown into NDJSON
- local save slots, editor mode, and story mode in one page

## Decentralized Collaboration Bridge

The bridge this repository provides is:

- shared law (kernel + bounded control law),
- independent local artifact creation,
- independent replay verification,
- shareable projection/artifact packages,
- interoperability at any shared deterministic timeline index.

---

## What this is

Genesis Frame is meant to be a **starting frame for use**.

It is not only a code library and not only a narrative site. It is a combined environment where:

- the **Atomic Kernel** provides deterministic logic and replay
- the **artifact/toolkit layer** lets users place and manipulate objects in a world
- the **story layer** turns a markdown corpus into traversable chapter-scenes with choices, inventory, and gates
- the **hub world** lets players move across chapters as a world-map structure

The current build centers on the narrative series:

**When Wisdom, Law, and the Tribe Sat Down Together**

with a cinematic prologue, hub progression, article worlds, and epilogue routing.

---

## Repository structure

```text
genesis-frame/
├── atomic-kernel/      # deterministic runtime, world page, tests, narrative bundle
└── narrative-series/   # markdown source corpus compiled into chapter data
````

Important paths:

* `atomic-kernel/world.html` — main interactive page
* `atomic-kernel/tools/build_narrative_ndjson.py` — markdown → NDJSON compiler
* `atomic-kernel/narrative_data/` — generated runtime narrative data
* `atomic-kernel/tests/test_all.py` — full validation suite
* `narrative-series/When Wisdom, Law, and the Tribe Sat Down Together/` — source text corpus

---

## Features

### Story Mode

* cinematic boot sequence
* world hub with chapter unlocking
* in-scene clickable 3D hub graph
* full-text chapter scenes with choices
* cross-world artifact inventory
* codex view of traversed scenes
* local save slots + autosave

### Editor Mode

* drag/drop artifact placement
* primitive, GLB, and SVG starter artifacts
* dropped GLB/SVG support
* transform controls for move / rotate / scale
* layout save/load JSON

### Projection Sharing

* export/import shareable projection packages (JSON)
* package includes UI frame, control-plane state, semantic artifact, and scene layout
* clipboard copy for quick sharing between users
* Aztec PNG carrier mode (`artifact_package.v1`) for share/packing transport with payload fingerprint verification
* explicit allowed package kinds with fail-closed import; schema documented in `atomic-kernel/docs/ARTIFACT_PACKAGE_SCHEMA.md`

### Recursive Node GUI

* unified node model across frames (`id`, `kind`, `properties`, `children`, `relations`, `actions`)
* navigator pane + 4 canonical projection planes: `FS` / `GS` / `RS` / `US`
* frame pairing law: `frame = (plane, basis)`
* fixed plane law:
  * `FS` = context/frame
  * `GS` = grouping/relations
  * `RS` = single selected artifact record
  * `US` = atomic units (properties/actions)
* bounded basis selector: `2`, `10`, `16`, `codepoint`, `mixed`
* basis interpretation is explicit and shareable via `basis_spec` artifacts
* canonical transform pair: `project(value, plane, basis_spec)` and `interpret(representation, plane, basis_spec)`
* test suite now enforces basis-spec canonicalization stability + projection/interpret reversibility
* recursive navigation: selecting any plane item promotes it to the next selected artifact and recomputes FS/GS/RS/US
* global plane rail in stage header keeps plane switching available in both simple and advanced UI
* side tools converge to same planes:
  * `FS` mode/saves/timeline/webhooks
  * `GS` artifact/template/document grouping + semantic registry
  * `RS` record builders/editors (control/UML)
  * `US` transform/snap/layout unit operations
* same command grammar on selected nodes: open / project / link / emit / share / replay

### Control-Plane UML/XML Builder

* control-plane panel accepts XML-style or line-style diagram specs
* node/edge specs are extruded into 3D control-plane geometry
* render/clear actions are replay-compatible via control-plane events

### Scene-First Onboarding

* starts in scene-first mode (toolbox collapsed)
* 3D menu artifacts in-world: Toolbox / Mode / Frame / Cycle
* cycle label updates from replay timeline and current phase
* menu ring is data-driven via XML/line spec and can be shared in projection packages

### Narrative Build Pipeline

* reads markdown corpus from `narrative-series/...`
* compiles chapters into **NDJSON**
* emits a hub manifest and browser bundle
* deterministic IDs derived from source path + heading slug for save stability

### Deterministic Substrate

* kernel replay and parity validation
* control-plane encoding tests
* artifact and geometry fixtures
* Python / JavaScript parity checks

---

## Narrative runtime format

The canonical runtime narrative format is **NDJSON**.

Record types include:

* `chapter_meta`
* `scene`
* `choice`
* `artifact`
* `gate`
* `semantic_node`
* `semantic_edge`
* `semantic_transition`

This allows the markdown corpus to compile into a stable runtime representation while keeping the original prose corpus readable and editable.

Character progression diagram templates (artifact-encoded) are provided at:

- `atomic-kernel/narrative_data/templates/character_progression_templates.json`
- `atomic-kernel/docs/CHARACTER_PROGRESSION_TEMPLATES.md`

Runtime can instantiate these templates directly into:
- Semantic frame (graph artifact),
- Control frame (UML/control diagram spec),
- World frame (spawned template node artifacts).

---

## Truth boundary

The repository does **not** treat every generated output as truth.

An artifact is authoritative only if it is:

* canonicalized
* deterministic for identical inputs
* replay-reconstructible
* independently verifiable

Practical split:

* **Foundational:** kernel law, bounded control/escape law, canonical artifacts
* **Projection/advisory:** UI frames, NLP extraction, WordNet typing, transient visuals

Normative sentence:

> An artifact is authoritative only if it is canonicalized, deterministic, replay-reconstructible, and independently verifiable; all other representations are projections.

Formal reduction spec:
- Normative core: `atomic-kernel/dev-docs/ATOMIC_KERNEL_NORMATIVE_CORE_v1_2.md`
- Proof notes: `atomic-kernel/dev-docs/ATOMIC_KERNEL_PROOF_NOTES_v1_2.md`
- Combined draft: `atomic-kernel/dev-docs/ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md`
- Law/code traceability: `atomic-kernel/dev-docs/LAW_TO_CODE_TRACEABILITY.md`

Recommended reading path:
- Read the Normative Core first, then the Proof Notes, then the Combined Draft only if full derivational context is needed.

---

## Running it

### 1. Clone the repo

```bash
git clone https://github.com/bthornemail/genesis-frame.git
cd genesis-frame
```

### 2. Build or rebuild the narrative data

```bash
python3 atomic-kernel/tools/build_narrative_ndjson.py --write
python3 atomic-kernel/tools/build_narrative_ndjson.py --verify
```

### 3. Run the test suite

```bash
python3 atomic-kernel/tests/test_all.py
```

### 4. Open the world page

Open:

```text
atomic-kernel/world.html
```

For best results, serve the repo through a local static server instead of opening the file directly in a browser.

Example:

```bash
cd atomic-kernel
python3 -m http.server 8000
```

Then visit:

```text
http://localhost:8000/world.html
```

---

## Save system

Genesis Frame includes:

* 3 manual save slots
* autosave
* save export to JSON
* save import from JSON

The save schema includes:

* `version`
* `current_phase`
* `current_chapter`
* `current_scene_id`
* `inventory[]`
* `unlocked_chapters[]`
* `seen_scenes[]`
* `choice_history[]`
* optional scene `layout`
* `event_log[]` and `timeline_index`
* `ui_frame` and `ui_subframe`
* `semantic_graph_artifact` and `semantic_artifact_meta`

---

## Browser debug API

The page exposes a small runtime API for testing and debugging:

```js
startNewGame(slot)
loadGame(slot)
saveGame(slot)
jumpToChapter(chapterId)
grantArtifact(artifactId)
jumpToEvent(index)
exportEventLog()
exportSemanticGraph()
registerDocument(documentId, text, source)
listDocuments()
analyzeDocument(request)
exportProjection()
importProjection(pkg)
exportArtifactPackage(artifactKind, payload?)
verifyArtifactPackage(pkg)
listProgressionTemplates()
instantiateTemplate(id, opts)
importTemplate(rawOrObj)
exportTemplate(id)
cloneTemplateAsProjection(id)
projectArtifact(idOrNode, plane)
setUIPlaneTab(plane)
setUIBasis(basis)
listBasisSpecs()
registerBasisSpec(spec)
projectValue(value, plane, basisSpecId?)
interpretValue(representation, plane, basisSpecId?)
setPlaySpeed(speed)
setUIFrame(frame)
```

---

## Validation

The current test lane validates both the deterministic kernel and the narrative pipeline, including:

* deterministic replay invariants
* control-plane roundtrips
* artifact/reference fixtures
* geometry tables
* JS parity vectors
* narrative build verification
* chapter coverage from markdown source
* runtime schema coverage
* deterministic ID stability checks

---

## Design intent

Genesis Frame exists because I wanted a first frame people could actually use.

The Atomic Kernel began as a law-first, deterministic substrate. But for people to enter it, there needed to be a **worlded interface**: something navigable, visual, textual, and playable.

This repo is that first frame.

It is a bridge between:

* formal substrate and public use
* deterministic law and narrative traversal
* artifact manipulation and chapter progression
* source markdown and runtime world state

---

## Status

Current status:

* deterministic kernel integrated
* narrative compiler integrated
* Three.js story/editor world integrated
* clickable 3D hub graph integrated
* tests passing

This is a working public frame, not a final endpoint.

---

## Source lineage

This repository was framed from my Atomic Kernel work and expanded into a standalone starting environment.

Primary upstream work:

* `bthornemail/atomic-kernel`

This repo:

* packages that work into a usable public frame
* includes the narrative corpus and generated runtime artifacts
* presents the project as a world people can enter instead of only a specification they can read

---

## License

Add the license you want for this repository here.

For example:

```text
MIT
```

or

```text
Apache-2.0
```

or a custom project license if this frame is meant to have different publishing terms.

---

## Author

**Brian Thorne**

Genesis Frame is the first starting frame for public use of the Atomic Kernel world, narrative, and artifact system.
