#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="$ROOT/artifacts"
PROOF_DIR="$ROOT/docs/proofs"
POLICY="$ROOT/narrative_data/contracts/canonical_time_policy.v0.json"
SCHEMA="$ROOT/docs/schemas/canonical_time_policy.v0.schema.json"
NORM="$ART_DIR/canonical-time-v0.normalized.json"
HASH="$ART_DIR/canonical-time-v0.replay-hash"
RECEIPT="$PROOF_DIR/canonical-time-v0.latest.md"

mkdir -p "$ART_DIR" "$PROOF_DIR"

jq . "$POLICY" >/dev/null
jq . "$SCHEMA" >/dev/null

python3 - "$POLICY" <<'PY'
import json
import pathlib
import sys
p = pathlib.Path(sys.argv[1])
obj = json.loads(p.read_text(encoding='utf-8'))
if obj.get('type') != 'canonical_time_policy':
    raise SystemExit('type mismatch')
if obj.get('authority') != 'algorithmic':
    raise SystemExit('authority mismatch')
if obj.get('canonical_time_source') != 'algorithmic_tick':
    raise SystemExit('canonical_time_source must be algorithmic_tick')
if obj.get('ordering_authority') != 'chirality_within_tick_only':
    raise SystemExit('ordering_authority mismatch')
if obj.get('proposal_acceptance_boundary') != 'lawful_tick_boundary':
    raise SystemExit('proposal boundary mismatch')
if len(obj.get('reject_conditions', [])) < 5:
    raise SystemExit('reject conditions insufficient')
PY

python3 - "$POLICY" "$NORM" <<'PY'
import json
import hashlib
import pathlib
import sys
policy = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
obj = json.loads(policy.read_text(encoding='utf-8'))
norm = {
  'type': 'canonical_time_v0_gate',
  'version': 1,
  'authority': obj['authority'],
  'canonical_time_source': obj['canonical_time_source'],
  'ordering_authority': obj['ordering_authority'],
  'eligibility_function': obj['eligibility_function'],
  'proposal_acceptance_boundary': obj['proposal_acceptance_boundary'],
  'reject_conditions': obj['reject_conditions'],
}
norm['replay_hash'] = hashlib.sha256(json.dumps(norm, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
out.write_text(json.dumps(norm, sort_keys=True, indent=2) + "\n", encoding='utf-8')
PY

sha256sum "$NORM" | awk '{print $1}' > "$HASH"

UTC_NOW="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
cat > "$RECEIPT" <<REC
# Canonical Time v0 Proof

Generated (UTC): $UTC_NOW
Command: bash tools/canonical_time_v0_gate.sh

Checks:
- policy schema JSON parse: PASS
- canonical time source single-authority: PASS
- chirality ordering scope constrained: PASS
- A14 eligibility relation present: PASS
- proposal acceptance boundary constrained: PASS

Artifacts:
- $NORM
- $HASH
- $POLICY
- $SCHEMA

Result: PASS
REC

echo "ok canonical time v0 gate"
