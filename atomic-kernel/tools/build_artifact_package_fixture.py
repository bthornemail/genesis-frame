#!/usr/bin/env python3
"""Build/verify deterministic artifact_package fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from artifact_package import create_artifact_package, verify_artifact_package
TESTS = ROOT / "tests"
PAYLOAD_PATH = TESTS / "artifact_package_payload.json"
PACKAGE_PATH = TESTS / "artifact_package_v1.json"
PNG_SHA256_PATH = TESTS / "artifact_package_aztec_png_sha256.txt"


def fixture_payload() -> dict:
    return {
        "type": "atomic_projection_package",
        "version": 1,
        "ui": {
            "frame": "world",
            "plane_tab": "RS",
            "basis": "10",
            "basis_spec_id": "dec_v1",
        },
        "control_plane": {
            "channel": "FS",
            "lane": 0,
            "numsys": 10,
            "basis": "10",
            "basis_spec_id": "dec_v1",
        },
        "semantic": {
            "artifact": None,
            "meta": None,
        },
        "layout": {
            "version": 1,
            "camera": {
                "position": [7, 6, 9],
                "target": [0, 1.2, 0],
            },
            "extraArtifacts": [],
            "objects": [],
        },
    }


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    return "sha256:" + h


def build() -> int:
    payload = fixture_payload()
    pkg = create_artifact_package("projection_package", payload, created_at="2026-03-19T00:00:00Z")

    TESTS.mkdir(parents=True, exist_ok=True)
    write_json(PAYLOAD_PATH, payload)
    write_json(PACKAGE_PATH, pkg)

    if PNG_SHA256_PATH.exists() and not PNG_SHA256_PATH.read_text(encoding="utf-8").strip():
        PNG_SHA256_PATH.write_text("", encoding="utf-8")

    print("WROTE", PAYLOAD_PATH)
    print("WROTE", PACKAGE_PATH)
    return 0


def verify() -> int:
    if not PAYLOAD_PATH.exists() or not PACKAGE_PATH.exists():
        print("MISSING: run with --write first")
        return 2

    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    pkg = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))

    expected = create_artifact_package("projection_package", payload, created_at="2026-03-19T00:00:00Z")
    if pkg != expected:
        print("MISMATCH: package fixture differs from deterministic build")
        return 2

    ok, decoded = verify_artifact_package(pkg)
    if not ok or decoded != payload:
        print("MISMATCH: package verification/decode failed")
        return 2

    if PNG_SHA256_PATH.exists():
        sha = PNG_SHA256_PATH.read_text(encoding="utf-8").strip()
        if sha and not sha.startswith("sha256:"):
            print("MISMATCH: png sha fixture malformed")
            return 2

    print("OK: artifact package fixtures deterministic")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.write:
        return build()
    if args.verify:
        return verify()
    parser.error("use --write or --verify")


if __name__ == "__main__":
    raise SystemExit(main())
