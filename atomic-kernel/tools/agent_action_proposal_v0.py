#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "narrative_data" / "contracts" / "agent_action_proposal.v0.json"

ALLOWED_PROVIDERS = {"mock", "ollama", "opencode", "openclaw_adapter"}


def stable_json(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def short_id(prefix: str, digest: str) -> str:
    return f"{prefix}_{digest[:16]}"


def mock_provider_output(intent: str) -> str:
    token = intent.strip().lower().replace(" ", "_")
    token = "".join(ch for ch in token if ch.isalnum() or ch == "_")
    token = token[:48] or "noop"
    return f"MOCK:{token}"


def ollama_provider_output(model: str, intent: str) -> str:
    cmd = [
        "ollama",
        "run",
        model,
        f"Return one concise action line only. Intent: {intent}",
    ]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True)
    line = out.stdout.strip().splitlines()
    return line[0].strip() if line else ""


def opencode_provider_output(intent: str) -> str:
    # v0 keeps this bounded/deterministic-envelope-first.
    cmd = ["opencode", "run", f"Return one concise action line only. Intent: {intent}"]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)
    line = out.stdout.strip().splitlines()
    return line[0].strip() if line else ""


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def ollama_ready() -> bool:
    if not command_exists("ollama"):
        return False
    try:
        r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=3)
        return r.returncode == 0
    except Exception:
        return False


def resolve_provider(provider: str, profile: str) -> str:
    if provider != "auto":
        return provider

    if profile == "large":
        order = ["ollama", "opencode", "openclaw_adapter", "mock"]
    elif profile == "medium":
        order = ["opencode", "ollama", "openclaw_adapter", "mock"]
    elif profile == "small":
        order = ["opencode", "openclaw_adapter", "mock"]
    else:
        raise SystemExit(f"unknown profile: {profile}")

    for p in order:
        if p == "mock":
            return p
        if p == "opencode" and command_exists("opencode"):
            return p
        if p == "ollama" and ollama_ready():
            return p
        if p == "openclaw_adapter" and (command_exists("openclaw") or os.getenv("OPENCLAW_ADAPTER_CMD", "").strip()):
            return p
    return "mock"


def build(provider: str, world_id: str, agent_id: str, canonical_tick: int, intent: str, ollama_model: str, profile: str) -> dict:
    provider = resolve_provider(provider, profile)
    if provider not in ALLOWED_PROVIDERS:
        raise SystemExit(f"unsupported provider: {provider}")
    if canonical_tick < 0:
        raise SystemExit("canonical_tick must be >= 0")
    if not intent.strip():
        raise SystemExit("intent must be non-empty")

    provider_output = ""
    mode = "external"
    provider_deterministic = False

    if provider == "mock":
        mode = "mock"
        provider_deterministic = True
        provider_output = mock_provider_output(intent)
    elif provider == "ollama":
        if not ollama_model:
            raise SystemExit("--ollama-model is required when provider=ollama")
        try:
            provider_output = ollama_provider_output(ollama_model, intent)
        except Exception:
            provider_output = "OLLAMA_CALL_FAILED"
    elif provider == "opencode":
        try:
            provider_output = opencode_provider_output(intent)
        except Exception:
            provider_output = "OPENCODE_CALL_FAILED"
    else:
        # Adapter providers are accepted by contract, but execution stays external in v0.
        provider_output = "EXTERNAL_ADAPTER_REQUIRED"

    intent_digest = sha256_text(intent.strip())
    key_digest = sha256_text(stable_json({
        "provider": provider,
        "world_id": world_id,
        "agent_id": agent_id,
        "canonical_tick": canonical_tick,
        "intent_digest": intent_digest,
        "provider_output": provider_output,
    }))

    proposal = {
        "v": "agent_action_proposal.v0",
        "type": "agent_action_proposal",
        "authority": "advisory",
        "mutation_boundary": "proposal_only",
        "provider": provider,
        "world_id": world_id,
        "agent_id": agent_id,
        "canonical_tick": canonical_tick,
        "proposal_id": short_id("prop", key_digest),
        "proposed_action": {
            "kind": "world_step_intent",
            "intent_text": intent.strip(),
            "intent_digest": intent_digest,
        },
        "provider_envelope": {
            "mode": mode,
            "provider_deterministic": provider_deterministic,
            "provider_output": provider_output,
        },
        "receipt_stub": {
            "status": "pending",
            "accepted": False,
            "receipt_ref": short_id("rcpt", sha256_text("receipt:" + key_digest)),
        },
    }
    proposal["replay_hash"] = sha256_text(stable_json(proposal))
    return proposal


def validate_shape(obj: dict) -> None:
    if obj.get("v") != "agent_action_proposal.v0":
        raise SystemExit("version mismatch")
    if obj.get("type") != "agent_action_proposal":
        raise SystemExit("type mismatch")
    if obj.get("authority") != "advisory":
        raise SystemExit("authority mismatch")
    if obj.get("mutation_boundary") != "proposal_only":
        raise SystemExit("mutation_boundary mismatch")
    if obj.get("receipt_stub", {}).get("accepted") is not False:
        raise SystemExit("receipt accepted must be false")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="auto")
    ap.add_argument("--profile", default=os.getenv("AGENT_BANDWIDTH_PROFILE", "small"))
    ap.add_argument("--world-id", default="world.v0:orchard_garden_lattice")
    ap.add_argument("--agent-id", default="writer.proposal.constructive")
    ap.add_argument("--canonical-tick", type=int, default=42)
    ap.add_argument("--intent", required=True)
    ap.add_argument("--ollama-model", default="")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "artifacts" / "agent-action-proposal-v0.normalized.json"))
    args = ap.parse_args()

    obj = build(
        provider=args.provider,
        world_id=args.world_id,
        agent_id=args.agent_id,
        canonical_tick=args.canonical_tick,
        intent=args.intent,
        ollama_model=args.ollama_model,
        profile=args.profile,
    )
    validate_shape(obj)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.write:
        out_path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif args.verify:
        on_disk = json.loads(Path(CONTRACT_PATH).read_text(encoding="utf-8"))
        check = dict(on_disk)
        replay_hash = check.pop("replay_hash", None)
        if replay_hash != sha256_text(stable_json(check)):
            raise SystemExit("contract replay_hash mismatch")
        if on_disk.get("authority") != "advisory":
            raise SystemExit("contract authority mismatch")
    else:
        print(json.dumps(obj, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
