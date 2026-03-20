"""Canonical basis-spec algebra for reversible projection.

This module defines deterministic basis specification validation,
projection, interpretation, and canonicalization helpers.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

BASIS_KINDS = {"2", "8", "10", "16", "36", "codepoint", "mixed"}


@dataclass(frozen=True)
class BasisSpec:
    type: str
    id: str
    kind: str
    version: int = 1
    radices: tuple[int, ...] = ()
    labels: tuple[str, ...] = ("value",)


def normalize_basis_spec(spec: dict[str, Any] | BasisSpec) -> BasisSpec:
    if isinstance(spec, BasisSpec):
        obj = spec
    else:
        if not isinstance(spec, dict):
            raise ValueError("basis_spec must be a dict")
        kind = str(spec.get("kind", "")).strip()
        if kind not in BASIS_KINDS:
            raise ValueError(f"invalid basis kind: {kind}")
        spec_id = str(spec.get("id", "")).strip()
        if not spec_id:
            raise ValueError("basis_spec.id is required")
        version = int(spec.get("version", 1))
        labels = tuple(str(x) for x in spec.get("labels", ["value"]))
        radices: tuple[int, ...]
        if kind == "mixed":
            src = spec.get("radices")
            if not isinstance(src, list) or not src:
                raise ValueError("mixed basis requires non-empty radices")
            vals = tuple(int(x) for x in src)
            if any(v < 2 for v in vals):
                raise ValueError("mixed radices must be >= 2")
            radices = vals
        else:
            radices = ()
        obj = BasisSpec(
            type="basis_spec",
            id=spec_id,
            kind=kind,
            version=version,
            radices=radices,
            labels=labels,
        )

    if obj.type != "basis_spec":
        raise ValueError("basis_spec.type must be 'basis_spec'")
    if not obj.id:
        raise ValueError("basis_spec.id is required")
    if obj.kind not in BASIS_KINDS:
        raise ValueError(f"invalid basis kind: {obj.kind}")
    if obj.version < 1:
        raise ValueError("basis_spec.version must be >= 1")
    if obj.kind == "mixed":
        if not obj.radices:
            raise ValueError("mixed basis requires radices")
        if any((not isinstance(r, int)) or r < 2 for r in obj.radices):
            raise ValueError("mixed radices must be integers >= 2")
    return obj


def basis_spec_to_dict(spec: BasisSpec) -> dict[str, Any]:
    out: dict[str, Any] = {
        "type": "basis_spec",
        "id": spec.id,
        "kind": spec.kind,
        "version": spec.version,
        "labels": list(spec.labels),
    }
    if spec.kind == "mixed":
        out["radices"] = list(spec.radices)
    return out


def canonical_basis_spec_json(spec: dict[str, Any] | BasisSpec) -> str:
    norm = normalize_basis_spec(spec)
    return json.dumps(basis_spec_to_dict(norm), sort_keys=True, separators=(",", ":"))


def basis_spec_fingerprint(spec: dict[str, Any] | BasisSpec) -> str:
    raw = canonical_basis_spec_json(spec).encode("utf-8")
    return "sha3_256:" + hashlib.sha3_256(raw).hexdigest()


def mixed_encode(value: int, radices: list[int] | tuple[int, ...]) -> list[int]:
    if value < 0:
        raise ValueError("value must be >= 0")
    vals = tuple(int(r) for r in radices)
    if not vals or any(r < 2 for r in vals):
        raise ValueError("radices must be non-empty integers >= 2")
    v = int(value)
    coords: list[int] = []
    for r in vals:
        coords.append(v % r)
        v //= r
    coords.append(v)
    return coords


def mixed_decode(coords: list[int] | tuple[int, ...], radices: list[int] | tuple[int, ...]) -> int:
    vals = tuple(int(r) for r in radices)
    if not vals or any(r < 2 for r in vals):
        raise ValueError("radices must be non-empty integers >= 2")
    if len(coords) != len(vals) + 1:
        raise ValueError("coords length must equal len(radices)+1")
    v = int(coords[-1])
    if v < 0:
        raise ValueError("tail coord must be >= 0")
    for i in range(len(vals) - 1, -1, -1):
        c = int(coords[i])
        r = vals[i]
        if c < 0 or c >= r:
            raise ValueError("coordinate out of range for radix")
        v = c + r * v
    return v


def project_value(value: int, plane: str, spec: dict[str, Any] | BasisSpec) -> dict[str, Any]:
    norm = normalize_basis_spec(spec)
    v = int(value)
    p = str(plane)

    if norm.kind == "2":
        rendered: Any = f"0b{v:b}"
    elif norm.kind == "8":
        rendered = f"0o{v:o}"
    elif norm.kind == "10":
        rendered = str(v)
    elif norm.kind == "16":
        rendered = f"0x{v:X}"
    elif norm.kind == "36":
        rendered = _to_base36(v)
    elif norm.kind == "codepoint":
        rendered = f"U+{v:04X}"
    else:
        rendered = {
            "coords": mixed_encode(v, norm.radices),
            "radices": list(norm.radices),
        }

    return {
        "plane": p,
        "basis_spec_id": norm.id,
        "basis": norm.kind,
        "rendered": rendered,
    }


def interpret_value(representation: Any, plane: str, spec: dict[str, Any] | BasisSpec) -> int:
    _ = str(plane)
    norm = normalize_basis_spec(spec)

    if norm.kind == "2":
        return int(str(representation).lower().removeprefix("0b"), 2)
    if norm.kind == "8":
        return int(str(representation).lower().removeprefix("0o"), 8)
    if norm.kind == "10":
        return int(str(representation), 10)
    if norm.kind == "16":
        return int(str(representation).lower().removeprefix("0x"), 16)
    if norm.kind == "36":
        return int(str(representation), 36)
    if norm.kind == "codepoint":
        return int(str(representation).upper().removeprefix("U+"), 16)

    if not isinstance(representation, dict):
        raise ValueError("mixed representation must be an object")
    coords = representation.get("coords")
    if not isinstance(coords, list):
        raise ValueError("mixed representation must include coords[]")
    return mixed_decode([int(x) for x in coords], norm.radices)


def default_basis_specs() -> list[BasisSpec]:
    return [
        normalize_basis_spec({"type": "basis_spec", "id": "bin_v1", "kind": "2", "version": 1, "labels": ["value"]}),
        normalize_basis_spec({"type": "basis_spec", "id": "oct_v1", "kind": "8", "version": 1, "labels": ["value"]}),
        normalize_basis_spec({"type": "basis_spec", "id": "dec_v1", "kind": "10", "version": 1, "labels": ["value"]}),
        normalize_basis_spec({"type": "basis_spec", "id": "hex_v1", "kind": "16", "version": 1, "labels": ["value"]}),
        normalize_basis_spec({"type": "basis_spec", "id": "base36_v1", "kind": "36", "version": 1, "labels": ["value"]}),
        normalize_basis_spec({"type": "basis_spec", "id": "codepoint_v1", "kind": "codepoint", "version": 1, "labels": ["codepoint"]}),
        normalize_basis_spec({"type": "basis_spec", "id": "orbit_offset_v1", "kind": "mixed", "version": 1, "radices": [36], "labels": ["offset", "orbit"]}),
        normalize_basis_spec({"type": "basis_spec", "id": "channel_lane_v1", "kind": "mixed", "version": 1, "radices": [16], "labels": ["lane", "channel"]}),
    ]


def _to_base36(v: int) -> str:
    if v < 0:
        raise ValueError("value must be >= 0")
    if v == 0:
        return "0"
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    out = []
    x = v
    while x > 0:
        x, r = divmod(x, 36)
        out.append(chars[r])
    return "".join(reversed(out))
