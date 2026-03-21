#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="$ROOT/artifacts"
PROOF_DIR="$ROOT/docs/proofs"
NORM="$ART_DIR/agent112-v0.normalized.json"
TMP1="$ART_DIR/.agent112-v0.pass1.json"
TMP2="$ART_DIR/.agent112-v0.pass2.json"
HASH_FILE="$ART_DIR/agent112-v0.replay-hash"
RECEIPT="$PROOF_DIR/agent112-v0.latest.md"

mkdir -p "$ART_DIR" "$PROOF_DIR"

python3 "$ROOT/tools/build_agent112_registry_v0.py" --write
python3 "$ROOT/tools/build_agent112_registry_v0.py" --verify

python3 - "$ROOT" > "$TMP1" <<'PY'
import json
import hashlib
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
pm = json.loads((root / 'narrative_data/agent112/proof_matrix_112.v0.json').read_text(encoding='utf-8'))
ar = json.loads((root / 'narrative_data/agent112/agent_registry_112.v0.json').read_text(encoding='utf-8'))
am = json.loads((root / 'narrative_data/agent112/agent_matrix_112.v0.json').read_text(encoding='utf-8'))

if pm.get('cell_count') != 112:
    raise SystemExit('cell_count must be 112')
if ar.get('agent_count') != 112:
    raise SystemExit('agent_count must be 112')
if pm.get('authority') != 'advisory' or ar.get('authority') != 'advisory':
    raise SystemExit('authority must remain advisory')
if am.get('authority') != 'advisory':
    raise SystemExit('agent matrix authority must remain advisory')

cells = {c['cell_id'] for c in pm['cells']}
agent_cells = [a['cell_id'] for a in ar['agents']]
if len(set(agent_cells)) != 112:
    raise SystemExit('agent cell mapping must be unique')
if cells != set(agent_cells):
    raise SystemExit('agent/cell set mismatch')

if am.get('role_count') != 8 or am.get('assistant_count_total') != 112:
    raise SystemExit('agent matrix cardinality mismatch')

priority_bands = {'critical', 'important', 'expansive'}
assistant_ids = []
assistant_cells = []
for role in am.get('roles', []):
    if role.get('priority_band') not in priority_bands:
        raise SystemExit(f'invalid priority band: {role.get("role_id")}')
    if len(role.get('agents', [])) != 7:
        raise SystemExit(f'role lane mismatch: {role.get("role_id")}')
    for lane in role.get('agents', []):
        if len(lane.get('assistants', [])) != 2:
            raise SystemExit(f'assistant lane mismatch: {lane.get("agent_id")}')
        for assistant in lane.get('assistants', []):
            assistant_ids.append(assistant.get('assistant_id'))
            assistant_cells.append(assistant.get('cell_id'))
if len(set(assistant_ids)) != 112:
    raise SystemExit('assistant ids must be unique')
if set(assistant_cells) != cells:
    raise SystemExit('assistant/cell mapping mismatch')

# proof-form parity per question/algorithm
index = {}
for c in pm['cells']:
    key = (c['question_id'], c['algorithm_id'])
    index.setdefault(key, set()).add(c['proof_form'])
if any(v != {'constructive', 'falsification'} for v in index.values()):
    raise SystemExit('proof-form parity mismatch')

out = {
    'type': 'agent112_v0_gate',
    'version': 1,
    'authority': 'advisory',
    'cell_count': pm['cell_count'],
    'agent_count': ar['agent_count'],
    'question_count': pm['question_count'],
    'algorithm_count': pm['algorithm_count'],
    'proof_form_count': pm['proof_form_count'],
    'source_matrix_sha256': pm['source_matrix_sha256'],
    'proof_matrix_replay_hash': pm['replay_hash'],
    'agent_registry_replay_hash': ar['replay_hash'],
    'agent_matrix_replay_hash': am['replay_hash'],
}
out['replay_hash'] = hashlib.sha256(json.dumps(out, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
print(json.dumps(out, indent=2, sort_keys=True))
PY

python3 - "$ROOT" > "$TMP2" <<'PY'
import json
import hashlib
import pathlib
import sys
root = pathlib.Path(sys.argv[1])
pm = json.loads((root / 'narrative_data/agent112/proof_matrix_112.v0.json').read_text(encoding='utf-8'))
ar = json.loads((root / 'narrative_data/agent112/agent_registry_112.v0.json').read_text(encoding='utf-8'))
am = json.loads((root / 'narrative_data/agent112/agent_matrix_112.v0.json').read_text(encoding='utf-8'))
out = {
    'type': 'agent112_v0_gate',
    'version': 1,
    'authority': 'advisory',
    'cell_count': pm['cell_count'],
    'agent_count': ar['agent_count'],
    'question_count': pm['question_count'],
    'algorithm_count': pm['algorithm_count'],
    'proof_form_count': pm['proof_form_count'],
    'source_matrix_sha256': pm['source_matrix_sha256'],
    'proof_matrix_replay_hash': pm['replay_hash'],
    'agent_registry_replay_hash': ar['replay_hash'],
    'agent_matrix_replay_hash': am['replay_hash'],
}
out['replay_hash'] = hashlib.sha256(json.dumps(out, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
print(json.dumps(out, indent=2, sort_keys=True))
PY

cmp -s "$TMP1" "$TMP2"
mv "$TMP1" "$NORM"
rm -f "$TMP2"

HASH="$(sha256sum "$NORM" | awk '{print $1}')"
printf '%s\n' "$HASH" > "$HASH_FILE"

UTC_NOW="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
cat > "$RECEIPT" <<REC
# Agent112 v0 Proof

Generated (UTC): $UTC_NOW
Root: $ROOT
Command: bash tools/agent112_v0_gate.sh

Checks:
- 8x7x2 proof matrix cardinality: PASS
- one agent per cell mapping: PASS
- role/lane/assistant partition integrity: PASS
- proof-form parity per Q/A: PASS
- advisory authority boundary: PASS
- deterministic rerun compare: PASS

Artifacts:
- $NORM
- $HASH_FILE
- narrative_data/agent112/proof_matrix_112.v0.json
- narrative_data/agent112/agent_registry_112.v0.json
- narrative_data/agent112/agent_matrix_112.v0.json

Replay Hash:
$HASH

Result: PASS
REC

echo "ok agent112 v0 gate"
