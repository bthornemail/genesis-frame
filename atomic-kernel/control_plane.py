"""Canonical control-plane encoding/parsing with COBS framing.

This module follows docs/CONTROL_PLANE_SPEC.md and provides:
- encode_control(channel, lane, context, ext=None) -> bytes
- parse_control_stream(data: bytes, tick: int) -> list[ControlEvent]
- cobs_encode(data: bytes) -> bytes
- cobs_decode(data: bytes) -> bytes
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Any

from crystal import B, T

CHANNEL_CODES = {
    "FS": 0x1C,
    "GS": 0x1D,
    "RS": 0x1E,
    "US": 0x1F,
}
CHANNEL_BY_CODE = {v: k for k, v in CHANNEL_CODES.items()}
CHANNEL_INDEX = {"FS": 0, "GS": 1, "RS": 2, "US": 3}

CONTEXT_NAMES = {
    0: "default",
    1: "numsys",
    2: "unicode",
    3: "extended",
}

NUMSYS_NAMES = {
    0: "DEC",
    1: "BIN",
    2: "HEX",
    3: "B36",
}

ALLOWED_ESCAPE_SCOPES = {
    "next-unit",
    "next-record",
    "next-group",
    "next-file",
    "quoted-literal",
    "structural-region",
}

FORBIDDEN_ESCAPE_SCOPES = {
    "time-based",
    "time",
    "silence-based",
    "silence",
    "external-state",
    "external",
    "implicit-infinite",
    "infinite",
}


class ControlPlaneError(ValueError):
    """Deterministic fail-closed parse error."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def validate_escape_scope(scope: str) -> str:
    """Validate escape scope label under Escape Access Law.

    Time/silence/external/implicit-infinite forms are rejected fail-closed.
    """
    normalized = str(scope or "").strip().lower()
    if normalized in FORBIDDEN_ESCAPE_SCOPES:
        raise ControlPlaneError("ESC_SCOPE_FORBIDDEN", f"forbidden scope form: {normalized}")
    if normalized not in ALLOWED_ESCAPE_SCOPES:
        raise ControlPlaneError("ESC_SCOPE_UNKNOWN", f"unknown scope form: {normalized}")
    return normalized


def canonical_escape_scope_active(mode: str, scope_depth: int = 0, projection_paused: bool = False) -> bool:
    """Canonical scope authority function.

    `projection_paused` is intentionally ignored to enforce:
    local UI/projection pause MUST NOT define canonical escape scope.
    """
    _ = projection_paused
    m = str(mode or "").strip().upper()
    return m in {"ESCAPE_PENDING", "CONTROL", "QUOTED_LITERAL"} or int(scope_depth) > 0


@dataclass(frozen=True)
class ControlEvent:
    channel: int
    lane: int
    context: int
    payload_kind: str
    payload: Any
    tick: int


def _channel_code(channel: int | str) -> int:
    if isinstance(channel, int):
        if channel in CHANNEL_BY_CODE:
            return channel
        if channel in (0, 1, 2, 3):
            return CHANNEL_CODES[["FS", "GS", "RS", "US"][channel]]
        raise ValueError("channel int must be byte 0x1C..0x1F or index 0..3")
    key = channel.upper()
    if key in CHANNEL_CODES:
        return CHANNEL_CODES[key]
    raise ValueError("channel str must be one of FS/GS/RS/US")


def encode_control(channel: int | str, lane: int, context: int, ext: Any = None) -> bytes:
    """Encode one control sequence."""
    ch = _channel_code(channel)
    if not 0 <= lane <= 15:
        raise ValueError("lane must be in [0, 15]")
    if context not in (0, 1, 2, 3):
        raise ValueError("context must be in [0, 3]")

    mask = ((lane & 0x0F) << 4) | ((context & 0x03) << 2) | 0x03
    out = bytearray([ch, mask])

    if context == 2:
        if ext is None:
            raise ValueError("CT=10 (unicode) requires ext (single codepoint)")
        if isinstance(ext, int):
            if not 0 <= ext <= 0x10FFFF:
                raise ValueError("unicode codepoint out of range")
            cp = chr(ext)
        else:
            cp = str(ext)
        if len(cp) != 1:
            raise ValueError("unicode ext must be exactly one codepoint")
        out.extend(cp.encode("utf-8"))
    elif context == 3:
        if ext is None:
            raise ValueError("CT=11 (extended) requires ext byte 0..255")
        ext_byte = int(ext)
        if not 0 <= ext_byte <= 0xFF:
            raise ValueError("extended ext must be in [0, 255]")
        out.append(ext_byte)

    return bytes(out)


def _read_one_utf8_codepoint(data: bytes, start: int) -> tuple[str, bytes, int]:
    if start >= len(data):
        raise ControlPlaneError("CT10_MISSING_UTF8", "missing UTF-8 bytes after CT=10")

    first = data[start]
    if first <= 0x7F:
        need = 1
    elif 0xC2 <= first <= 0xDF:
        need = 2
    elif 0xE0 <= first <= 0xEF:
        need = 3
    elif 0xF0 <= first <= 0xF4:
        need = 4
    else:
        raise ControlPlaneError("CT10_INVALID_UTF8", f"invalid UTF-8 lead byte 0x{first:02X}")

    end = start + need
    if end > len(data):
        raise ControlPlaneError("CT10_INVALID_UTF8", "truncated UTF-8 codepoint")
    chunk = data[start:end]

    try:
        char = chunk.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ControlPlaneError("CT10_INVALID_UTF8", str(exc)) from exc

    cp = ord(char)
    if 0xD800 <= cp <= 0xDFFF:
        raise ControlPlaneError("CT10_INVALID_UTF8", "surrogate codepoint is forbidden")

    return char, chunk, need


def parse_control_stream(data: bytes, tick: int) -> list[ControlEvent]:
    """Parse a canonical unstuffed control stream.

    Fail-closed rules:
    - channel byte missing/invalid mask marker
    - invalid CT=10 UTF-8 codepoint sequence
    - CT=11 algorithm selector mismatch
    """
    events: list[ControlEvent] = []
    i = 0

    while i < len(data):
        b = data[i]
        if b in CHANNEL_BY_CODE:
            if i + 1 >= len(data):
                raise ControlPlaneError("MISSING_MASK", "channel byte at end of stream")
            mask = data[i + 1]
            if (mask & 0x03) != 0x03:
                raise ControlPlaneError("INVALID_MASK_MARKER", f"mask 0x{mask:02X} does not end in binary 11")

            lane = (mask >> 4) & 0x0F
            context = (mask >> 2) & 0x03
            channel_name = CHANNEL_BY_CODE[b]
            i += 2

            if context == 0:
                payload_kind = "control"
                payload: Any = {"channel_name": channel_name, "mask": mask}
            elif context == 1:
                numsys = (lane >> 2) & 0x03
                lane_in_ctx = lane & 0x03
                payload_kind = "numsys"
                payload = {
                    "channel_name": channel_name,
                    "mask": mask,
                    "numsys_code": numsys,
                    "numsys": NUMSYS_NAMES[numsys],
                    "lane_within_ctx": lane_in_ctx,
                }
            elif context == 2:
                char, utf8_bytes, consumed = _read_one_utf8_codepoint(data, i)
                i += consumed
                payload_kind = "unicode"
                payload = {
                    "channel_name": channel_name,
                    "mask": mask,
                    "char": char,
                    "codepoint": ord(char),
                    "utf8": utf8_bytes.hex().upper(),
                }
            else:
                if i >= len(data):
                    raise ControlPlaneError("CT11_MISSING_EXT", "missing algorithm byte after CT=11")
                algo_byte = data[i]
                i += 1
                expected = B[tick % T] & 0x0F
                selector = (algo_byte >> 4) & 0x0F
                if selector != expected:
                    raise ControlPlaneError(
                        "CT11_ALGO_MISMATCH",
                        f"selector=0x{selector:X} expected=0x{expected:X} for tick={tick}",
                    )
                payload_kind = "extended"
                payload = {
                    "channel_name": channel_name,
                    "mask": mask,
                    "algorithm_byte": algo_byte,
                    "algorithm_selector": selector,
                    "algorithm_param": algo_byte & 0x0F,
                }

            events.append(
                ControlEvent(
                    channel=CHANNEL_INDEX[channel_name],
                    lane=lane,
                    context=context,
                    payload_kind=payload_kind,
                    payload=payload,
                    tick=tick,
                )
            )
            continue

        events.append(
            ControlEvent(
                channel=-1,
                lane=-1,
                context=0,
                payload_kind="data",
                payload=b,
                tick=tick,
            )
        )
        i += 1

    return events


def cobs_encode(data: bytes) -> bytes:
    """COBS-encode one payload frame (without trailing 0x00 delimiter)."""
    if not data:
        return b"\x01"

    out = bytearray()
    code_pos = len(out)
    out.append(0)
    code = 1

    for b in data:
        if b == 0:
            out[code_pos] = code
            code_pos = len(out)
            out.append(0)
            code = 1
        else:
            out.append(b)
            code += 1
            if code == 0xFF:
                out[code_pos] = code
                code_pos = len(out)
                out.append(0)
                code = 1

    out[code_pos] = code
    return bytes(out)


def cobs_decode(data: bytes) -> bytes:
    """COBS-decode one payload frame (without trailing 0x00 delimiter)."""
    if not data:
        raise ControlPlaneError("COBS_EMPTY", "empty COBS frame")
    if 0 in data:
        raise ControlPlaneError("COBS_ZERO_IN_FRAME", "COBS frame cannot contain 0x00")

    out = bytearray()
    i = 0
    n = len(data)

    while i < n:
        code = data[i]
        if code == 0:
            raise ControlPlaneError("COBS_BAD_CODE", "encountered code byte 0x00")
        i += 1

        end = i + code - 1
        if end > n:
            raise ControlPlaneError("COBS_OVERRUN", "code byte overruns frame length")

        out.extend(data[i:end])
        i = end

        if code != 0xFF and i < n:
            out.append(0)

    return bytes(out)


def _events_json(events: list[ControlEvent]) -> str:
    return json.dumps([asdict(e) for e in events], indent=2, sort_keys=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Atomic Kernel control-plane tools")
    sub = parser.add_subparsers(dest="cmd", required=True)

    enc = sub.add_parser("encode", help="encode one control sequence")
    enc.add_argument("channel", help="FS/GS/RS/US or 0..3")
    enc.add_argument("lane", type=int)
    enc.add_argument("context", type=int, help="0=default 1=numsys 2=unicode 3=extended")
    enc.add_argument("--ext", default=None, help="unicode char/codepoint or extended byte")

    dec = sub.add_parser("decode", help="parse a raw hex stream")
    dec.add_argument("hex_stream", help="hex bytes, e.g. 1c034865")
    dec.add_argument("--tick", type=int, default=0)

    ver = sub.add_parser("verify", help="parse stream and report OK/FAIL")
    ver.add_argument("hex_stream")
    ver.add_argument("--tick", type=int, default=0)

    cenc = sub.add_parser("cobs-encode", help="COBS encode a raw hex stream")
    cenc.add_argument("hex_stream")

    cdec = sub.add_parser("cobs-decode", help="COBS decode a frame hex stream")
    cdec.add_argument("hex_stream")

    args = parser.parse_args()

    if args.cmd == "encode":
        channel: int | str
        if args.channel.isdigit():
            channel = int(args.channel)
        else:
            channel = args.channel

        ext: Any = args.ext
        if args.context == 3 and ext is not None:
            ext = int(ext, 0)
        elif args.context == 2 and ext is not None:
            try:
                if ext.lower().startswith("0x"):
                    ext = int(ext, 16)
            except (ValueError, AttributeError):
                pass

        print(encode_control(channel, args.lane, args.context, ext).hex())
        return 0

    if args.cmd == "decode":
        raw = bytes.fromhex(args.hex_stream)
        print(_events_json(parse_control_stream(raw, args.tick)))
        return 0

    if args.cmd == "verify":
        raw = bytes.fromhex(args.hex_stream)
        parse_control_stream(raw, args.tick)
        print("OK")
        return 0

    if args.cmd == "cobs-encode":
        raw = bytes.fromhex(args.hex_stream)
        print(cobs_encode(raw).hex())
        return 0

    if args.cmd == "cobs-decode":
        raw = bytes.fromhex(args.hex_stream)
        print(cobs_decode(raw).hex())
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
