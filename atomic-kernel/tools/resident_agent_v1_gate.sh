#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="$ROOT/artifacts"
PROOF_DIR="$ROOT/docs/proofs"
NORM="$ART_DIR/resident-agent-v1.normalized.json"
TMP1="$ART_DIR/.resident-agent-v1.pass1.json"
TMP2="$ART_DIR/.resident-agent-v1.pass2.json"
HASH_FILE="$ART_DIR/resident-agent-v1.replay-hash"
RECEIPT="$PROOF_DIR/resident-agent-v1.latest.md"

mkdir -p "$ART_DIR" "$PROOF_DIR"

CHAPTER_ID="$(ls "$ROOT"/narrative_data/chapters/ch_*.ndjson | sed -n '1p' | xargs -n1 basename | sed 's/.ndjson$//')"

python3 "$ROOT/tools/resident_agent_tick_v1.py" --seed "resident-v1" --chapter-id "$CHAPTER_ID" --start-tick 0 --ticks 8 > "$TMP1"
python3 "$ROOT/tools/resident_agent_tick_v1.py" --seed "resident-v1" --chapter-id "$CHAPTER_ID" --start-tick 0 --ticks 8 > "$TMP2"

cmp -s "$TMP1" "$TMP2"
mv "$TMP1" "$NORM"
rm -f "$TMP2"

python3 - "$NORM" <<'PY'
import json
import sys
p = sys.argv[1]
obj = json.load(open(p, 'r', encoding='utf-8'))
if obj.get('authority') != 'advisory':
    raise SystemExit('authority must be advisory')
if any(x.get('status') != 'pending' for x in obj.get('proposals', [])):
    raise SystemExit('all proposals must remain pending')
actions = set(obj.get('action_enum', []))
if actions != {'choice_select','camera_branch','avatar_swap','scene_pace_change'}:
    raise SystemExit('action enum mismatch')
print('ok resident agent contract checks')
PY

HASH="$(sha256sum "$NORM" | awk '{print $1}')"
printf '%s\n' "$HASH" > "$HASH_FILE"

UTC_NOW="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
cat > "$RECEIPT" <<REC
# Resident Agent v1 Proof

Generated (UTC): $UTC_NOW
Root: $ROOT
Command: bash tools/resident_agent_v1_gate.sh

Checks:
- deterministic rerun compare: PASS
- authority advisory only: PASS
- proposal-only pending status: PASS
- bounded action enum: PASS

Artifacts:
- $NORM
- $HASH_FILE

Replay Hash:

$HASH

Result: PASS
REC

echo "ok resident agent v1 gate"
