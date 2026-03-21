#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="$ROOT/artifacts"
PROOF_DIR="$ROOT/docs/proofs"
NORM="$ART_DIR/immersive-parity-v1.normalized.json"
TMP1="$ART_DIR/.immersive-parity-v1.normalized.pass1.json"
TMP2="$ART_DIR/.immersive-parity-v1.normalized.pass2.json"
HASH_FILE="$ART_DIR/immersive-parity-v1.replay-hash"
RECEIPT="$PROOF_DIR/immersive-parity-v1.latest.md"

mkdir -p "$ART_DIR" "$PROOF_DIR"

emit_once() {
  python3 - "$ROOT" <<'PY'
import json
import hashlib
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
chapter_dir = root / "narrative_data" / "chapters"
cue_dir = root / "narrative_data" / "cues"
docs_cue_dir = root.parent / "docs" / "immersive-data" / "cues"
casting_dir = root / "narrative_data" / "casting"
docs_casting_dir = root.parent / "docs" / "immersive-data" / "casting"
contracts_dir = root / "narrative_data" / "contracts"
world_html = (root / "world.html").read_text(encoding="utf-8")
portal_html = (root.parent / "docs" / "portal-immersive-sims.html").read_text(encoding="utf-8")

def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

chapters = sorted(p.stem for p in chapter_dir.glob("ch_*.ndjson"))
cues = sorted(p.name for p in cue_dir.glob("ch_*.cinematic_cues.v1.json"))
docs_cues = sorted(p.name for p in docs_cue_dir.glob("ch_*.cinematic_cues.v1.json"))
expected_cues = [f"{cid}.cinematic_cues.v1.json" for cid in chapters]

if cues != expected_cues:
    raise SystemExit(f"cue set mismatch vs chapters: cues={len(cues)} chapters={len(chapters)}")
if docs_cues != expected_cues:
    raise SystemExit(f"docs cue set mismatch vs chapters: docs_cues={len(docs_cues)} chapters={len(chapters)}")

cue_digests = {}
for name in expected_cues:
    a = cue_dir / name
    b = docs_cue_dir / name
    da = sha(a)
    db = sha(b)
    if da != db:
        raise SystemExit(f"cue mirror mismatch: {name}")
    payload = json.loads(a.read_text(encoding="utf-8"))
    cue_digests[name] = {
        "sha256": da,
        "chapter_id": payload.get("chapter_id"),
        "timeline_tick_span": payload.get("timeline_tick_span"),
        "cue_digest_sha256": payload.get("cue_digest_sha256"),
    }

casting_files = [
    "avatar_cast_map.v1.json",
    "landscape_cast_map.v1.json",
    "public_allowlist.v1.json",
]
casting_mirror = {}
for name in casting_files:
    a = casting_dir / name
    b = docs_casting_dir / name
    if not a.exists() or not b.exists():
        raise SystemExit(f"missing casting mirror file: {name}")
    da = sha(a)
    db = sha(b)
    if da != db:
        raise SystemExit(f"casting mirror mismatch: {name}")
    casting_mirror[name] = da

proposal = json.loads((contracts_dir / "immersive_proposal.v1.json").read_text(encoding="utf-8"))
receipt = json.loads((contracts_dir / "immersive_receipt.v1.json").read_text(encoding="utf-8"))

required_world_ids = [
    "btn-story-director-play",
    "btn-story-director-stepin",
    "btn-story-director-diverge",
    "btn-story-director-accept",
    "btn-story-director-reject",
    "story-director-meta",
]
required_portal_ids = [
    "storyPlay",
    "storyStepIn",
    "storyDiverge",
    "storyAccept",
    "storyReject",
    "storyState",
    "storyBody",
    "proposalList",
]
for rid in required_world_ids:
    if f'id="{rid}"' not in world_html:
        raise SystemExit(f"missing world control id: {rid}")
for rid in required_portal_ids:
    if f'id="{rid}"' not in portal_html:
        raise SystemExit(f"missing portal control id: {rid}")

required_action_tokens = ["choice_select", "camera_branch", "avatar_swap", "scene_pace_change"]
for token in required_action_tokens:
    if token not in world_html:
        raise SystemExit(f"world missing action token: {token}")
    if token not in portal_html:
        raise SystemExit(f"portal missing action token: {token}")

proposal_actions = proposal.get("properties", {}).get("action", {}).get("enum", [])
receipt_decisions = receipt.get("properties", {}).get("decision", {}).get("enum", [])
if sorted(proposal_actions) != sorted(required_action_tokens):
    raise SystemExit("proposal action enum mismatch")
if sorted(receipt_decisions) != ["accepted", "rejected"]:
    raise SystemExit("receipt decision enum mismatch")

world_has_pending = "status: 'pending'" in world_html
world_has_queue = "queueImmersiveProposal(" in world_html
world_has_accept = "acceptImmersiveProposal(" in world_html
world_has_reject = "rejectImmersiveProposal(" in world_html
portal_has_pending = "status: 'pending'" in portal_html
portal_has_queue = "queueProposal(" in portal_html
portal_has_accept = "acceptProposal(" in portal_html
portal_has_reject = "rejectProposal(" in portal_html
if not all([
    world_has_pending, world_has_queue, world_has_accept, world_has_reject,
    portal_has_pending, portal_has_queue, portal_has_accept, portal_has_reject,
]):
    raise SystemExit("proposal lifecycle hooks missing in runtime surfaces")

out = {
    "type": "immersive_parity_v1",
    "version": 1,
    "authority": "advisory",
    "chapters": chapters,
    "chapter_count": len(chapters),
    "cue_count": len(expected_cues),
    "cue_mirror_parity": True,
    "casting_mirror_parity": True,
    "cue_digests": cue_digests,
    "casting_sha256": casting_mirror,
    "proposal_action_enum": proposal_actions,
    "receipt_decision_enum": receipt_decisions,
    "world_controls_present": required_world_ids,
    "portal_controls_present": required_portal_ids,
    "proposal_lifecycle_tokens_present": {
        "world_pending": world_has_pending,
        "world_queue_hook": world_has_queue,
        "world_accept_hook": world_has_accept,
        "world_reject_hook": world_has_reject,
        "portal_pending": portal_has_pending,
        "portal_queue_hook": portal_has_queue,
        "portal_accept_hook": portal_has_accept,
        "portal_reject_hook": portal_has_reject,
    },
}

print(json.dumps(out, indent=2, sort_keys=True))
PY
}

emit_once > "$TMP1"
emit_once > "$TMP2"

cmp -s "$TMP1" "$TMP2"
mv "$TMP1" "$NORM"
rm -f "$TMP2"

HASH="$(sha256sum "$NORM" | awk '{print $1}')"
printf '%s\n' "$HASH" > "$HASH_FILE"

UTC_NOW="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
cat > "$RECEIPT" <<EOF
# Immersive Parity v1 Proof

Generated (UTC): $UTC_NOW
Root: $ROOT
Command: bash tools/immersive_parity_v1_gate.sh

Checks:
- chapter/cue count parity: PASS
- cue mirror byte parity (atomic-kernel <-> docs): PASS
- casting mirror byte parity (atomic-kernel <-> docs): PASS
- world control surface presence: PASS
- portal control surface presence: PASS
- immersive proposal/receipt contract enums: PASS
- deterministic rerun compare: PASS

Artifacts:
- $NORM
- $HASH_FILE

Replay Hash:
\`$HASH\`

Result: PASS
EOF

echo "ok immersive parity v1 gate"
