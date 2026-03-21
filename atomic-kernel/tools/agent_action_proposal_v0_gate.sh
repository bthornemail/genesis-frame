#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="$ROOT/artifacts"
PROOF_DIR="$ROOT/docs/proofs"
SCHEMA="$ROOT/docs/schemas/agent_action_proposal.v0.schema.json"
CONTRACT="$ROOT/narrative_data/contracts/agent_action_proposal.v0.json"
NORM="$ART_DIR/agent-action-proposal-v0.normalized.json"
HASH="$ART_DIR/agent-action-proposal-v0.replay-hash"
RECEIPT="$PROOF_DIR/agent-action-proposal-v0.latest.md"

mkdir -p "$ART_DIR" "$PROOF_DIR"

jq . "$SCHEMA" >/dev/null
jq . "$CONTRACT" >/dev/null

python3 "$ROOT/tools/agent_action_proposal_v0.py" --verify --intent "verify-contract-shape"

TMP1="$ART_DIR/.agent-action-proposal-v0.tmp1.json"
TMP2="$ART_DIR/.agent-action-proposal-v0.tmp2.json"

python3 "$ROOT/tools/agent_action_proposal_v0.py" \
  --provider mock \
  --world-id world.v0:orchard_garden_lattice \
  --agent-id writer.proposal.constructive \
  --canonical-tick 52 \
  --intent "Queue chapter-scene dialogue branch proposal" \
  --write \
  --out "$TMP1"

python3 "$ROOT/tools/agent_action_proposal_v0.py" \
  --provider mock \
  --world-id world.v0:orchard_garden_lattice \
  --agent-id writer.proposal.constructive \
  --canonical-tick 52 \
  --intent "Queue chapter-scene dialogue branch proposal" \
  --write \
  --out "$TMP2"

cmp -s "$TMP1" "$TMP2"
cp "$TMP1" "$NORM"
rm -f "$TMP1" "$TMP2"

python3 - "$NORM" <<'PY'
import hashlib
import json
import pathlib
import re
import sys

p = pathlib.Path(sys.argv[1])
obj = json.loads(p.read_text(encoding='utf-8'))

if obj.get('authority') != 'advisory':
    raise SystemExit('authority mismatch')
if obj.get('mutation_boundary') != 'proposal_only':
    raise SystemExit('mutation_boundary mismatch')
if obj.get('provider') != 'mock':
    raise SystemExit('provider mismatch for deterministic gate')
if obj.get('receipt_stub', {}).get('accepted') is not False:
    raise SystemExit('accepted must be false')
if not re.match(r'^prop_[0-9a-f]{16}$', obj.get('proposal_id', '')):
    raise SystemExit('proposal_id format mismatch')
if not re.match(r'^rcpt_[0-9a-f]{16}$', obj.get('receipt_stub', {}).get('receipt_ref', '')):
    raise SystemExit('receipt_ref format mismatch')

check = dict(obj)
replay_hash = check.pop('replay_hash', None)
expect = hashlib.sha256(json.dumps(check, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
if replay_hash != expect:
    raise SystemExit('replay_hash mismatch')
PY

sha256sum "$NORM" | awk '{print $1}' > "$HASH"

UTC_NOW="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
cat > "$RECEIPT" <<REC
# Agent Action Proposal v0 Proof

Generated (UTC): $UTC_NOW
Command: bash tools/agent_action_proposal_v0_gate.sh

Checks:
- schema JSON parse: PASS
- contract envelope verify: PASS
- mock deterministic rerun byte equality: PASS
- advisory + proposal-only boundary: PASS
- receipt accepted=false: PASS
- replay_hash integrity: PASS

Artifacts:
- $NORM
- $HASH
- $SCHEMA
- $CONTRACT

Result: PASS
REC

echo "ok agent action proposal v0 gate"
