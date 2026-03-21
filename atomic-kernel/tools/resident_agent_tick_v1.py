#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "narrative_data" / "chapters"
ARTIFACTS_DIR = ROOT / "artifacts"

ACTION_ENUM = [
    "choice_select",
    "camera_branch",
    "avatar_swap",
    "scene_pace_change",
]

DEFAULT_RESIDENTS = [
    {"id": "solomon", "role": "advisor_wisdom", "goal": "preserve_identity_before_power"},
    {"id": "solon", "role": "advisor_law", "goal": "stabilize_disagreement_without_violence"},
    {"id": "asabiyah", "role": "witness_cohesion", "goal": "maintain_shared_cohesion_surface"},
]


def stable_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def require_chapter(chapter_id: str):
    p = CHAPTER_DIR / f"{chapter_id}.ndjson"
    if not p.exists():
        raise SystemExit(f"missing chapter: {chapter_id}")


def pick_action(seed: str, chapter_id: str, tick: int, resident_id: str) -> str:
    h = digest_text(f"{seed}|{chapter_id}|{tick}|{resident_id}")
    idx = int(h[:8], 16) % len(ACTION_ENUM)
    return ACTION_ENUM[idx]


def build_target(chapter_id: str, tick: int) -> str:
    return f"scene:{chapter_id}:t{tick}"


def build_requested_state(action: str, tick: int) -> str:
    if action == "choice_select":
        return f"branch:choice_window:t{tick}"
    if action == "camera_branch":
        return f"camera:cinematic_branch:t{tick}"
    if action == "avatar_swap":
        return f"avatar:cast_swap:t{tick}"
    return f"pace:adjust:t{tick}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", required=True)
    ap.add_argument("--chapter-id", required=True)
    ap.add_argument("--start-tick", type=int, default=0)
    ap.add_argument("--ticks", type=int, default=8)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    if args.start_tick < 0:
        raise SystemExit("start_tick must be >= 0")
    if args.ticks <= 0 or args.ticks > 128:
        raise SystemExit("ticks must be in 1..128")

    require_chapter(args.chapter_id)

    residents = sorted(DEFAULT_RESIDENTS, key=lambda r: r["id"])
    proposals = []
    for t in range(args.start_tick, args.start_tick + args.ticks):
        for r in residents:
            action = pick_action(args.seed, args.chapter_id, t, r["id"])
            proposal_id = digest_text(f"proposal|{args.seed}|{args.chapter_id}|{t}|{r['id']}|{action}")[:24]
            proposals.append(
                {
                    "proposal_id": f"imm_{proposal_id}",
                    "status": "pending",
                    "tick": t,
                    "chapter_id": args.chapter_id,
                    "actor_id": r["id"],
                    "action": action,
                    "target": build_target(args.chapter_id, t),
                    "requested_state": build_requested_state(action, t),
                }
            )

    out = {
        "v": "resident_agent_tick.v1",
        "authority": "advisory",
        "seed": args.seed,
        "chapter_id": args.chapter_id,
        "start_tick": args.start_tick,
        "ticks": args.ticks,
        "residents": residents,
        "action_enum": ACTION_ENUM,
        "proposals": proposals,
    }
    out["replay_hash"] = digest_text(stable_json(out))

    if args.write:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        (ARTIFACTS_DIR / "resident-agent-v1.normalized.json").write_text(
            json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (ARTIFACTS_DIR / "resident-agent-v1.replay-hash").write_text(
            out["replay_hash"] + "\n", encoding="utf-8"
        )

    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
