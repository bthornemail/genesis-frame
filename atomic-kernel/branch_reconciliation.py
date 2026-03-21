"""Branch/reconciliation helpers for explicit base+delta+return behavior."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class BranchArtifact:
    type: str
    version: int
    branch_id: str
    parent_lineage_id: str
    base_index: int
    deltas: list[dict[str, Any]]
    prefix_fingerprint: str
    return_to: str


def materialize_branch_artifact(
    canonical_log: list[dict[str, Any]],
    base_index: int,
    deltas: list[dict[str, Any]],
    parent_lineage_id: str = "mainline",
) -> dict[str, Any]:
    total = len(canonical_log)
    base = max(0, min(int(base_index), total))
    prefix = canonical_log[:base]
    fp = hashlib.sha256(_stable(prefix).encode("utf-8")).hexdigest()
    payload = _stable({"base_index": base, "deltas": deltas, "parent_lineage_id": parent_lineage_id})
    bid = "fork_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    artifact = BranchArtifact(
        type="fork_artifact",
        version=1,
        branch_id=bid,
        parent_lineage_id=str(parent_lineage_id),
        base_index=base,
        deltas=[dict(x or {}) for x in deltas],
        prefix_fingerprint=fp,
        return_to="canonical",
    )
    return asdict(artifact)


def replay_branch(canonical_log: list[dict[str, Any]], branch_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    base = int(branch_artifact.get("base_index", 0))
    prefix = canonical_log[:base]
    deltas = [dict(x or {}) for x in branch_artifact.get("deltas", [])]
    return prefix + deltas


def return_to_canonical(canonical_log: list[dict[str, Any]], branch_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    base = int(branch_artifact.get("base_index", 0))
    return canonical_log[:base]


def branch_reconciliation_valid(canonical_log: list[dict[str, Any]], branch_artifact: dict[str, Any]) -> bool:
    base = int(branch_artifact.get("base_index", -1))
    if base < 0 or base > len(canonical_log):
        return False
    if branch_artifact.get("return_to") != "canonical":
        return False
    expected_fp = hashlib.sha256(_stable(canonical_log[:base]).encode("utf-8")).hexdigest()
    return str(branch_artifact.get("prefix_fingerprint", "")) == expected_fp


def reconcile_temporal_views(
    canonical_log: list[dict[str, Any]],
    branch_artifact: dict[str, Any],
    pending_proposals: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Deterministic past/present/future reconciliation summary.

    - past: canonical prefix up to branch base_index
    - present: branch replay (prefix + branch deltas)
    - future: accepted deferred proposals sorted by (apply_at_tick, proposal_id)
    """
    past = return_to_canonical(canonical_log, branch_artifact)
    present = replay_branch(canonical_log, branch_artifact)

    future_items: list[dict[str, Any]] = []
    for raw in (pending_proposals or []):
        item = dict(raw or {})
        if not bool(item.get("accepted", False)):
            continue
        apply_at = int(item.get("apply_at_tick", -1))
        if apply_at < 0:
            continue
        future_items.append(
            {
                "proposal_id": str(item.get("proposal_id", "")),
                "apply_at_tick": apply_at,
                "payload": dict(item.get("payload", {})),
            }
        )
    future_items.sort(key=lambda x: (x["apply_at_tick"], x["proposal_id"]))

    past_hash = hashlib.sha256(_stable(past).encode("utf-8")).hexdigest()
    present_hash = hashlib.sha256(_stable(present).encode("utf-8")).hexdigest()
    future_hash = hashlib.sha256(_stable(future_items).encode("utf-8")).hexdigest()

    return {
        "type": "temporal_reconciliation_receipt",
        "version": 1,
        "branch_id": str(branch_artifact.get("branch_id", "")),
        "base_index": int(branch_artifact.get("base_index", 0)),
        "past_len": len(past),
        "present_len": len(present),
        "future_len": len(future_items),
        "past_hash": past_hash,
        "present_hash": present_hash,
        "future_hash": future_hash,
        "future": future_items,
    }
