# tests/test_all.py
#
# Run with: python3 tests/test_all.py
# All tests must pass before you ship anything.

import json
import os
import shutil
import subprocess
import sys
import hashlib
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from artifact import (
    REF_HASH_PATH,
    REF_STREAM_PATH,
    REFERENCE_TICK,
    artifact_hash,
    canonical_stream,
    freeze_reference,
    verify_reference,
)
from aztec_geometry import coordinates_for, validate_coordinate_table
from artifact_package import ALLOWED_ARTIFACT_KINDS, create_artifact_package, verify_artifact_package
from branch_reconciliation import (
    branch_reconciliation_valid,
    materialize_branch_artifact,
    reconcile_temporal_views,
    replay_branch,
    return_to_canonical,
)
from esc_depth import ESC_CODE, count_leading_esc, esc_decode, esc_encode, radices_for_depth, transylvania_coverage_report
from header8 import (
    ESC_AXIS,
    FS_AXIS,
    GS_AXIS,
    INVARIANT_AXES,
    NULL_AXIS,
    RS_AXIS,
    US_AXIS,
    classify_block,
    classify_structural,
    create_header8_artifact,
    interpret_header,
    make_header8,
    pack16,
    unpack16,
)
from basis_spec import (
    basis_spec_fingerprint,
    canonical_basis_spec_json,
    default_basis_specs,
    interpret_value,
    mixed_decode,
    mixed_encode,
    normalize_basis_spec,
    project_value,
)
from control_plane import (
    ControlPlaneError,
    canonical_escape_scope_active,
    cobs_decode,
    cobs_encode,
    encode_control,
    parse_control_stream,
    validate_escape_scope,
)
from crystal import tick, position_at, read, state_at, run, W, T, B, MASK
from incidence_projection import (
    FANO_LINES,
    classify_entity,
    continuation_surface,
    fano_triplet,
    frame_at_tick,
    is_collapsed,
    projection_vector,
    select_continuation,
    step_projection,
)
from identity import clock, sid, sid_for_object, oid_step, ObjectChain, replay_chain, GENESIS_STATE as GENESIS
from kernel import delta, replay, SUPPORTED_WIDTHS, check_parity
from observer import observe, SEEDS
from proposal_receipt import accept_proposal, commit_proposal, defer_proposal
from projection_receipt import multi_projection_receipt, projection_receipt_anchored, projection_receipt_equivalent
from world import frame, trace

PASS = 0
FAIL = 0
repo_root = Path(os.path.dirname(os.path.dirname(__file__))).parent
node = shutil.which("node")


def check(name, condition):
    global PASS, FAIL
    if condition:
        print(f"  ✓ {name}")
        PASS += 1
    else:
        print(f"  ✗ FAIL: {name}")
        FAIL += 1


print("=" * 55)
print("ATOMIC KERNEL — FULL TEST SUITE")
print("=" * 55)

# ── Kernel law (Coq-certified) ────────────────────────────────────
print("\nKernel law (Coq: delta_deterministic, replay_deterministic, replay_len):")
check("supported widths defined",       SUPPORTED_WIDTHS == {16, 32, 64, 128, 256})
check("delta deterministic",            delta(16, 0x0001) == delta(16, 0x0001))
check("delta bounded 16-bit",           delta(16, 0x0001) <= 0xFFFF)
check("replay length = steps",          len(replay(16, 0x0001, 8)) == 8)
check("replay 32-bit length",           len(replay(32, 0x0001, 8)) == 8)
check("replay starts at masked seed",   replay(16, 0x0001, 1)[0] == 0x0001)

# Golden parity vectors — proves this matches the Coq proof exactly
golden = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'golden_parity.json')
check("parity vectors exist",           os.path.exists(golden))
if os.path.exists(golden):
    check("all parity vectors pass",    check_parity(golden))

# width=16 first 4 steps match known Coq output
seq16 = replay(16, 0x0001, 4)
check("16-bit step 0 = 0x0001",         seq16[0] == 0x0001)
check("16-bit step 1 = 0x5D17",         seq16[1] == 0x5D17)
check("16-bit step 2 = 0x98CC",         seq16[2] == 0x98CC)
check("16-bit step 3 = 0xCCD3",         seq16[3] == 0xCCD3)

# ── Crystal ───────────────────────────────────────────────────────
print("\nCrystal:")
check("period T = 8",                   T == 8)
check("orbit weight W = 36",            W == 36)
check("block B sums to 36",             sum(B) == 36)
check("block B length 8",               len(B) == 8)
check("position_at(0) = 0",             position_at(0) == 0)
check("position_at(8) = 36",            position_at(8) == 36)
check("position_at(16) = 72",           position_at(16) == 72)
check("read(36) = (1,0)",               read(36) == (1, 0))
check("read(72) = (2,0)",               read(72) == (2, 0))
check("state bounded",                  all(state_at(1, n) <= MASK for n in range(32)))
check("state_at period=16",             state_at(0x0001, 16) == 0x0001)
check("determinism",                    state_at(0x0001, 100) == state_at(0x0001, 100))

rows = run(0x0001, 8)
check("run returns 8 rows",             len(rows) == 8)
check("run orbit 0 in first spin",      all(r['orbit'] == 0 for r in rows))

# ── Identity ──────────────────────────────────────────────────────
print("\nIdentity:")
c0 = clock(0)
c8 = clock(8)
check("clock(0) frame=0",               c0['frame'] == 0)
check("clock(0) tick=1",                c0['tick'] == 1)
check("clock(8) frame=1",               c8['frame'] == 1)
check("clock string format",            c0['str'] == "0.1.00")
check("clock deterministic",            clock(42)['str'] == clock(42)['str'])

s1 = sid_for_object(0x0001)
s2 = sid_for_object(0xCAFE)
check("SID is sid: prefixed",           s1.startswith("sid:"))
check("SID stable",                     sid_for_object(0x0001) == sid_for_object(0x0001))
check("Different seeds → different SIDs", s1 != s2)

chain = ObjectChain(0x0001)
r0 = chain.step(0)
r8 = chain.step(8)
check("OID is oid: prefixed",           r0['oid'].startswith("oid:"))
check("OID changes each step",          r0['oid'] != r8['oid'])
check("prev chains via state",          r8['prev_state'] == r0['state'])
check("first prev = genesis",           r0['prev_state'] == GENESIS)
check("verify r0",                      chain.verify(r0))
check("verify r8",                      chain.verify(r8))

# Replay produces identical chain
replayed = replay_chain(0x0001, [0, 8])
check("replay OID[0] matches",          replayed[0]['oid'] == r0['oid'])
check("replay OID[1] matches",          replayed[1]['oid'] == r8['oid'])

# ── Observer ──────────────────────────────────────────────────────
print("\nObserver:")
o = observe(0x0001, 0)
check("observe returns seed",           o['seed'] == 0x0001)
check("observe returns hex",            o['hex'] == '0x0001')
check("observe x in [0,63]",            0 <= o['x'] <= 63)
check("observe y >= 0",                 o['y'] >= 0)
check("observe has color",              o['color'].startswith('rgb('))
check("observe has symbol",             len(o['symbol']) == 1)
check("observe deterministic",          observe(0x0001, 42) == observe(0x0001, 42))
check("16 seeds defined",               len(SEEDS) == 16)
check("all seeds unique",               len(set(SEEDS)) == 16)

# ── World ─────────────────────────────────────────────────────────
print("\nWorld:")
f0 = frame(0)
check("frame returns 16 objects",       len(f0) == 16)
check("all objects have orbit",         all('orbit' in o for o in f0))
check("frame deterministic",            frame(42) == frame(42))
check("frame 0 != frame 8",             frame(0) != frame(8))

t0 = trace(0, 4)
check("trace returns 4 frames",         len(t0) == 4)
check("trace frame 0 == frame(0)",      t0[0] == frame(0))
check("trace frame 3 == frame(3)",      t0[3] == frame(3))

# ── Control Plane + Artifacts ────────────────────────────────────
print("\nControl Plane + Artifacts:")
ref_stream = bytes.fromhex("1C0348656C6C6F1D73DEAD1E3BE288821F174A2F1D0F9A")

ctl_default = encode_control("FS", 0, 0)
ctl_numsys = encode_control("US", 1, 1)
ctl_unicode = encode_control("RS", 3, 2, "∂")
ctl_extended = encode_control("GS", 0, 3, 0x9A)
check("encode_control CT=00",           ctl_default == bytes.fromhex("1C03"))
check("encode_control CT=01",           ctl_numsys == bytes.fromhex("1F17"))
check("encode_control CT=10",           ctl_unicode == bytes.fromhex("1E3BE28882"))
check("encode_control CT=11",           ctl_extended == bytes.fromhex("1D0F9A"))

events = parse_control_stream(ref_stream, REFERENCE_TICK)
check("parse_control_stream yields events", len(events) > 0)
check("parse includes unicode event",   any(e.payload_kind == "unicode" for e in events))
check("parse includes extended event",  any(e.payload_kind == "extended" for e in events))
check("canonical_stream roundtrip",     canonical_stream(events) == ref_stream)

cobs_sample = bytes.fromhex("1100220033")
cobs_wire = cobs_encode(cobs_sample)
check("cobs roundtrip",                  cobs_decode(cobs_wire) == cobs_sample)

# Fail-closed assertions
try:
    parse_control_stream(bytes.fromhex("1C00"), REFERENCE_TICK)
    bad_mask = False
except ControlPlaneError as exc:
    bad_mask = exc.code == "INVALID_MASK_MARKER"
check("fail closed invalid mask marker", bad_mask)

try:
    parse_control_stream(bytes.fromhex("1E3BFF"), REFERENCE_TICK)
    bad_utf8 = False
except ControlPlaneError as exc:
    bad_utf8 = exc.code == "CT10_INVALID_UTF8"
check("fail closed invalid CT10 utf8",   bad_utf8)

try:
    parse_control_stream(bytes.fromhex("1D0F9A"), 0)
    bad_ct11 = False
except ControlPlaneError as exc:
    bad_ct11 = exc.code == "CT11_ALGO_MISMATCH"
check("fail closed CT11 mismatch",       bad_ct11)

# 112-proof executable lanes (initial)
# Q5 / Escape / falsification: time-based closure forbidden
try:
    validate_escape_scope("time-based")
    scope_forbidden_ok = False
except ControlPlaneError as exc:
    scope_forbidden_ok = exc.code == "ESC_SCOPE_FORBIDDEN"
check("112 Q5 Escape falsification: time-based scope rejected", scope_forbidden_ok)
scope_local_pause_ok = (
    canonical_escape_scope_active("DATA", 0, projection_paused=False)
    == canonical_escape_scope_active("DATA", 0, projection_paused=True)
)
check("112 Q5 Projection falsification: local pause non-authority", scope_local_pause_ok)

freeze_reference()
check("reference stream frozen",         REF_STREAM_PATH.exists())
check("reference hash frozen",           REF_HASH_PATH.exists())
check("reference fixture verifies",      verify_reference())
check("reference hash matches bytes",    REF_HASH_PATH.read_text().strip() == artifact_hash(REF_STREAM_PATH.read_bytes()))

# ── Admitted invariants in test suite ─────────────────────────────
print("\nAdmitted invariants:")
inv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admitted_invariants.json')
with open(inv_path, 'r', encoding='utf-8') as f:
    inv = json.load(f)

seed = int(inv['seed'], 16)
steps = int(inv['steps'])
seq = replay(16, seed, steps)
states_ok = True
mods_ok = True
for row, state in zip(inv['states'], seq):
    if state != int(row['state'], 16):
        states_ok = False
        break
    if (state % 7) != row['E1'] or (state % 37) != row['E9']:
        mods_ok = False
        break

check("admitted state snapshots match", states_ok)
check("admitted E1/E9 match replay",    mods_ok)

# ── Aztec geometry table tests ────────────────────────────────────
print("\nAztec geometry:")
summary = validate_coordinate_table()
check("60 coordinate entries",           summary['entries'] == 60)
check("60 unique coordinates",           summary['unique_positions'] == 60)
check("coordinates in bounds",           summary['in_bounds'] is True)
check("chebyshev ring matches",          summary['ring_match'] is True)
check("15 lanes per channel",            summary['per_channel_15'] is True)

spot = coordinates_for(3, 15)
check("FS lane15 spot check",            (spot.x, spot.y, spot.r) == (14, 2, 11))

# ── Basis specs: canonicalization + proof roundtrips ─────────────
print("\nBasis specs:")
specs = default_basis_specs()
check("default basis specs non-empty", len(specs) >= 6)
check("basis spec ids unique", len({s.id for s in specs}) == len(specs))
stable_json_ok = True
stable_fp_ok = True
roundtrip_ok = True
mixed_pair_ok = True

samples = [0, 1, 7, 11, 27, 36, 83, 255, 1024, 65535]
for spec in specs:
    try:
        normalized = normalize_basis_spec(spec)
        j1 = canonical_basis_spec_json(normalized)
        j2 = canonical_basis_spec_json(normalized)
        if j1 != j2:
            stable_json_ok = False
        f1 = basis_spec_fingerprint(normalized)
        f2 = basis_spec_fingerprint(normalized)
        if f1 != f2:
            stable_fp_ok = False
        for v in samples:
            p = project_value(v, "RS", normalized)
            out = interpret_value(p["rendered"], "RS", normalized)
            if out != v:
                roundtrip_ok = False
                break
        if normalized.kind == "mixed":
            coords = mixed_encode(83, normalized.radices)
            back = mixed_decode(coords, normalized.radices)
            if back != 83:
                mixed_pair_ok = False
    except Exception:
        stable_json_ok = False
        stable_fp_ok = False
        roundtrip_ok = False
        mixed_pair_ok = False

check("basis canonical JSON stable", stable_json_ok)
check("basis fingerprint stable", stable_fp_ok)
check("project/interpret roundtrip", roundtrip_ok)
check("mixed encode/decode roundtrip", mixed_pair_ok)

# ── Deterministic incidence projection law ────────────────────────
print("\nIncidence projection:")
frame16 = frame_at_tick(16, {"type": "basis_spec", "id": "dec_v1", "kind": "10"})
pv = projection_vector({"entity": "watcher", "seed": 1}, frame16)
surf = continuation_surface({"entity": "watcher", "seed": 1}, frame16)
step_out = step_projection({"entity": "watcher", "seed": 1}, 16, {"type": "basis_spec", "id": "dec_v1", "kind": "10"})
check("fano lines fixed x7", len(FANO_LINES) == 7)
check("fano triplet cycles mod 7", fano_triplet(0) == fano_triplet(7))
check("frame carries deterministic triplet", frame16["triplet"] == fano_triplet(16))
check("projection vector has four planes", len(pv) == 4)
check("projection deterministic same input", pv == projection_vector({"entity": "watcher", "seed": 1}, frame16))
check("collapsed iff all projections equal", is_collapsed(pv) == all(p == pv[0] for p in pv))
check("continuation surface non-empty", len(surf) >= 1)
check("continuation deterministic select", select_continuation(surf, 5) == surf[5 % len(surf)])
check("classification is collapsed or divergent", classify_entity({"entity": "watcher", "seed": 1}, frame16) in {"collapsed", "divergent"})
check("step projection kind valid", step_out["kind"] in {"collapsed", "divergent"})
incidence_resolution_ok = True
entity_inc = {"entity": "watcher", "seed": 1}
pv1 = projection_vector(entity_inc, frame16)
pv2 = projection_vector(entity_inc, frame16)
if pv1 != pv2:
    incidence_resolution_ok = False
klass = classify_entity(entity_inc, frame16)
surf_inc = continuation_surface(entity_inc, frame16)
if klass == "collapsed" and len(surf_inc) != 1:
    incidence_resolution_ok = False
if klass == "divergent" and len(surf_inc) < 2:
    incidence_resolution_ok = False
check("112 Q8 Incidence constructive: deterministic collapse/divergence resolution", incidence_resolution_ok)

# ── Algorithm A13: ESC-depth mixed-radix header ──────────────────
print("\nESC-depth (A13):")
a13_roundtrip_ok = True
for d, v in ((1, 0x42), (2, 0x1B), (3, 12345), (4, 987654)):
    enc = esc_encode(v, d)
    dec = esc_decode(enc)
    if dec["value"] != v or dec["depth"] != d:
        a13_roundtrip_ok = False
        break
check("A13 roundtrip depth 1..4", a13_roundtrip_ok)
check("A13 depth count from ESC prefix", count_leading_esc([ESC_CODE, ESC_CODE, ESC_CODE, 0x10]) == 3)
check("A13 radices depth=3", radices_for_depth(3) == [36, 8])
check("A13 radices depth=4", radices_for_depth(4) == [256, 65536])
cov = transylvania_coverage_report()
check("A13 transylvania tickets = 14", cov["ticket_count"] == 14)
check("A13 NULL only in low set", cov["null_only_low"] is True)
check("A13 active symbol pair coverage", cov["active_pair_coverage"] is True)

# ── Header8 canonical algorithm ───────────────────────────────────
print("\nHeader8 canonical algorithm:")
h = make_header8(0x1B, 0x00)
check(
    "Header8 invariant axes fixed",
    (h.null_axis, h.esc_axis, h.fs_axis, h.gs_axis, h.rs_axis, h.us_axis) == INVARIANT_AXES,
)
check("Header8 axis constants canonical", INVARIANT_AXES == (NULL_AXIS, ESC_AXIS, FS_AXIS, GS_AXIS, RS_AXIS, US_AXIS))
check("Header8 structural ESC", classify_structural(0x1B) == "ESC")
check("Header8 structural payload", classify_structural(0x41) == "PAYLOAD")
check("Header8 block C0", classify_block(0x00) == "C0")
check("Header8 block extension", classify_block(0x80) == "EXTENSION")
check("Header8 block custom extended", classify_block(0x1_0000) == "CUSTOM_EXTENDED")
p16 = pack16(0x1B, 0x00)
u8 = unpack16(p16)
check("Header8 pack/unpack roundtrip", u8 == (0x1B, 0x00))
ih = interpret_header(0x1B, 0x00)
check("Header8 interpret deterministic", ih == interpret_header(0x1B, 0x00))
check("Header8 interpret role", ih["structural_role"] == "ESC")
header_art = create_header8_artifact(0x1B, 0x00)
check("Header8 artifact type/version", header_art["type"] == "header8_artifact" and header_art["version"] == 1)

# ── Artifact package carrier fixtures ─────────────────────────────
print("\nArtifact package carrier:")
carrier_payload = {
    "type": "atomic_projection_package",
    "version": 1,
    "ui": {"frame": "world", "plane_tab": "RS", "basis": "10", "basis_spec_id": "dec_v1"},
}
carrier_pkg = create_artifact_package("projection_package", carrier_payload, created_at="2026-03-19T00:00:00Z")
ok_pkg = True
try:
    ok, dec = verify_artifact_package(carrier_pkg)
    ok_pkg = bool(ok and dec == carrier_payload)
except Exception:
    ok_pkg = False
check("artifact_package create/verify", ok_pkg)
check("artifact kinds allowlist", set(ALLOWED_ARTIFACT_KINDS) == {
    "projection_package",
    "semantic_graph_artifact",
    "progression_template",
    "control_diagram_artifact",
    "header8_artifact",
})
header_pkg_ok = True
try:
    header_pkg = create_artifact_package("header8_artifact", header_art, created_at="2026-03-20T00:00:00Z")
    ok_h, dec_h = verify_artifact_package(header_pkg)
    header_pkg_ok = bool(ok_h and dec_h["type"] == "header8_artifact")
except Exception:
    header_pkg_ok = False
check("header8 artifact package create/verify", header_pkg_ok)

pkg_fixture_builder = repo_root / "atomic-kernel" / "tools" / "build_artifact_package_fixture.py"
pkg_fixture_verify = subprocess.run(
    [sys.executable, str(pkg_fixture_builder), "--verify"],
    capture_output=True,
    text=True,
)
if pkg_fixture_verify.stdout.strip():
    print(pkg_fixture_verify.stdout.strip())
if pkg_fixture_verify.stderr.strip():
    print(pkg_fixture_verify.stderr.strip())
check("artifact package fixture verify", pkg_fixture_verify.returncode == 0)

png_fixture_builder = repo_root / "atomic-kernel" / "tools" / "build_artifact_package_png_fixture.mjs"
if node is None:
    check("artifact aztec png fixture verify", False)
else:
    png_fixture_verify = subprocess.run(
        [node, str(png_fixture_builder), "--verify"],
        capture_output=True,
        text=True,
    )
    if png_fixture_verify.stdout.strip():
        print(png_fixture_verify.stdout.strip())
    if png_fixture_verify.stderr.strip():
        print(png_fixture_verify.stderr.strip())
    check("artifact aztec png fixture verify", png_fixture_verify.returncode == 0)

# ── Independent JS runtime parity ─────────────────────────────────
print("\nSecond runtime parity (JavaScript):")
if node is None:
    check("node runtime available", False)
else:
    proc = subprocess.run(
        [node, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'js_runtime', 'check_parity.mjs')],
        capture_output=True,
        text=True,
    )
    print(proc.stdout.strip())
    if proc.stderr.strip():
        print(proc.stderr.strip())
    check("js runtime parity vectors pass", proc.returncode == 0)

# ── Narrative pipeline + NDJSON validation ────────────────────────
print("\nNarrative pipeline:")
builder = repo_root / "atomic-kernel" / "tools" / "build_narrative_ndjson.py"
narr_source = repo_root / "narrative-series" / "When Wisdom, Law, and the Tribe Sat Down Together"
narr_bundle = repo_root / "atomic-kernel" / "narrative_data" / "narrative_bundle.js"
progression_templates = repo_root / "atomic-kernel" / "narrative_data" / "templates" / "character_progression_templates.json"

build_verify = subprocess.run(
    [sys.executable, str(builder), "--verify"],
    capture_output=True,
    text=True,
)
if build_verify.stdout.strip():
    print(build_verify.stdout.strip())
if build_verify.stderr.strip():
    print(build_verify.stderr.strip())
check("narrative build determinism verify", build_verify.returncode == 0)

bundle_ok = narr_bundle.exists()
check("narrative bundle exists", bundle_ok)
if bundle_ok:
    raw = narr_bundle.read_text(encoding="utf-8")
    prefix = "window.NARRATIVE_DATA = "
    suffix = ";\n"
    schema_ok = False
    chapter_count_ok = False
    id_uniqueness_ok = False
    if raw.startswith(prefix) and raw.endswith(suffix):
        data = json.loads(raw[len(prefix):-len(suffix)])
        chapters = data.get("chapters", {})
        chapter_count = len(chapters)

        expected_paths = []
        expected_paths.extend(sorted((narr_source / "PRELUDE").glob("*.md")))
        for roman in ("I", "II", "III", "IV", "V", "VI", "VII", "VIII"):
            p = narr_source / f"ARTICLE {roman}.md"
            if p.exists():
                expected_paths.append(p)
        aside = narr_source / "ASIDE.md"
        if aside.exists():
            expected_paths.append(aside)
        expected_paths.extend(sorted((narr_source / "EPILOUGE").glob("*.md")))
        chapter_count_ok = chapter_count == len(expected_paths)

        seen_ids = set()
        id_uniqueness_ok = True
        schema_ok = True
        required = {
            "chapter_meta": {"id", "title", "source_path", "order", "world_theme", "intro_scene_id"},
            "scene": {"id", "chapter_id", "heading", "body_text", "world_node", "grants_artifacts", "requires_artifacts"},
            "choice": {"id", "from_scene_id", "label", "to_scene_id", "requires_artifacts", "grants_artifacts"},
            "artifact": {"id", "name", "description", "model_ref", "cross_world_tags"},
            "semantic_node": {"id", "scene_id", "chapter_id", "label", "kind"},
            "semantic_edge": {"id", "scene_id", "chapter_id", "subject", "predicate", "object", "weight"},
            "semantic_transition": {"id", "scene_id", "op", "target_id"},
        }
        for ch in chapters.values():
            recs = ch.get("records", [])
            by_type = {}
            for r in recs:
                rid = r.get("id")
                if rid:
                    if rid in seen_ids:
                        id_uniqueness_ok = False
                    seen_ids.add(rid)
                by_type.setdefault(r.get("type"), []).append(r)
            for rtype, keys in required.items():
                rows = by_type.get(rtype, [])
                if not rows:
                    schema_ok = False
                    continue
                for row in rows:
                    if not keys.issubset(set(row.keys())):
                        schema_ok = False
    check("every markdown file maps to chapter data", chapter_count_ok)
    check("ndjson runtime schema coverage", schema_ok)
    check("deterministic id uniqueness in bundle", id_uniqueness_ok)

templates_ok = progression_templates.exists()
schema_ok = False
if templates_ok:
    try:
        bundle = json.loads(progression_templates.read_text(encoding="utf-8"))
        templates = bundle.get("templates", [])
        schema_ok = bool(templates) and all(
            {"id", "name", "kind", "nodes", "edges", "transitions"}.issubset(set(t.keys()))
            for t in templates
        )
    except Exception:
        schema_ok = False
check("character progression templates exist", templates_ok)
check("character progression template schema", schema_ok)

# ── WordNet 5WN browser NLP bridge ────────────────────────────────
print("\nWordNet 5WN NLP bridge:")
wordnet_builder = repo_root / "atomic-kernel" / "tools" / "build_wordnet_5wn_index.py"
wordnet_index = repo_root / "atomic-kernel" / "nlp" / "wordnet_5wn_index.json"
wordnet_bundle = repo_root / "atomic-kernel" / "nlp" / "bundle.js"

wn_verify = subprocess.run(
    [sys.executable, str(wordnet_builder), "--verify"],
    capture_output=True,
    text=True,
)
if wn_verify.stdout.strip():
    print(wn_verify.stdout.strip())
if wn_verify.stderr.strip():
    print(wn_verify.stderr.strip())
check("wordnet index deterministic verify", wn_verify.returncode == 0)
check("wordnet index exists", wordnet_index.exists())
check("nlp browser bundle exists", wordnet_bundle.exists())

# Q1 / Transition / constructive: deterministic replay receipt
seed_q1 = 0xACE1
steps_q1 = 16
trace_a = replay(16, seed_q1, steps_q1)
trace_b = replay(16, seed_q1, steps_q1)
digest = hashlib.sha256(",".join(f"{x:04X}" for x in trace_a).encode("utf-8")).hexdigest()
receipt_q1 = {
    "question": "Q1",
    "algorithm": "transition",
    "proof_type": "constructive",
    "seed": f"0x{seed_q1:04X}",
    "steps": steps_q1,
    "deterministic": trace_a == trace_b,
    "trace_sha256": digest,
}
check("112 Q1 Transition constructive: deterministic replay receipt", bool(receipt_q1["deterministic"] and receipt_q1["trace_sha256"]))

# Q6 / Proposal-Receipt / constructive: accepted proposal applies only at next lawful tick
proposal = defer_proposal("wp_q6_001", {"target": "avatar_policy", "value": "queued"}, current_tick=12)
accepted = accept_proposal(proposal)
applied_same_tick, receipt_same_tick = commit_proposal(accepted, tick=12)
applied_next_tick, receipt_next_tick = commit_proposal(accepted, tick=13)
q6_ok = (applied_same_tick is False and receipt_same_tick is None and applied_next_tick is True and receipt_next_tick is not None)
check("112 Q6 Proposal/Receipt constructive: deferred next-tick commit", q6_ok)

# Q7 / Branch-Reconciliation / constructive: explicit base+delta+return replayable
canonical_log = [
    {"t": 0, "type": "new_game", "payload": {"slot": 0}},
    {"t": 1, "type": "chapter_entered", "payload": {"chapter_id": "article_i"}},
    {"t": 2, "type": "choice_selected", "payload": {"choice_id": "c1"}},
    {"t": 3, "type": "scene_entered", "payload": {"scene_id": "s2"}},
]
deltas = [
    {"t": 2, "type": "artifact_granted", "payload": {"artifact_id": "a1"}},
    {"t": 3, "type": "choice_selected", "payload": {"choice_id": "c_branch"}},
]
fork = materialize_branch_artifact(canonical_log, 2, deltas, parent_lineage_id="mainline")
branch_ok = (
    branch_reconciliation_valid(canonical_log, fork)
    and replay_branch(canonical_log, fork) == (canonical_log[:2] + deltas)
    and return_to_canonical(canonical_log, fork) == canonical_log[:2]
)
check("112 Q7 Branch/Reconciliation constructive: base+delta+return replayable", branch_ok)

# Q7 / Branch-Reconciliation / constructive: deterministic past/present/future reconciliation
reconcile_a = reconcile_temporal_views(
    canonical_log,
    fork,
    pending_proposals=[
        {
            "proposal_id": accepted.proposal_id,
            "apply_at_tick": accepted.apply_at_tick,
            "payload": dict(accepted.payload),
            "accepted": accepted.accepted,
        }
    ],
)
reconcile_b = reconcile_temporal_views(
    canonical_log,
    fork,
    pending_proposals=[
        {
            "proposal_id": accepted.proposal_id,
            "apply_at_tick": accepted.apply_at_tick,
            "payload": dict(accepted.payload),
            "accepted": accepted.accepted,
        }
    ],
)
q7_temporal_ok = (
    reconcile_a == reconcile_b
    and reconcile_a["past_len"] == 2
    and reconcile_a["present_len"] == 4
    and reconcile_a["future_len"] == 1
)
check("112 Q7 Branch/Reconciliation constructive: deterministic past/present/future reconciliation", q7_temporal_ok)

# Q4 / Projection / constructive: same canonical state -> equivalent multi-projection receipts
canon_state = {
    "tick": 42,
    "phase": "chapter_scene",
    "chapter": "article_iv",
    "scene": "scene_2",
    "inventory": ["artifact_a", "artifact_b"],
}
proj_a = multi_projection_receipt(canon_state)
proj_b = multi_projection_receipt(canon_state)
q4_ok = projection_receipt_equivalent(proj_a, proj_b) and projection_receipt_anchored(proj_a)
check("112 Q4 Projection constructive: equivalent multi-projection receipts", q4_ok)

# ── Final ─────────────────────────────────────────────────────────
print()
print("=" * 55)
total = PASS + FAIL
print(f"  {PASS}/{total} passed  {'✓ ALL GOOD' if FAIL == 0 else f'✗ {FAIL} FAILED'}")
print("=" * 55)
sys.exit(0 if FAIL == 0 else 1)
