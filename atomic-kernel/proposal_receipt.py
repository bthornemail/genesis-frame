"""Deferred proposal / receipt helpers for lawful next-frame commit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DeferredProposal:
    proposal_id: str
    created_tick: int
    apply_at_tick: int
    payload: dict[str, Any]
    accepted: bool = False


def defer_proposal(proposal_id: str, payload: dict[str, Any], current_tick: int) -> DeferredProposal:
    tick = max(0, int(current_tick))
    return DeferredProposal(
        proposal_id=str(proposal_id),
        created_tick=tick,
        apply_at_tick=tick + 1,
        payload=dict(payload or {}),
        accepted=False,
    )


def accept_proposal(proposal: DeferredProposal) -> DeferredProposal:
    return DeferredProposal(
        proposal_id=proposal.proposal_id,
        created_tick=proposal.created_tick,
        apply_at_tick=proposal.apply_at_tick,
        payload=dict(proposal.payload),
        accepted=True,
    )


def commit_proposal(proposal: DeferredProposal, tick: int) -> tuple[bool, dict[str, Any] | None]:
    now = max(0, int(tick))
    if not proposal.accepted:
        return False, None
    if now < proposal.apply_at_tick:
        return False, None
    receipt = {
        "type": "proposal_receipt",
        "proposal_id": proposal.proposal_id,
        "applied_tick": now,
        "apply_at_tick": proposal.apply_at_tick,
        "payload": dict(proposal.payload),
        "status": "applied",
    }
    return True, receipt
