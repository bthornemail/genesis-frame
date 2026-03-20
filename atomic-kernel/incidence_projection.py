"""Deterministic incidence projection law over shared ticks.

This module defines a projection-family scheduler using a canonical
7-point Fano incidence schedule and the existing basis-spec algebra.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from basis_spec import BasisSpec, normalize_basis_spec, project_value

PLANES = ("FS", "GS", "RS", "US")

FANO_LINES: tuple[tuple[int, int, int], ...] = (
    (0, 1, 3),
    (0, 2, 5),
    (0, 4, 6),
    (1, 2, 4),
    (1, 5, 6),
    (2, 3, 6),
    (3, 4, 5),
)


def fano_triplet(tick: int) -> tuple[int, int, int]:
    idx = int(tick) % len(FANO_LINES)
    return FANO_LINES[idx]


def frame_at_tick(tick: int, basis_spec: dict[str, Any] | BasisSpec, plane: str = "RS") -> dict[str, Any]:
    p = str(plane).upper()
    if p not in PLANES:
        raise ValueError(f"invalid plane: {plane}")
    spec = normalize_basis_spec(basis_spec)
    return {
        "tick": int(tick),
        "plane": p,
        "basis_spec": spec,
        "triplet": fano_triplet(tick),
    }


def project_entity(entity_state: Any, plane: str, frame: dict[str, Any]) -> dict[str, Any]:
    p = str(plane).upper()
    if p not in PLANES:
        raise ValueError(f"invalid plane: {plane}")
    triplet = frame.get("triplet")
    if not isinstance(triplet, tuple) or len(triplet) != 3:
        raise ValueError("frame.triplet must be a tuple of size 3")
    basis_spec = normalize_basis_spec(frame.get("basis_spec"))
    seed = _projection_seed(entity_state, p, triplet)
    return project_value(seed, p, basis_spec)


def projection_vector(entity_state: Any, frame: dict[str, Any]) -> list[dict[str, Any]]:
    return [project_entity(entity_state, p, frame) for p in PLANES]


def is_collapsed(projections: list[dict[str, Any]]) -> bool:
    if not projections:
        return True
    first = projections[0]
    return all(p == first for p in projections)


def is_divergent(projections: list[dict[str, Any]]) -> bool:
    return not is_collapsed(projections)


def classify_entity(entity_state: Any, frame: dict[str, Any]) -> str:
    pv = projection_vector(entity_state, frame)
    return "collapsed" if is_collapsed(pv) else "divergent"


def continuation_surface(entity_state: Any, frame: dict[str, Any]) -> list[dict[str, Any]]:
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for p in projection_vector(entity_state, frame):
        key = json.dumps(p, sort_keys=True, separators=(",", ":"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


def select_continuation(surface: list[dict[str, Any]], index: int) -> dict[str, Any]:
    if not surface:
        raise ValueError("surface must be non-empty")
    idx = int(index) % len(surface)
    return surface[idx]


def step_projection(entity_state: Any, tick: int, basis_spec: dict[str, Any] | BasisSpec) -> dict[str, Any]:
    frame = frame_at_tick(tick, basis_spec)
    pv = projection_vector(entity_state, frame)
    if is_collapsed(pv):
        return {
            "tick": int(tick),
            "frame": {
                "plane": frame["plane"],
                "basis_spec_id": frame["basis_spec"].id,
                "triplet": frame["triplet"],
            },
            "kind": "collapsed",
            "value": pv[0],
        }
    surf = continuation_surface(entity_state, frame)
    return {
        "tick": int(tick),
        "frame": {
            "plane": frame["plane"],
            "basis_spec_id": frame["basis_spec"].id,
            "triplet": frame["triplet"],
        },
        "kind": "divergent",
        "surface": surf,
    }


def _projection_seed(entity_state: Any, plane: str, triplet: tuple[int, int, int]) -> int:
    body = json.dumps(
        {"entity_state": entity_state, "plane": plane, "triplet": list(triplet)},
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    digest = hashlib.sha3_256(body).digest()
    return int.from_bytes(digest[:4], "big")
