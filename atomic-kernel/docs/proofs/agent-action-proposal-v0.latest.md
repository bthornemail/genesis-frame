# Agent Action Proposal v0 Proof

Generated (UTC): 2026-03-21T20:18:54Z
Command: bash tools/agent_action_proposal_v0_gate.sh

Checks:
- schema JSON parse: PASS
- contract envelope verify: PASS
- mock deterministic rerun byte equality: PASS
- advisory + proposal-only boundary: PASS
- receipt accepted=false: PASS
- replay_hash integrity: PASS

Artifacts:
- /home/main/devops/genesis-frame/atomic-kernel/artifacts/agent-action-proposal-v0.normalized.json
- /home/main/devops/genesis-frame/atomic-kernel/artifacts/agent-action-proposal-v0.replay-hash
- /home/main/devops/genesis-frame/atomic-kernel/docs/schemas/agent_action_proposal.v0.schema.json
- /home/main/devops/genesis-frame/atomic-kernel/narrative_data/contracts/agent_action_proposal.v0.json

Result: PASS
