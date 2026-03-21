# Publish Immediate Use

This is the shortest path to launch Genesis Frame for immediate presentation/use.

## 0) One-command walkthrough

```bash
./start-walkthrough
```

Optional custom port:

```bash
./start-walkthrough 8080
```

## 1) Verify strict build

```bash
python3 atomic-kernel/tests/test_all.py
```

Expected: `140/140 passed`.

## 2) Serve runtime

```bash
cd atomic-kernel
python3 -m http.server 8000
```

Open:

- `http://localhost:8000/world.html`

## 3) Presentation path (live demo)

1. Start in Story mode.
2. Let canonical autoplay run (show continuity without interaction).
3. Show global strip only: `Mode / Frame / Attention / More`.
4. Enter `Semantic` frame:
   - show `Narrow / Expand / More`.
5. Trigger interrupt interaction:
   - show witness/readout behavior and deferred next-frame commit.
6. Show artifact carrier export/import:
   - export Aztec PNG
   - import Aztec PNG
   - verify-before-apply path
7. Show Header8 artifact import path:
   - `header8_artifact` accepted in carrier allowlist.

## 4) Canonical references during demo

- `atomic-kernel/docs/ESCAPE_ACCESS_LAW.md`
- `atomic-kernel/docs/ALGORITHM_A13_ESC_DEPTH_MIXED_RADIX.md`
- `atomic-kernel/docs/HEADER8_CANONICAL_ALGORITHM.md`
- `atomic-kernel/docs/WITNESS_PLANE_SPEC.md`
- `atomic-kernel/docs/112_PROOFS_MATRIX.md`

## 5) Release statement

Atomic Kernel / Genesis Frame is ready for immediate use with deterministic replay, bounded interrupt law, first-class artifact carriers (including Header8), and executable proof lanes backing incidence and reconciliation behavior.

## 6) Presenter script

Use:

- `LIVE_DEMO_TALK_TRACK.md`
