#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FRANCHISE_MARKERS = (
    "bluey",
    "family_guy",
    "jimmy_neutron",
    "incredibles",
    "fairy_oddparents",
)

DEFAULT_ENABLED_IDS = {
    "human_malefemale_basemesh_rigged",
    "city",
    "lowpoly_city",
    "ccity_building_set_1",
    "park_0914",
    "park_0926",
}


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", text.lower())
    return re.sub(r"_+", "_", s).strip("_")


def rel(path: Path, root: Path) -> str:
    return "/" + path.relative_to(root).as_posix()


def infer_kind(asset_id: str) -> str:
    s = asset_id.lower()
    if "character" in s or s in {"nikki_and_nick", "lucero_and_nicholas", "lori_and_zack", "steven_and_stacy"}:
        return "avatar"
    if "city" in s or "park" in s or "arena" in s:
        return "environment"
    if "angel" in s or "bird" in s or "brain" in s:
        return "prop"
    return "prop"


def infer_role(asset_id: str, kind: str) -> str:
    s = asset_id.lower()
    if kind == "avatar":
        if "crowd" in s or "all_characters" in s:
            return "character/crowd"
        return "character/human"
    if "park" in s or "garden" in s:
        return "architecture/park"
    if "temple" in s or "ophanim" in s:
        return "architecture/temple"
    if "city" in s or "arena" in s:
        if "pack" in s or "building_set" in s or "ccity" in s:
            return "architecture/city_block"
        return "environment/ground"
    if "brain" in s:
        return "effect/hologram"
    if "bird" in s or "angel" in s:
        return "symbolic/object"
    if kind == "environment":
        return "environment/ground"
    return "symbolic/object"


def infer_theme(asset_id: str, role: str) -> str:
    s = asset_id.lower()
    if "park" in s or "garden" in s:
        return "garden_threshold"
    if "arena" in s:
        return "civic_square"
    if "temple" in s or "ophanim" in s:
        return "gate_plaza"
    if "city" in s:
        return "city_street"
    if "brain" in s:
        return "witness_sparse"
    if role.startswith("character/"):
        return "gate_plaza"
    return "gate_plaza"


def infer_scale_hint(asset_id: str, role: str) -> float:
    s = asset_id.lower()
    if role.startswith("character/"):
        return 1.0
    if role.startswith("environment/"):
        return 1.25 if "city" in s else 1.1
    if role.startswith("architecture/"):
        return 1.15
    if role == "effect/hologram":
        return 0.95
    return 1.0


def infer_title(asset_id: str) -> str:
    return asset_id.replace("_", " ").replace("-", " ").title()


def find_candidate_dirs(imports_dir: Path, stem: str) -> list[Path]:
    stems = sorted({stem, stem.replace("-", "_"), stem.replace("_", "-")})
    out = []
    for s in stems:
        p = imports_dir / s
        if p.is_dir():
            out.append(p)
    return out


def pick_preview_image(dirs: list[Path]) -> Path | None:
    for d in dirs:
        for pattern in ("*.png", "*.jpg", "*.jpeg", "textures/*.png", "textures/*.jpg", "textures/*.jpeg"):
            files = sorted(d.glob(pattern))
            if files:
                return files[0]
    return None


def pick_license(dirs: list[Path]) -> Path | None:
    for d in dirs:
        p = d / "license.txt"
        if p.is_file():
            return p
    return None


def build_manifest(imports_dir: Path) -> dict:
    entries = []
    root = imports_dir.parent.parent  # /docs
    glb_files = sorted(imports_dir.glob("*.glb"))
    gltf_files = sorted(imports_dir.glob("*/scene.gltf"))

    seen_ids = set()

    for glb in glb_files:
        asset_id = slug(glb.stem)
        seen_ids.add(asset_id)
        dirs = find_candidate_dirs(imports_dir, glb.stem)
        license_file = pick_license(dirs)
        preview = pick_preview_image(dirs)
        entry_gltf = None
        for d in dirs:
            p = d / "scene.gltf"
            if p.is_file():
                entry_gltf = p
                break

        has_franchise_marker = any(m in asset_id for m in FRANCHISE_MARKERS)
        redistributable = bool(license_file) and not has_franchise_marker
        kind = infer_kind(asset_id)
        role = infer_role(asset_id, kind)
        theme = infer_theme(asset_id, role)
        scale_hint = infer_scale_hint(asset_id, role)
        default_enabled = redistributable and (asset_id in DEFAULT_ENABLED_IDS or role in {
            "environment/ground", "architecture/city_block", "character/human"
        })

        entries.append(
            {
                "id": asset_id,
                "title": infer_title(asset_id),
                "kind": kind,
                "role": role,
                "theme": theme,
                "entry_glb": rel(glb, root),
                "entry_gltf": rel(entry_gltf, root) if entry_gltf else None,
                "preview_image": rel(preview, root) if preview else None,
                "license_file": rel(license_file, root) if license_file else None,
                "author": "",
                "source_url": "",
                "license_kind": "unknown",
                "attribution_required": bool(license_file),
                "redistributable": redistributable,
                "default_enabled": default_enabled,
                "tags": [kind, "imported", "local-library"],
                "scale_hint": scale_hint,
                "spawn_offset": [0, 0, 0],
                "notes": "auto-scanned from docs/imports",
            }
        )

    for gltf in gltf_files:
        asset_id = slug(gltf.parent.name)
        if asset_id in seen_ids:
            continue
        dirs = [gltf.parent]
        license_file = pick_license(dirs)
        preview = pick_preview_image(dirs)
        has_franchise_marker = any(m in asset_id for m in FRANCHISE_MARKERS)
        redistributable = bool(license_file) and not has_franchise_marker
        kind = infer_kind(asset_id)
        role = infer_role(asset_id, kind)
        theme = infer_theme(asset_id, role)
        scale_hint = infer_scale_hint(asset_id, role)
        default_enabled = redistributable and (asset_id in DEFAULT_ENABLED_IDS or role in {
            "environment/ground", "architecture/city_block", "character/human"
        })
        entries.append(
            {
                "id": asset_id,
                "title": infer_title(asset_id),
                "kind": kind,
                "role": role,
                "theme": theme,
                "entry_glb": None,
                "entry_gltf": rel(gltf, root),
                "preview_image": rel(preview, root) if preview else None,
                "license_file": rel(license_file, root) if license_file else None,
                "author": "",
                "source_url": "",
                "license_kind": "unknown",
                "attribution_required": bool(license_file),
                "redistributable": redistributable,
                "default_enabled": default_enabled,
                "tags": [kind, "imported", "local-library"],
                "scale_hint": scale_hint,
                "spawn_offset": [0, 0, 0],
                "notes": "auto-scanned from docs/imports",
            }
        )

    entries.sort(key=lambda x: (0 if x["default_enabled"] else 1, x["title"]))
    return {
        "type": "asset_manifest",
        "version": 1,
        "generated_by": "build_import_asset_manifest.py",
        "assets": entries,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    imports_dir = repo_root / "docs" / "imports"
    out_file = imports_dir / "asset-manifest.json"

    manifest = build_manifest(imports_dir)
    payload = json.dumps(manifest, indent=2, ensure_ascii=True) + "\n"

    if args.verify:
        if not out_file.exists():
            raise SystemExit("asset-manifest.json missing")
        existing = out_file.read_text(encoding="utf-8")
        if existing != payload:
            raise SystemExit("asset-manifest.json out of date; run --write")
        print("OK: import asset manifest deterministic")
        return 0

    if args.write or not out_file.exists():
        out_file.write_text(payload, encoding="utf-8")
        print(f"Wrote {out_file}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
