#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="$ROOT/artifacts"
PROOF_DIR="$ROOT/docs/proofs"
SCHEMA="$ROOT/docs/schemas/agent_provider_policy.v0.schema.json"
CONTRACT="$ROOT/narrative_data/contracts/agent_provider_policy.v0.json"
NORM="$ART_DIR/agent-provider-policy-v0.normalized.json"
HASH="$ART_DIR/agent-provider-policy-v0.replay-hash"
RECEIPT="$PROOF_DIR/agent-provider-policy-v0.latest.md"

mkdir -p "$ART_DIR" "$PROOF_DIR"

jq . "$SCHEMA" >/dev/null
jq . "$CONTRACT" >/dev/null

python3 "$ROOT/tools/agent_provider_router_v0.py" --verify
python3 "$ROOT/tools/agent_provider_router_v0.py" --profile small --write --out "$ART_DIR/.agent-provider-small.json"
python3 "$ROOT/tools/agent_provider_router_v0.py" --profile medium --write --out "$ART_DIR/.agent-provider-medium.json"
python3 "$ROOT/tools/agent_provider_router_v0.py" --profile large --write --out "$ART_DIR/.agent-provider-large.json"

python3 - "$ART_DIR/.agent-provider-small.json" "$ART_DIR/.agent-provider-medium.json" "$ART_DIR/.agent-provider-large.json" <<'PY'
import json, pathlib, re, sys
paths=[pathlib.Path(p) for p in sys.argv[1:]]
for p in paths:
    obj=json.loads(p.read_text(encoding='utf-8'))
    if obj.get('v')!='agent_provider_policy.v0':
        raise SystemExit('version mismatch')
    if obj.get('authority')!='advisory':
        raise SystemExit('authority mismatch')
    if obj.get('selected_profile') not in {'small','medium','large'}:
        raise SystemExit('selected_profile mismatch')
    if obj.get('selected_provider') not in {'mock','opencode','ollama','openclaw_adapter'}:
        raise SystemExit('selected_provider mismatch')
    if not re.match(r'^[0-9a-f]{64}$', obj.get('replay_hash','')):
        raise SystemExit('replay_hash format mismatch')
PY

cp "$ART_DIR/.agent-provider-small.json" "$NORM"
rm -f "$ART_DIR/.agent-provider-small.json" "$ART_DIR/.agent-provider-medium.json" "$ART_DIR/.agent-provider-large.json"
sha256sum "$NORM" | awk '{print $1}' > "$HASH"

UTC_NOW="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
cat > "$RECEIPT" <<REC
# Agent Provider Policy v0 Proof

Generated (UTC): $UTC_NOW
Command: bash tools/agent_provider_router_v0_gate.sh

Checks:
- schema JSON parse: PASS
- contract replay-hash verify: PASS
- profile routing (small/medium/large): PASS
- selected provider bounded set: PASS
- policy authority advisory: PASS

Artifacts:
- $NORM
- $HASH
- $SCHEMA
- $CONTRACT

Result: PASS
REC

echo "ok agent provider policy v0 gate"
