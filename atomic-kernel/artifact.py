"""Canonical stream/artifact utilities.

Provides:
- canonical_stream(events) -> bytes
- artifact_hash(bytes_) -> "sha3_256:<hex>"
- deterministic reference fixture freeze/verify helpers
"""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from control_plane import ControlEvent, encode_control, parse_control_stream

ROOT = Path(__file__).resolve().parent
TESTS_DIR = ROOT / "tests"
REF_STREAM_PATH = TESTS_DIR / "reference_stream.bin"
REF_HASH_PATH = TESTS_DIR / "reference_stream_hash.txt"
REFERENCE_TICK = 4


def _to_dict(event: Any) -> dict[str, Any]:
    if is_dataclass(event):
        return asdict(event)
    if isinstance(event, dict):
        return event
    raise TypeError("event must be dataclass or dict")


def canonical_stream(events: list[Any]) -> bytes:
    """Serialize normalized events back to the canonical byte stream."""
    out = bytearray()

    for raw in events:
        e = _to_dict(raw)
        kind = e["payload_kind"]

        if kind == "data":
            out.append(int(e["payload"]) & 0xFF)
            continue

        channel = int(e["channel"])
        lane = int(e["lane"])
        context = int(e["context"])

        if context == 2:
            payload = e.get("payload", {})
            if isinstance(payload, dict) and "char" in payload:
                ext = payload["char"]
            else:
                ext = chr(int(payload.get("codepoint")))
            out.extend(encode_control(channel, lane, context, ext))
        elif context == 3:
            payload = e.get("payload", {})
            ext = payload["algorithm_byte"] if isinstance(payload, dict) else payload
            out.extend(encode_control(channel, lane, context, ext))
        else:
            out.extend(encode_control(channel, lane, context))

    return bytes(out)


def artifact_hash(bytes_: bytes) -> str:
    return "sha3_256:" + hashlib.sha3_256(bytes_).hexdigest()


def build_reference_stream() -> bytes:
    """Reference stream from the annotated control-plane packet (deterministic)."""
    out = bytearray()
    out.extend(encode_control("FS", 0, 0))
    out.extend(b"Hello")
    out.extend(encode_control("GS", 7, 0))
    out.extend(bytes.fromhex("DEAD"))
    out.extend(encode_control("RS", 3, 2, "\u2202"))
    out.extend(encode_control("US", 1, 1))  # lane nibble 0b0001 => DEC / lane-within-ctx=1
    out.extend(bytes.fromhex("4A2F"))
    # High nibble must match B[REFERENCE_TICK % 8] = 9.
    out.extend(encode_control("GS", 0, 3, 0x9A))
    return bytes(out)


def freeze_reference(stream_path: Path = REF_STREAM_PATH, hash_path: Path = REF_HASH_PATH) -> tuple[Path, Path, str]:
    stream = build_reference_stream()
    # Validate parser acceptance using the fixed reference tick.
    parse_control_stream(stream, REFERENCE_TICK)

    stream_path.write_bytes(stream)
    digest = artifact_hash(stream)
    hash_path.write_text(digest + "\n", encoding="utf-8")
    return stream_path, hash_path, digest


def verify_reference(stream_path: Path = REF_STREAM_PATH, hash_path: Path = REF_HASH_PATH) -> bool:
    if not stream_path.exists() or not hash_path.exists():
        return False

    stream = stream_path.read_bytes()
    stored = hash_path.read_text(encoding="utf-8").strip()

    try:
        parse_control_stream(stream, REFERENCE_TICK)
    except Exception:
        return False

    return stored == artifact_hash(stream)


def main() -> int:
    parser = argparse.ArgumentParser(description="Atomic Kernel artifact tools")
    sub = parser.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("hash", help="compute sha3_256 hash for hex bytes")
    h.add_argument("hex_stream")

    fr = sub.add_parser("freeze-reference", help="write reference stream + hash fixtures")
    fr.add_argument("--stream", default=str(REF_STREAM_PATH))
    fr.add_argument("--hash", dest="hash_file", default=str(REF_HASH_PATH))

    vr = sub.add_parser("verify-reference", help="verify frozen reference stream/hash fixtures")
    vr.add_argument("--stream", default=str(REF_STREAM_PATH))
    vr.add_argument("--hash", dest="hash_file", default=str(REF_HASH_PATH))

    cs = sub.add_parser("canonical-stream", help="parse a stream then re-serialize canonically")
    cs.add_argument("hex_stream")
    cs.add_argument("--tick", type=int, default=REFERENCE_TICK)

    args = parser.parse_args()

    if args.cmd == "hash":
        raw = bytes.fromhex(args.hex_stream)
        print(artifact_hash(raw))
        return 0

    if args.cmd == "freeze-reference":
        sp, hp, digest = freeze_reference(Path(args.stream), Path(args.hash_file))
        print(f"WROTE {sp}")
        print(f"WROTE {hp}")
        print(digest)
        return 0

    if args.cmd == "verify-reference":
        ok = verify_reference(Path(args.stream), Path(args.hash_file))
        print("MATCH" if ok else "MISMATCH")
        return 0 if ok else 1

    if args.cmd == "canonical-stream":
        raw = bytes.fromhex(args.hex_stream)
        events = parse_control_stream(raw, args.tick)
        print(canonical_stream(events).hex())
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
