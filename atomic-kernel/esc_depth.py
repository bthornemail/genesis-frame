"""Algorithm A13: ESC-depth mixed-radix coordinate header."""

from __future__ import annotations

from itertools import combinations
from typing import Any

from basis_spec import mixed_decode, mixed_encode

ESC_CODE = 0x1B

BASIS_SYMBOLS = ("NULL", "ESC", "FS", "GS", "RS", "US", "0x&&", "0x??")
ACTIVE_SYMBOLS = ("ESC", "FS", "GS", "RS", "US", "0x&&", "0x??")

LOW_TICKETS = (
    ("NULL", "ESC", "RS"),
    ("NULL", "FS", "US"),
    ("NULL", "GS", "0x??"),
    ("ESC", "FS", "0x??"),
    ("ESC", "GS", "US"),
    ("FS", "GS", "RS"),
    ("RS", "US", "0x??"),
)

HIGH_TICKETS = (
    ("ESC", "FS", "US"),
    ("ESC", "GS", "0x&&"),
    ("ESC", "RS", "0x??"),
    ("FS", "GS", "0x??"),
    ("FS", "RS", "0x&&"),
    ("GS", "RS", "US"),
    ("US", "0x&&", "0x??"),
)

ALL_TICKETS = LOW_TICKETS + HIGH_TICKETS


def count_leading_esc(stream: list[int] | tuple[int, ...], esc_code: int = ESC_CODE) -> int:
    c = 0
    for b in stream:
        if int(b) != int(esc_code):
            break
        c += 1
    return c


def radices_for_depth(depth: int) -> list[int]:
    d = int(depth)
    if d < 1:
        raise ValueError("depth must be >= 1")
    if d == 1:
        return []
    if d == 2:
        return [128]
    if d == 3:
        return [36, 8]
    if d == 4:
        return [256, 65536]
    # Extension convention: preserve A13 base then append one radix per depth.
    out = [256, 65536]
    out.extend([65536] * (d - 4))
    return out


def esc_encode(value: int, depth: int, esc_code: int = ESC_CODE) -> list[int]:
    d = int(depth)
    if d < 1:
        raise ValueError("depth must be >= 1")
    v = int(value)
    if v < 0:
        raise ValueError("value must be >= 0")
    prefix = [int(esc_code)] * d
    if d == 1:
        return prefix + [v]
    rad = radices_for_depth(d)
    coords = mixed_encode(v, rad)
    return prefix + coords


def _decode_with_depth(data: list[int], depth: int) -> dict[str, Any]:
    if depth < 1:
        raise ValueError("depth must be >= 1")
    rest = data[depth:]
    rad = radices_for_depth(depth)
    need = 1 if depth == 1 else (len(rad) + 1)
    if len(rest) < need:
        raise ValueError("insufficient coordinate payload for depth")
    coords = rest[:need]
    if depth == 1:
        value = int(coords[0])
    else:
        value = mixed_decode(coords, rad)
    return {
        "depth": depth,
        "value": value,
        "radices": rad,
        "coords": coords,
        "rest": rest[need:],
    }


def esc_decode(
    stream: list[int] | tuple[int, ...],
    esc_code: int = ESC_CODE,
    depth: int | None = None,
) -> dict[str, Any]:
    data = [int(x) for x in stream]
    if depth is not None:
        return _decode_with_depth(data, int(depth))
    max_depth = count_leading_esc(data, esc_code=esc_code)
    if max_depth < 1:
        raise ValueError("stream does not start with ESC prefix")
    for candidate in range(max_depth, 0, -1):
        try:
            return _decode_with_depth(data, candidate)
        except ValueError:
            continue
    raise ValueError("unable to infer valid ESC depth from stream")


def pair_coverage(tickets: tuple[tuple[str, str, str], ...], symbols: tuple[str, ...]) -> bool:
    pairs = set()
    for t in tickets:
        for a, b in combinations(sorted(t), 2):
            pairs.add((a, b))
    required = set(tuple(sorted(p)) for p in combinations(symbols, 2))
    return required.issubset(pairs)


def transylvania_coverage_report() -> dict[str, Any]:
    null_only_low = all(("NULL" not in t) for t in HIGH_TICKETS)
    active_full = pair_coverage(ALL_TICKETS, ACTIVE_SYMBOLS)
    return {
        "ticket_count": len(ALL_TICKETS),
        "null_only_low": null_only_low,
        "active_pair_coverage": active_full,
    }
