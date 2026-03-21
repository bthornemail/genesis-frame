#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_MATRIX_PATH = ROOT / "narrative_data" / "agent112" / "agent_matrix_112.v0.json"
OUT_PATH = ROOT / "narrative_data" / "contracts" / "role_toolset_matrix_112.v0.json"

ALGORITHM_BY_LANE = {
    "transition": "carrier",
    "control": "header8",
    "projection": "activation_projection",
    "escape": "escape_control",
    "chirality": "chirality_fano",
    "proposal": "proposal_receipt",
    "reconcile": "a14_scheduling",
}

TOOLSET_DEFS = {
    "carrier": {
        "basis": "dormant canonical artifact carrier",
        "mcp_tools": [
            {"name": "verify_artifact", "availability": "planned"},
            {"name": "decode_artifact", "availability": "planned"},
            {"name": "get_artifact_manifest", "availability": "planned"},
            {"name": "emit_aztec_projection", "availability": "planned"},
        ],
    },
    "header8": {
        "basis": "atomic unit/stream interpretation",
        "mcp_tools": [
            {"name": "interpret_header8_stream", "availability": "planned"},
            {"name": "verify_header8_stream", "availability": "planned"},
            {"name": "classify_structural", "availability": "planned"},
            {"name": "classify_block", "availability": "planned"},
        ],
    },
    "escape_control": {
        "basis": "bounded scoped interpretation",
        "mcp_tools": [
            {"name": "enter_escape_scope", "availability": "planned"},
            {"name": "close_escape_scope", "availability": "planned"},
            {"name": "validate_escape_scope", "availability": "planned"},
            {"name": "reject_invalid_escape", "availability": "planned"},
        ],
    },
    "chirality_fano": {
        "basis": "canonical ordering over partitions",
        "mcp_tools": [
            {"name": "partition_candidate_set", "availability": "planned"},
            {"name": "kernel_bit", "availability": "planned"},
            {"name": "chirality_select", "availability": "planned"},
            {"name": "verify_order_invariance", "availability": "planned"},
        ],
    },
    "a14_scheduling": {
        "basis": "eligibility and bounded runtime scheduling",
        "mcp_tools": [
            {"name": "get_incidence_schedule_snapshot", "availability": "planned"},
            {"name": "compute_eligibility", "availability": "planned"},
            {"name": "schedule_agent_step", "availability": "planned"},
            {"name": "check_tick_budget", "availability": "planned"},
        ],
    },
    "proposal_receipt": {
        "basis": "proposal-first mutation boundary",
        "mcp_tools": [
            {"name": "create_proposal", "availability": "planned"},
            {"name": "accept_proposal", "availability": "planned"},
            {"name": "reject_proposal", "availability": "planned"},
            {"name": "emit_receipt", "availability": "planned"},
            {"name": "verify_receipt_lineage", "availability": "planned"},
            {"name": "step_world", "availability": "planned"},
        ],
    },
    "activation_projection": {
        "basis": "advisory local views from dormant carrier",
        "mcp_tools": [
            {"name": "activate_artifact", "availability": "planned"},
            {"name": "get_projection_view", "availability": "planned"},
            {"name": "verify_projection_view", "availability": "planned"},
            {"name": "get_world_projection", "availability": "planned"},
            {"name": "get_world_state", "availability": "planned"},
            {"name": "verify_world", "availability": "planned"},
        ],
    },
    "control_plane": {
        "basis": "bounded allowlisted control plane pages",
        "mcp_tools": [
            {"name": "list_control_plane_pages", "availability": "available"},
            {"name": "get_control_plane_page", "availability": "available"},
        ],
    },
}


def stable_json(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build() -> dict:
    am = json.loads(AGENT_MATRIX_PATH.read_text(encoding="utf-8"))

    roles = []
    for role in am["roles"]:
        lanes = []
        for lane in role["agents"]:
            lane_id = lane["lane_id"]
            algorithm_family = ALGORITHM_BY_LANE[lane_id]
            lanes.append(
                {
                    "lane_id": lane_id,
                    "agent_id": lane["agent_id"],
                    "algorithm_family": algorithm_family,
                    "proof_assistants": [
                        {
                            "assistant_id": a["assistant_id"],
                            "proof_form": a["proof_form"],
                            "cell_id": a["cell_id"],
                        }
                        for a in lane["assistants"]
                    ],
                    "toolset": TOOLSET_DEFS[algorithm_family],
                }
            )
        roles.append(
            {
                "role_id": role["role_id"],
                "question_id": role["question_id"],
                "question_slug": role["question_slug"],
                "priority_band": role["priority_band"],
                "lane_agents": lanes,
            }
        )

    out = {
        "v": "role_toolset_matrix_112.v0",
        "authority": "advisory",
        "basis": {
            "roles": 8,
            "lanes_per_role": 7,
            "proof_forms_per_lane": 2,
            "formula": "8x7x2",
            "algorithm_families": [
                "carrier",
                "header8",
                "escape_control",
                "chirality_fano",
                "a14_scheduling",
                "proposal_receipt",
                "activation_projection",
            ],
        },
        "control_plane_tools": TOOLSET_DEFS["control_plane"],
        "source_agent_matrix": "narrative_data/agent112/agent_matrix_112.v0.json",
        "source_agent_matrix_replay_hash": am["replay_hash"],
        "roles": roles,
    }
    out["replay_hash"] = sha256_text(stable_json(out))
    return out


def validate(obj: dict):
    if obj.get("v") != "role_toolset_matrix_112.v0":
        raise SystemExit("invalid version")
    if obj.get("authority") != "advisory":
        raise SystemExit("authority must be advisory")
    b = obj.get("basis", {})
    if b.get("roles") != 8 or b.get("lanes_per_role") != 7 or b.get("proof_forms_per_lane") != 2:
        raise SystemExit("basis cardinality mismatch")
    if len(obj.get("roles", [])) != 8:
        raise SystemExit("role count mismatch")

    assistants = []
    for role in obj["roles"]:
        lanes = role.get("lane_agents", [])
        if len(lanes) != 7:
            raise SystemExit(f"lane count mismatch for role {role.get('role_id')}")
        for lane in lanes:
            proofs = lane.get("proof_assistants", [])
            if len(proofs) != 2:
                raise SystemExit(f"proof assistant count mismatch for lane {lane.get('lane_id')}")
            names = sorted(p["proof_form"] for p in proofs)
            if names != ["constructive", "falsification"]:
                raise SystemExit(f"proof form mismatch for lane {lane.get('lane_id')}")
            assistants.extend(p["assistant_id"] for p in proofs)
    if len(set(assistants)) != 112:
        raise SystemExit("assistant IDs must be unique and total 112")


def write_json(path: Path, value: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    obj = build()
    validate(obj)

    if args.write:
        write_json(OUT_PATH, obj)
    elif args.verify:
        on_disk = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        if stable_json(on_disk) != stable_json(obj):
            raise SystemExit("role_toolset_matrix_112.v0.json drift")
    else:
        print(json.dumps(obj, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
