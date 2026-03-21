"""Canonical Header8 algorithmic artifact.

Represents one encoded unit as an 8-coordinate header:
(NULL, ESC, FS, GS, RS, US, byte_point, code_block)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

NULL_AXIS = 0x00
ESC_AXIS = 0x1B
FS_AXIS = 0x1C
GS_AXIS = 0x1D
RS_AXIS = 0x1E
US_AXIS = 0x1F

INVARIANT_AXES = (NULL_AXIS, ESC_AXIS, FS_AXIS, GS_AXIS, RS_AXIS, US_AXIS)


class Header8Error(ValueError):
    pass


@dataclass(frozen=True)
class Header8:
    null_axis: int
    esc_axis: int
    fs_axis: int
    gs_axis: int
    rs_axis: int
    us_axis: int
    byte_point: int
    code_block: int


def _require_u8(name: str, value: int) -> int:
    v = int(value)
    if not 0 <= v <= 0xFF:
        raise Header8Error(f"{name} must be in [0x00..0xFF]")
    return v


def make_header8(byte_point: int, code_block: int) -> Header8:
    b = _require_u8("byte_point", byte_point)
    c = int(code_block)
    if c < 0:
        raise Header8Error("code_block must be >= 0")
    return Header8(
        null_axis=NULL_AXIS,
        esc_axis=ESC_AXIS,
        fs_axis=FS_AXIS,
        gs_axis=GS_AXIS,
        rs_axis=RS_AXIS,
        us_axis=US_AXIS,
        byte_point=b,
        code_block=c,
    )


def classify_structural(byte_point: int) -> str:
    b = _require_u8("byte_point", byte_point)
    if b == FS_AXIS:
        return "FS"
    if b == GS_AXIS:
        return "GS"
    if b == RS_AXIS:
        return "RS"
    if b == US_AXIS:
        return "US"
    if b == ESC_AXIS:
        return "ESC"
    if b == NULL_AXIS:
        return "NULL"
    return "PAYLOAD"


def classify_block(code_block: int) -> str:
    c = int(code_block)
    if c < 0:
        raise Header8Error("code_block must be >= 0")
    if c == 0x00:
        return "C0"
    if c == 0x20:
        return "BASIC_TEXT"
    if 0x80 <= c <= 0xEF:
        return "EXTENSION"
    if 0xF0 <= c <= 0xFF:
        return "CUSTOM"
    if c > 0xFF:
        return "CUSTOM_EXTENDED"
    return "RESERVED"


def interpret_header(byte_point: int, code_block: int) -> dict[str, Any]:
    h = make_header8(byte_point, code_block)
    return {
        "header": (
            h.null_axis,
            h.esc_axis,
            h.fs_axis,
            h.gs_axis,
            h.rs_axis,
            h.us_axis,
            h.byte_point,
            h.code_block,
        ),
        "structural_role": classify_structural(h.byte_point),
        "semantic_block": classify_block(h.code_block),
    }


def pack16(byte_point: int, code_block: int) -> int:
    b = _require_u8("byte_point", byte_point)
    c = _require_u8("code_block", code_block)
    return ((b & 0xFF) << 8) | (c & 0xFF)


def unpack16(value: int) -> tuple[int, int]:
    v = int(value)
    if not 0 <= v <= 0xFFFF:
        raise Header8Error("packed value must be in [0x0000..0xFFFF]")
    return ((v >> 8) & 0xFF, v & 0xFF)


def create_header8_artifact(byte_point: int, code_block: int) -> dict[str, Any]:
    h = make_header8(byte_point, code_block)
    packed = None
    if 0 <= h.code_block <= 0xFF:
        packed = f"0x{pack16(h.byte_point, h.code_block):04X}"
    return {
        "type": "header8_artifact",
        "version": 1,
        "basis": {
            "NULL": "0x00",
            "ESC": "0x1B",
            "FS": "0x1C",
            "GS": "0x1D",
            "RS": "0x1E",
            "US": "0x1F",
        },
        "byte_point": f"0x{h.byte_point:02X}",
        "code_block": f"0x{h.code_block:X}",
        "packed16": packed,
        "structural_role": classify_structural(h.byte_point),
        "semantic_block": classify_block(h.code_block),
    }

