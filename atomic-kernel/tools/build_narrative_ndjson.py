#!/usr/bin/env python3
"""Build narrative markdown corpus into NDJSON chapter files + hub manifest + browser bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ATOMIC_ROOT = ROOT / "atomic-kernel"
SOURCE_ROOT = ROOT / "narrative-series" / "When Wisdom, Law, and the Tribe Sat Down Together"
OUTPUT_ROOT = ATOMIC_ROOT / "narrative_data"
CHAPTERS_OUT = OUTPUT_ROOT / "chapters"
HUB_OUT = OUTPUT_ROOT / "hub.ndjson"
BUNDLE_OUT = OUTPUT_ROOT / "narrative_bundle.js"

WORLD_THEMES = [
    "river-gate",
    "tower-shadow",
    "desert-law",
    "garden-memory",
    "city-of-measure",
    "witness-plain",
]


def sid(value: str, prefix: str) -> str:
    h = hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{h}"


def slug(text: str) -> str:
    text = re.sub(r"[*_`#]+", "", text).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "scene"


def clean_heading(line: str) -> str:
    s = re.sub(r"^#{1,6}\s+", "", line).strip()
    s = re.sub(r"[*`_]+", "", s).strip()
    return s or "Untitled"


def chapter_files() -> list[Path]:
    files: list[Path] = []

    prelude = sorted((SOURCE_ROOT / "PRELUDE").glob("*.md"), key=lambda p: p.name.lower())
    files.extend(prelude)

    for i in range(1, 9):
        p = SOURCE_ROOT / f"ARTICLE {'I' * 0}.md"
        roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"][i - 1]
        p = SOURCE_ROOT / f"ARTICLE {roman}.md"
        if p.exists():
            files.append(p)

    aside = SOURCE_ROOT / "ASIDE.md"
    if aside.exists():
        files.append(aside)

    epilogue = sorted((SOURCE_ROOT / "EPILOUGE").glob("*.md"), key=lambda p: p.name.lower())
    files.extend(epilogue)

    return files


@dataclass
class SceneChunk:
    heading: str
    body: str


def parse_markdown_scenes(path: Path) -> list[SceneChunk]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    headers: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        if re.match(r"^#{1,6}\s+", line.strip()):
            headers.append((idx, clean_heading(line)))

    if not headers:
        body = "\n".join(lines).strip()
        return [SceneChunk(heading=path.stem, body=body)]

    scenes: list[SceneChunk] = []
    for i, (start_idx, heading) in enumerate(headers):
        end_idx = headers[i + 1][0] if i + 1 < len(headers) else len(lines)
        body_lines = lines[start_idx + 1 : end_idx]
        body = "\n".join(body_lines).strip()
        if not body:
            body = "..."
        scenes.append(SceneChunk(heading=heading, body=body))
    return scenes


def chapter_phase(path: Path) -> str:
    rel = path.relative_to(SOURCE_ROOT)
    if rel.parts[0] == "PRELUDE":
        return "prelude"
    if rel.parts[0] == "EPILOUGE":
        return "epilogue"
    if path.name.startswith("ARTICLE"):
        return "article"
    return "aside"


def build_records_for_chapter(path: Path, order: int, req_artifacts: list[str]) -> dict[str, Any]:
    rel = path.relative_to(ROOT).as_posix()
    chapter_id = sid(rel, "ch")
    chunks = parse_markdown_scenes(path)
    theme = WORLD_THEMES[order % len(WORLD_THEMES)]
    phase = chapter_phase(path)

    artifact_id = sid(f"artifact:{rel}", "art")
    artifact = {
        "type": "artifact",
        "id": artifact_id,
        "chapter_id": chapter_id,
        "name": f"Sigil of {path.stem}",
        "description": f"Cross-world artifact from {path.stem}",
        "model_ref": {
            "type": "primitive",
            "primitive": "box",
            "color": int(hashlib.sha1(chapter_id.encode()).hexdigest()[:6], 16),
        },
        "cross_world_tags": [phase, slug(path.stem)],
    }

    scenes: list[dict[str, Any]] = []
    choices: list[dict[str, Any]] = []

    for idx, chunk in enumerate(chunks):
        scene_id = sid(f"{rel}:{idx}:{slug(chunk.heading)}", "sc")
        grants = [artifact_id] if idx == len(chunks) - 1 else []
        requires = req_artifacts if idx == 0 else []
        scenes.append(
            {
                "type": "scene",
                "id": scene_id,
                "chapter_id": chapter_id,
                "heading": chunk.heading,
                "body_text": chunk.body,
                "world_node": f"{theme}-{idx % 4}",
                "grants_artifacts": grants,
                "requires_artifacts": requires,
            }
        )

    for idx, scene in enumerate(scenes):
        if idx < len(scenes) - 1:
            to_scene = scenes[idx + 1]["id"]
            label = "Continue"
            grants = []
        else:
            to_scene = "__hub__"
            label = "Return to Hub"
            grants = [artifact_id]
        choice_id = sid(f"{scene['id']}:{to_scene}", "chc")
        choices.append(
            {
                "type": "choice",
                "id": choice_id,
                "from_scene_id": scene["id"],
                "label": label,
                "to_scene_id": to_scene,
                "requires_artifacts": [],
                "grants_artifacts": grants,
            }
        )

    meta = {
        "type": "chapter_meta",
        "id": chapter_id,
        "title": path.stem,
        "source_path": rel,
        "order": order,
        "phase": phase,
        "world_theme": theme,
        "intro_scene_id": scenes[0]["id"],
    }

    gate = {
        "type": "gate",
        "id": sid(f"gate:{chapter_id}", "gate"),
        "target_chapter_id": chapter_id,
        "requires_artifacts": req_artifacts,
        "lock_text": "Artifact required from previous world.",
        "unlock_text": "Path opens. Enter chapter.",
    }

    records = [meta, artifact, *scenes, *choices]
    return {
        "chapter_id": chapter_id,
        "records": records,
        "gate": gate,
        "artifact_id": artifact_id,
        "meta": meta,
    }


def write_ndjson(path: Path, records: list[dict[str, Any]]) -> None:
    lines = [json.dumps(r, ensure_ascii=False, sort_keys=True) for r in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def records_from_ndjson(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


def build(write: bool) -> dict[str, Any]:
    files = chapter_files()
    if not files:
        raise SystemExit(f"No markdown files found under {SOURCE_ROOT}")

    chapter_payloads: list[dict[str, Any]] = []
    prior_artifact: list[str] = []

    for idx, path in enumerate(files):
        req = [] if idx == 0 else list(prior_artifact)
        payload = build_records_for_chapter(path, idx, req)
        chapter_payloads.append(payload)
        prior_artifact = [payload["artifact_id"]]

    prologue_id = chapter_payloads[0]["chapter_id"]
    hub_records: list[dict[str, Any]] = [
        {
            "type": "hub_meta",
            "id": "hub_main",
            "title": "World Map Hub",
            "prologue_chapter_id": prologue_id,
        }
    ]
    for payload in chapter_payloads:
        hub_records.append(payload["gate"])

    bundle = {
        "hub": {
            "meta": hub_records[0],
            "gates": [r for r in hub_records[1:] if r["type"] == "gate"],
        },
        "chapters": {
            p["chapter_id"]: {
                "meta": p["meta"],
                "records": p["records"],
            }
            for p in chapter_payloads
        },
    }

    if write:
        CHAPTERS_OUT.mkdir(parents=True, exist_ok=True)
        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

        for payload in chapter_payloads:
            out = CHAPTERS_OUT / f"{payload['chapter_id']}.ndjson"
            write_ndjson(out, payload["records"])

        write_ndjson(HUB_OUT, hub_records)

        js = "window.NARRATIVE_DATA = " + json.dumps(bundle, ensure_ascii=False) + ";\n"
        BUNDLE_OUT.write_text(js, encoding="utf-8")

    return {
        "files": files,
        "chapter_payloads": chapter_payloads,
        "hub_records": hub_records,
        "bundle": bundle,
    }


def validate_existing() -> list[str]:
    problems: list[str] = []
    generated = build(write=False)

    for payload in generated["chapter_payloads"]:
        path = CHAPTERS_OUT / f"{payload['chapter_id']}.ndjson"
        if not path.exists():
            problems.append(f"missing chapter ndjson: {path}")
            continue
        got = records_from_ndjson(path)
        if got != payload["records"]:
            problems.append(f"chapter ndjson mismatch: {path.name}")

        if not any(r.get("type") == "chapter_meta" for r in got):
            problems.append(f"chapter_meta missing in {path.name}")
        if not any(r.get("type") == "scene" for r in got):
            problems.append(f"scene records missing in {path.name}")

    if not HUB_OUT.exists():
        problems.append("missing hub.ndjson")
    else:
        hub = records_from_ndjson(HUB_OUT)
        if hub != generated["hub_records"]:
            problems.append("hub.ndjson mismatch")
        if not any(r.get("type") == "hub_meta" for r in hub):
            problems.append("hub_meta missing")

    if not BUNDLE_OUT.exists():
        problems.append("missing narrative_bundle.js")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Build narrative NDJSON + browser bundle")
    parser.add_argument("--write", action="store_true", help="write output files")
    parser.add_argument("--verify", action="store_true", help="verify generated files deterministically")
    args = parser.parse_args()

    if args.verify:
        problems = validate_existing()
        if problems:
            for p in problems:
                print(f"FAIL: {p}")
            return 1
        print("OK: narrative data files are valid and deterministic")
        return 0

    build(write=True if args.write or not args.verify else False)
    print(f"WROTE: {HUB_OUT}")
    print(f"WROTE: {BUNDLE_OUT}")
    print(f"WROTE: {CHAPTERS_OUT}/*.ndjson")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
