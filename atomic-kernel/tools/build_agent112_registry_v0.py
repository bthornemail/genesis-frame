#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_DOC = ROOT / "docs" / "112_PROOFS_MATRIX.md"
OUT_DIR = ROOT / "narrative_data" / "agent112"

QUESTIONS = [
    ("Q1", "source_of_truth"),
    ("Q2", "system_motion"),
    ("Q3", "payload_control_separation"),
    ("Q4", "projection_meaning_preservation"),
    ("Q5", "intervention_without_replay_loss"),
    ("Q6", "collaboration_without_hidden_authority"),
    ("Q7", "branch_return_without_fragmentation"),
    ("Q8", "open_meaning_closed_law"),
]

ROLE_BY_QUESTION = {
    "Q1": "metatron",
    "Q2": "enoch",
    "Q3": "solomon",
    "Q4": "solon",
    "Q5": "asabiyah",
    "Q6": "writer",
    "Q7": "reader",
    "Q8": "composer",
}

PRIORITY_BAND_BY_QUESTION = {
    "Q1": "critical",
    "Q2": "important",
    "Q3": "critical",
    "Q4": "important",
    "Q5": "critical",
    "Q6": "critical",
    "Q7": "critical",
    "Q8": "expansive",
}

ALGORITHMS = [
    ("A1", "transition"),
    ("A2", "control_plane"),
    ("A3", "projection"),
    ("A4", "escape"),
    ("A5", "fano_path"),
    ("A6", "proposal_receipt"),
    ("A7", "branch_reconciliation"),
]

LANE_ID_BY_ALGORITHM = {
    "A1": "transition",
    "A2": "control",
    "A3": "projection",
    "A4": "escape",
    "A5": "chirality",
    "A6": "proposal",
    "A7": "reconcile",
}

PROOF_FORMS = ["constructive", "falsification"]


def stable_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def must_reject_for(proof_form: str):
    if proof_form == "constructive":
        return ["missing_inputs", "schema_mismatch", "non_deterministic_output"]
    return ["silent_mutation", "authority_escalation", "bypass_commit_boundary"]


def expected_invariant(question_slug: str, algorithm_slug: str, proof_form: str):
    return f"{question_slug}:{algorithm_slug}:{proof_form}:obligation_preserved"


def build():
    matrix_sha = sha256_text(MATRIX_DOC.read_text(encoding="utf-8"))

    cells = []
    agents = []

    for q_idx, (q_id, q_slug) in enumerate(QUESTIONS, start=1):
        for a_idx, (a_id, a_slug) in enumerate(ALGORITHMS, start=1):
            for pf in PROOF_FORMS:
                cell_id = f"{q_id}_{a_id}_{pf}"
                agent_id = f"agent_{cell_id}"
                cell = {
                    "cell_id": cell_id,
                    "question_id": q_id,
                    "question_slug": q_slug,
                    "algorithm_id": a_id,
                    "algorithm_slug": a_slug,
                    "proof_form": pf,
                    "cell_index": len(cells),
                    "expected_invariant": expected_invariant(q_slug, a_slug, pf),
                    "must_reject_conditions": must_reject_for(pf),
                }
                agent = {
                    "agent_id": agent_id,
                    "cell_id": cell_id,
                    "question_id": q_id,
                    "algorithm_id": a_id,
                    "proof_form": pf,
                    "zone_id": q_id,
                    "proposal_lane": "witness.proposal.pending",
                    "receipt_lane": "witness.receipt.audit",
                    "authority": "advisory",
                    "role": "proof_cell_steward",
                    "expected_invariant": cell["expected_invariant"],
                    "must_reject_conditions": cell["must_reject_conditions"],
                }
                cells.append(cell)
                agents.append(agent)

    proof_matrix = {
        "v": "proof_matrix_112.v0",
        "authority": "advisory",
        "cell_count": len(cells),
        "question_count": len(QUESTIONS),
        "algorithm_count": len(ALGORITHMS),
        "proof_form_count": len(PROOF_FORMS),
        "source_matrix_doc": "docs/112_PROOFS_MATRIX.md",
        "source_matrix_sha256": matrix_sha,
        "cells": cells,
    }

    agent_registry = {
        "v": "agent_registry_112.v0",
        "authority": "advisory",
        "agent_count": len(agents),
        "mapping_cardinality": "one_agent_per_cell",
        "source_proof_matrix": "narrative_data/agent112/proof_matrix_112.v0.json",
        "agents": agents,
    }

    proof_matrix["replay_hash"] = sha256_text(stable_json(proof_matrix))
    agent_registry["replay_hash"] = sha256_text(stable_json(agent_registry))

    roles = []
    by_cell = {cell["cell_id"]: cell for cell in cells}
    by_agent_cell = {agent["cell_id"]: agent for agent in agents}

    for q_id, q_slug in QUESTIONS:
        role_id = ROLE_BY_QUESTION[q_id]
        role = {
            "role_id": role_id,
            "question_id": q_id,
            "question_slug": q_slug,
            "priority_band": PRIORITY_BAND_BY_QUESTION[q_id],
            "agents": [],
        }
        for a_id, a_slug in ALGORITHMS:
            lane_id = LANE_ID_BY_ALGORITHM[a_id]
            agent_entry = {
                "algorithm_id": a_id,
                "algorithm_slug": a_slug,
                "lane_id": lane_id,
                "agent_id": f"{role_id}.{lane_id}",
                "assistants": [],
            }
            for pf in PROOF_FORMS:
                cell_id = f"{q_id}_{a_id}_{pf}"
                cell = by_cell[cell_id]
                mapped_agent = by_agent_cell[cell_id]
                agent_entry["assistants"].append(
                    {
                        "assistant_id": f"{role_id}.{lane_id}.{pf}",
                        "proof_form": pf,
                        "cell_id": cell_id,
                        "lane_id": lane_id,
                        "mapped_agent_id": mapped_agent["agent_id"],
                        "expected_invariant": cell["expected_invariant"],
                    }
                )
            role["agents"].append(agent_entry)
        roles.append(role)

    agent_matrix = {
        "v": "agent_matrix_112.v0",
        "authority": "advisory",
        "role_count": len(roles),
        "lane_count_per_role": len(ALGORITHMS),
        "assistant_count_per_lane": len(PROOF_FORMS),
        "assistant_count_total": len(roles) * len(ALGORITHMS) * len(PROOF_FORMS),
        "mapping_formula": "8x7x2",
        "source_proof_matrix": "narrative_data/agent112/proof_matrix_112.v0.json",
        "source_agent_registry": "narrative_data/agent112/agent_registry_112.v0.json",
        "roles": roles,
    }

    agent_matrix["replay_hash"] = sha256_text(stable_json(agent_matrix))

    return proof_matrix, agent_registry, agent_matrix


def validate(proof_matrix, agent_registry, agent_matrix):
    if proof_matrix["cell_count"] != 112:
        raise SystemExit("proof matrix must contain 112 cells")
    if agent_registry["agent_count"] != 112:
        raise SystemExit("agent registry must contain 112 agents")

    cells = {c["cell_id"] for c in proof_matrix["cells"]}
    mapped = {a["cell_id"] for a in agent_registry["agents"]}
    if cells != mapped:
        raise SystemExit("agent/cell mapping mismatch")

    if any(a["authority"] != "advisory" for a in agent_registry["agents"]):
        raise SystemExit("all agents must remain advisory")

    if agent_matrix["role_count"] != 8:
        raise SystemExit("agent matrix must contain 8 roles")
    if agent_matrix["assistant_count_total"] != 112:
        raise SystemExit("agent matrix must contain 112 assistants")
    if agent_matrix.get("authority") != "advisory":
        raise SystemExit("agent matrix authority must remain advisory")

    assistant_ids = []
    mapped_cells = []
    for role in agent_matrix["roles"]:
        if len(role.get("agents", [])) != 7:
            raise SystemExit(f"role lane count mismatch: {role.get('role_id')}")
        if role.get("priority_band") not in {"critical", "important", "expansive"}:
            raise SystemExit(f"invalid priority band: {role.get('role_id')}")
        for lane in role["agents"]:
            if len(lane.get("assistants", [])) != 2:
                raise SystemExit(f"assistant count mismatch: {lane.get('agent_id')}")
            for assistant in lane["assistants"]:
                assistant_ids.append(assistant["assistant_id"])
                mapped_cells.append(assistant["cell_id"])
    if len(set(assistant_ids)) != 112:
        raise SystemExit("assistant ids must be unique")
    if set(mapped_cells) != {c["cell_id"] for c in proof_matrix["cells"]}:
        raise SystemExit("assistant/cell mapping mismatch")


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    proof_matrix, agent_registry, agent_matrix = build()
    validate(proof_matrix, agent_registry, agent_matrix)

    pm_path = OUT_DIR / "proof_matrix_112.v0.json"
    ar_path = OUT_DIR / "agent_registry_112.v0.json"
    am_path = OUT_DIR / "agent_matrix_112.v0.json"

    if args.write:
        write_json(pm_path, proof_matrix)
        write_json(ar_path, agent_registry)
        write_json(am_path, agent_matrix)
    elif args.verify:
        on_disk_pm = json.loads(pm_path.read_text(encoding="utf-8"))
        on_disk_ar = json.loads(ar_path.read_text(encoding="utf-8"))
        on_disk_am = json.loads(am_path.read_text(encoding="utf-8"))
        if stable_json(on_disk_pm) != stable_json(proof_matrix):
            raise SystemExit("proof_matrix_112.v0.json drift")
        if stable_json(on_disk_ar) != stable_json(agent_registry):
            raise SystemExit("agent_registry_112.v0.json drift")
        if stable_json(on_disk_am) != stable_json(agent_matrix):
            raise SystemExit("agent_matrix_112.v0.json drift")
    else:
        print(
            json.dumps(
                {
                    "proof_matrix": proof_matrix,
                    "agent_registry": agent_registry,
                    "agent_matrix": agent_matrix,
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
