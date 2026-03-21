"""Canonical artifact_package.v1 helpers.

Carrier is transport-only. This module validates and verifies packages before use.
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from typing import Any

ALLOWED_ARTIFACT_KINDS = (
    "projection_package",
    "semantic_graph_artifact",
    "progression_template",
    "control_diagram_artifact",
    "header8_artifact",
)


class ArtifactPackageError(ValueError):
    pass


@dataclass(frozen=True)
class ArtifactPackage:
    type: str
    version: int
    artifact_kind: str
    payload_encoding: str
    payload_b64: str
    fingerprint_algo: str
    fingerprint: str
    created_at: str = ""


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def payload_bytes(payload_obj: Any) -> bytes:
    return canonical_json(payload_obj).encode("utf-8")


def payload_fingerprint_sha256(payload_obj: Any) -> str:
    b = payload_bytes(payload_obj)
    return "sha256:" + hashlib.sha256(b).hexdigest()


def create_artifact_package(artifact_kind: str, payload_obj: Any, *, created_at: str = "") -> dict[str, Any]:
    kind = str(artifact_kind)
    if kind not in ALLOWED_ARTIFACT_KINDS:
        raise ArtifactPackageError(f"unsupported artifact_kind: {kind}")

    b = payload_bytes(payload_obj)
    fp = "sha256:" + hashlib.sha256(b).hexdigest()
    pkg: dict[str, Any] = {
        "type": "artifact_package",
        "version": 1,
        "artifact_kind": kind,
        "payload_encoding": "utf8-json",
        "payload_b64": base64.b64encode(b).decode("ascii"),
        "fingerprint_algo": "sha256",
        "fingerprint": fp,
    }
    if created_at:
        pkg["created_at"] = created_at
    return pkg


def verify_artifact_package(pkg: dict[str, Any]) -> tuple[bool, Any]:
    if not isinstance(pkg, dict):
        raise ArtifactPackageError("package must be an object")
    if pkg.get("type") != "artifact_package" or int(pkg.get("version", -1)) != 1:
        raise ArtifactPackageError("unsupported package type/version")
    kind = str(pkg.get("artifact_kind", ""))
    if kind not in ALLOWED_ARTIFACT_KINDS:
        raise ArtifactPackageError(f"unsupported artifact_kind: {kind}")
    if pkg.get("payload_encoding") != "utf8-json":
        raise ArtifactPackageError("unsupported payload_encoding")
    if pkg.get("fingerprint_algo") != "sha256":
        raise ArtifactPackageError("unsupported fingerprint algorithm")
    try:
        raw = base64.b64decode(str(pkg.get("payload_b64", "")), validate=True)
    except Exception as exc:  # noqa: BLE001
        raise ArtifactPackageError("invalid payload_b64") from exc

    got = "sha256:" + hashlib.sha256(raw).hexdigest()
    expected = str(pkg.get("fingerprint", ""))
    if got != expected:
        raise ArtifactPackageError("fingerprint mismatch")

    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ArtifactPackageError("invalid utf8-json payload") from exc

    return True, payload
