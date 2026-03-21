#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "narrative_data" / "contracts" / "agent_provider_policy.v0.json"


def stable_json(v: dict) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def ollama_server_ready() -> bool:
    if not command_exists("ollama"):
        return False
    try:
        r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=3)
        return r.returncode == 0
    except Exception:
        return False


def openclaw_adapter_ready() -> bool:
    if command_exists("openclaw"):
        return True
    adapter_cmd = os.getenv("OPENCLAW_ADAPTER_CMD", "").strip()
    return bool(adapter_cmd)


def provider_ready(provider: str, probe: dict) -> bool:
    if provider == "mock":
        return True
    if provider == "opencode":
        return probe["opencode"]
    if provider == "ollama":
        return probe["ollama_binary"] and probe["ollama_server"]
    if provider == "openclaw_adapter":
        return probe["openclaw_adapter"]
    return False


def build(profile: str) -> dict:
    base = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if base.get("v") != "agent_provider_policy.v0":
        raise SystemExit("policy contract version mismatch")

    profiles = base.get("profiles", {})
    if profile not in profiles:
        raise SystemExit(f"unknown profile: {profile}")

    probe = {
        "opencode": command_exists("opencode"),
        "ollama_binary": command_exists("ollama"),
        "ollama_server": ollama_server_ready(),
        "openclaw_adapter": openclaw_adapter_ready(),
    }

    selected_provider = "mock"
    for p in profiles[profile]:
        if provider_ready(p, probe):
            selected_provider = p
            break

    out = {
        "v": "agent_provider_policy.v0",
        "authority": "advisory",
        "profiles": profiles,
        "runtime_probe": probe,
        "selected_profile": profile,
        "selected_provider": selected_provider,
    }
    out["replay_hash"] = sha256_text(stable_json(out))
    return out


def verify_contract() -> None:
    obj = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if obj.get("authority") != "advisory":
        raise SystemExit("contract authority mismatch")
    if set(obj.get("profiles", {}).keys()) != {"small", "medium", "large"}:
        raise SystemExit("contract profiles mismatch")
    check = dict(obj)
    replay_hash = check.pop("replay_hash", None)
    expect = sha256_text(stable_json(check))
    if replay_hash != expect:
        raise SystemExit("contract replay_hash mismatch")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default=os.getenv("AGENT_BANDWIDTH_PROFILE", "small"))
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "artifacts" / "agent-provider-policy-v0.normalized.json"))
    args = ap.parse_args()

    if args.verify:
        verify_contract()
        return

    obj = build(args.profile)
    if args.write:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(obj, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
