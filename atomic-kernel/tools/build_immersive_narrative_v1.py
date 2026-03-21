#!/usr/bin/env python3
import json
import hashlib
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "narrative_data" / "chapters"
CUES_DIR = ROOT / "narrative_data" / "cues"
CASTING_DIR = ROOT / "narrative_data" / "casting"
CONTRACTS_DIR = ROOT / "narrative_data" / "contracts"
MANIFEST_PATH = ROOT.parent / "docs" / "imports" / "asset-manifest.json"
DOCS_CUES_DIR = ROOT.parent / "docs" / "immersive-data" / "cues"
DOCS_CASTING_DIR = ROOT.parent / "docs" / "immersive-data" / "casting"


def stable_dump(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_ndjson(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
      line = line.strip()
      if line:
        rows.append(json.loads(line))
    return rows


def sid(prefix: str, text: str) -> str:
    return f"{prefix}_{hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]}"


def build_cue_for_chapter(path: Path):
    rows = load_ndjson(path)
    meta = next((r for r in rows if r.get("type") == "chapter_meta"), None)
    if not meta:
        return None
    chapter_id = str(meta["id"])
    scenes = [r for r in rows if r.get("type") == "scene"]
    choices = [r for r in rows if r.get("type") == "choice"]
    by_from = defaultdict(list)
    for c in choices:
        by_from[str(c.get("from_scene_id", ""))].append(c)

    total_tick = 0
    timeline = []
    for idx, s in enumerate(scenes):
        scene_id = str(s.get("id"))
        scene_choices = by_from.get(scene_id, [])
        cue_points = [
            {
                "kind": "camera",
                "tick": total_tick,
                "camera_mode": "cinematic_dolly",
            },
            {
                "kind": "dialogue",
                "tick": total_tick + 4,
                "line_budget": max(1, min(12, len(str(s.get("body_text", ""))) // 180 + 1)),
            },
            {
                "kind": "step_in",
                "tick": total_tick + 10,
                "duration_ticks": 12,
                "interaction_mode": "advisory_proposal",
            },
        ]
        if scene_choices:
            cue_points.append(
                {
                    "kind": "choice_window",
                    "tick": total_tick + 22,
                    "duration_ticks": 10,
                    "choice_ids": [str(c.get("id")) for c in scene_choices],
                }
            )
        if any(str(c.get("to_scene_id")) == "__hub__" for c in scene_choices):
            cue_points.append(
                {
                    "kind": "return_hub",
                    "tick": total_tick + 34,
                    "target": "__hub__",
                }
            )

        timeline.append(
            {
                "scene_id": scene_id,
                "scene_heading": str(s.get("heading", scene_id)),
                "order": idx,
                "start_tick": total_tick,
                "end_tick": total_tick + 36,
                "cue_points": cue_points,
                "world_node": s.get("world_node"),
            }
        )
        total_tick += 36

    canonical = json.dumps(timeline, sort_keys=True, separators=(",", ":"))
    return {
        "type": "cinematic_cues",
        "version": 1,
        "chapter_id": chapter_id,
        "chapter_title": str(meta.get("title", chapter_id)),
        "world_theme": str(meta.get("world_theme", "gate_plaza")),
        "determinism_key": "seed|chapter_id|scene_id|tick",
        "timeline": timeline,
        "timeline_tick_span": total_tick,
        "cue_digest_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }


def pick_by_theme(assets, theme):
    t = str(theme or "").strip().lower()
    themed = [a for a in assets if str(a.get("theme", "")).strip().lower() == t]
    if themed:
        return themed[0]
    return assets[0] if assets else None


def build_casting(chapter_metas, manifest_assets):
    avatars = [a for a in manifest_assets if a.get("kind") == "avatar" and a.get("redistributable") is True]
    envs = [a for a in manifest_assets if a.get("kind") == "environment" and a.get("redistributable") is True]
    avatars.sort(key=lambda a: str(a.get("id", "")))
    envs.sort(key=lambda a: str(a.get("id", "")))

    noun_order = [
        "solomon", "solon", "asabiyah", "watcher", "city", "gate", "tribe", "wisdom", "law", "cohesion"
    ]
    cast_rows = []
    for idx, noun in enumerate(noun_order):
        if not avatars:
            break
        asset = avatars[idx % len(avatars)]
        cast_rows.append(
            {
                "noun": noun,
                "avatar_asset_id": asset.get("id"),
                "policy": "queued_swap_only",
                "fallback": "primitive_actor",
            }
        )

    theme_map = {}
    for meta in chapter_metas:
        th = str(meta.get("world_theme", "gate_plaza"))
        if th in theme_map:
            continue
        picked = pick_by_theme(envs, th)
        if not picked:
            continue
        theme_map[th] = {
            "landscape_asset_id": picked.get("id"),
            "fallback": "procedural_grid",
        }

    allow_assets = [a for a in manifest_assets if a.get("redistributable") is True and a.get("kind") in {"avatar", "environment"}]
    allow_assets.sort(key=lambda a: str(a.get("id", "")))
    allowlist = {
        "type": "public_allowlist",
        "version": 1,
        "policy": "allowlist_only",
        "asset_ids": [a.get("id") for a in allow_assets],
        "assets": [
            {
                "id": a.get("id"),
                "title": a.get("title"),
                "kind": a.get("kind"),
                "entry_glb": a.get("entry_glb"),
                "entry_gltf": a.get("entry_gltf"),
                "license_file": a.get("license_file"),
                "license_kind": a.get("license_kind"),
                "attribution_required": bool(a.get("attribution_required")),
            }
            for a in allow_assets
        ],
    }

    return (
        {
            "type": "avatar_cast_map",
            "version": 1,
            "policy": "proposal_queue_only",
            "mappings": cast_rows,
        },
        {
            "type": "landscape_cast_map",
            "version": 1,
            "policy": "allowlist_only",
            "theme_map": theme_map,
        },
        allowlist,
    )


def build_contracts():
    proposal = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "immersive_proposal.v1",
        "title": "Immersive Proposal v1",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "type", "version", "proposal_id", "chapter_id", "scene_id", "tick", "action", "payload", "status", "authority"
        ],
        "properties": {
            "type": {"const": "immersive_proposal"},
            "version": {"const": 1},
            "proposal_id": {"type": "string", "minLength": 4},
            "chapter_id": {"type": "string", "minLength": 4},
            "scene_id": {"type": "string", "minLength": 4},
            "tick": {"type": "integer", "minimum": 0},
            "action": {"enum": ["choice_select", "camera_branch", "avatar_swap", "scene_pace_change"]},
            "payload": {"type": "object", "additionalProperties": True},
            "status": {"enum": ["pending", "accepted", "rejected"]},
            "authority": {"const": "advisory"},
        },
    }
    receipt = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "immersive_receipt.v1",
        "title": "Immersive Receipt v1",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "type", "version", "receipt_id", "proposal_id", "decision", "reason", "frame_boundary_tick", "authority"
        ],
        "properties": {
            "type": {"const": "immersive_receipt"},
            "version": {"const": 1},
            "receipt_id": {"type": "string", "minLength": 4},
            "proposal_id": {"type": "string", "minLength": 4},
            "decision": {"enum": ["accepted", "rejected"]},
            "reason": {"type": "string", "minLength": 1},
            "frame_boundary_tick": {"type": "integer", "minimum": 0},
            "authority": {"const": "advisory"},
        },
    }
    return proposal, receipt


def main():
    chapters = sorted(CHAPTER_DIR.glob("ch_*.ndjson"), key=lambda p: p.name)
    chapter_metas = []

    CUES_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_CUES_DIR.mkdir(parents=True, exist_ok=True)

    for p in chapters:
        cues = build_cue_for_chapter(p)
        if not cues:
            continue
        chapter_metas.append({
            "id": cues["chapter_id"],
            "title": cues["chapter_title"],
            "world_theme": cues["world_theme"],
        })
        out_name = f"{cues['chapter_id']}.cinematic_cues.v1.json"
        stable_dump(CUES_DIR / out_name, cues)
        stable_dump(DOCS_CUES_DIR / out_name, cues)

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assets = list(manifest.get("assets", []))
    avatar_map, landscape_map, allowlist = build_casting(chapter_metas, assets)

    stable_dump(CASTING_DIR / "avatar_cast_map.v1.json", avatar_map)
    stable_dump(CASTING_DIR / "landscape_cast_map.v1.json", landscape_map)
    stable_dump(CASTING_DIR / "public_allowlist.v1.json", allowlist)

    stable_dump(DOCS_CASTING_DIR / "avatar_cast_map.v1.json", avatar_map)
    stable_dump(DOCS_CASTING_DIR / "landscape_cast_map.v1.json", landscape_map)
    stable_dump(DOCS_CASTING_DIR / "public_allowlist.v1.json", allowlist)

    proposal_schema, receipt_schema = build_contracts()
    stable_dump(CONTRACTS_DIR / "immersive_proposal.v1.json", proposal_schema)
    stable_dump(CONTRACTS_DIR / "immersive_receipt.v1.json", receipt_schema)

    index = {
        "type": "immersive_narrative_build",
        "version": 1,
        "chapters": [m["id"] for m in sorted(chapter_metas, key=lambda x: x["id"])],
        "outputs": {
            "cues_dir": str(CUES_DIR.relative_to(ROOT)),
            "casting_dir": str(CASTING_DIR.relative_to(ROOT)),
            "contracts_dir": str(CONTRACTS_DIR.relative_to(ROOT)),
        },
    }
    stable_dump(ROOT / "narrative_data" / "immersive_narrative_build.v1.json", index)
    print(f"ok immersive narrative build v1 chapters={len(chapter_metas)}")


if __name__ == "__main__":
    main()
