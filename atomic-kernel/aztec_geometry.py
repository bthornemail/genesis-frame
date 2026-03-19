"""Normative 27x27 Aztec coordinate mapping for 60 canonical states."""

from __future__ import annotations

from dataclasses import dataclass

GRID_SIZE = 27
CENTER = (13, 13)

CHANNEL_NAMES = {0: "US", 1: "RS", 2: "GS", 3: "FS"}
QUAD_NAMES = {0: "TR", 1: "BR", 2: "BL", 3: "TL"}

# lane -> (x, y, r, quadrant) for each channel
_COORDS: dict[int, dict[int, tuple[int, int, int, int]]] = {
    0: {
        1: (17, 13, 4, 1), 2: (16, 17, 4, 1), 3: (11, 17, 4, 2), 4: (9, 15, 4, 2),
        5: (9, 11, 4, 3), 6: (12, 9, 4, 3), 7: (18, 8, 5, 0), 8: (18, 12, 5, 0),
        9: (18, 16, 5, 1), 10: (15, 18, 5, 1), 11: (10, 18, 5, 2), 12: (8, 16, 5, 2),
        13: (8, 12, 5, 3), 14: (9, 8, 5, 3), 15: (14, 8, 5, 0),
    },
    1: {
        1: (19, 13, 6, 1), 2: (18, 19, 6, 1), 3: (11, 19, 6, 2), 4: (7, 17, 6, 2),
        5: (7, 11, 6, 3), 6: (10, 7, 6, 3), 7: (17, 7, 6, 0), 8: (20, 10, 7, 0),
        9: (20, 16, 7, 1), 10: (17, 20, 7, 1), 11: (10, 20, 7, 2), 12: (6, 18, 7, 2),
        13: (6, 12, 7, 3), 14: (7, 6, 7, 3), 15: (14, 6, 7, 0),
    },
    2: {
        1: (21, 13, 8, 1), 2: (20, 21, 8, 1), 3: (11, 21, 8, 2), 4: (5, 19, 8, 2),
        5: (5, 11, 8, 3), 6: (8, 5, 8, 3), 7: (17, 5, 8, 0), 8: (22, 8, 9, 0),
        9: (22, 16, 9, 1), 10: (19, 22, 9, 1), 11: (10, 22, 9, 2), 12: (4, 20, 9, 2),
        13: (4, 12, 9, 3), 14: (5, 4, 9, 3), 15: (14, 4, 9, 0),
    },
    3: {
        1: (23, 13, 10, 1), 2: (22, 23, 10, 1), 3: (11, 23, 10, 2), 4: (3, 21, 10, 2),
        5: (3, 11, 10, 3), 6: (6, 3, 10, 3), 7: (17, 3, 10, 0), 8: (24, 6, 11, 0),
        9: (24, 16, 11, 1), 10: (21, 24, 11, 1), 11: (10, 24, 11, 2), 12: (2, 22, 11, 2),
        13: (2, 12, 11, 3), 14: (3, 2, 11, 3), 15: (14, 2, 11, 0),
    },
}

NULL_LANE_POSITIONS = {
    0: (13, 9, 4),
    1: (13, 6, 7),
    2: (13, 4, 9),
    3: (13, 2, 11),
}


@dataclass(frozen=True)
class AztecCoord:
    channel: int
    channel_name: str
    lane: int
    lane_bits: str
    x: int
    y: int
    r: int
    quadrant: int
    quadrant_name: str


def coordinates_for(channel: int, lane: int) -> AztecCoord:
    if channel not in _COORDS:
        raise ValueError("channel must be 0..3")
    if lane not in _COORDS[channel]:
        raise ValueError("lane must be 1..15 for canonical data coordinates")

    x, y, r, q = _COORDS[channel][lane]
    return AztecCoord(
        channel=channel,
        channel_name=CHANNEL_NAMES[channel],
        lane=lane,
        lane_bits=f"{lane:04b}",
        x=x,
        y=y,
        r=r,
        quadrant=q,
        quadrant_name=QUAD_NAMES[q],
    )


def coordinate_table() -> list[AztecCoord]:
    out = []
    for ch in range(4):
        for lane in range(1, 16):
            out.append(coordinates_for(ch, lane))
    return out


def chebyshev_r(x: int, y: int) -> int:
    cx, cy = CENTER
    dx = x - cx
    dy = y - cy
    return max(abs(dx), abs(dy))


def validate_coordinate_table() -> dict[str, int | bool]:
    table = coordinate_table()
    unique = {(c.x, c.y) for c in table}
    in_bounds = all(0 <= c.x < GRID_SIZE and 0 <= c.y < GRID_SIZE for c in table)
    ring_ok = all(chebyshev_r(c.x, c.y) == c.r for c in table)
    per_channel_ok = all(sum(1 for c in table if c.channel == ch) == 15 for ch in range(4))

    return {
        "entries": len(table),
        "unique_positions": len(unique),
        "in_bounds": in_bounds,
        "ring_match": ring_ok,
        "per_channel_15": per_channel_ok,
    }


if __name__ == "__main__":
    summary = validate_coordinate_table()
    print(summary)
