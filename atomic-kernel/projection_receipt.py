"""Deterministic multi-projection receipts anchored to canonical state."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def multi_projection_receipt(canonical_state: dict[str, Any]) -> dict[str, Any]:
    src = _stable(canonical_state)
    canon = _hex(src)

    views = {
        "text": {
            "canonical_hash": canon,
            "content": f"text:{canon[:24]}",
        },
        "graph": {
            "canonical_hash": canon,
            "nodes": int(canon[0:2], 16) % 9 + 2,
            "edges": int(canon[2:4], 16) % 17 + 1,
        },
        "svg": {
            "canonical_hash": canon,
            "content": f"<svg data-anchor='{canon[:20]}'/>",
        },
        "obj_mtl": {
            "canonical_hash": canon,
            "obj": f"o ak_{canon[:12]}",
            "mtl": f"newmtl ak_{canon[12:24]}",
        },
        "glb": {
            "canonical_hash": canon,
            "uri": f"glb://{canon[:32]}",
        },
        "xr": {
            "canonical_hash": canon,
            "anchor": canon[:32],
            "mode": "xr",
        },
    }

    receipt = {
        "type": "projection_receipt",
        "version": 1,
        "canonical_hash": canon,
        "views": views,
    }
    return receipt


def projection_receipt_equivalent(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return _stable(a) == _stable(b)


def projection_receipt_anchored(receipt: dict[str, Any]) -> bool:
    canon = str(receipt.get("canonical_hash", ""))
    views = receipt.get("views", {})
    if not canon or not isinstance(views, dict):
        return False
    for v in views.values():
        if not isinstance(v, dict):
            return False
        if str(v.get("canonical_hash", "")) != canon:
            return False
    return True
