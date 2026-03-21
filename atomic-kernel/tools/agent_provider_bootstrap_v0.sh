#!/usr/bin/env bash
set -euo pipefail

PROFILE="${1:-small}"
INSTALL_MISSING="${INSTALL_MISSING:-0}"

have() { command -v "$1" >/dev/null 2>&1; }

start_ollama_if_needed() {
  if ! have ollama; then
    return 1
  fi
  if ollama list >/dev/null 2>&1; then
    return 0
  fi
  nohup ollama serve >/tmp/ollama-serve.log 2>&1 &
  sleep 2
  ollama list >/dev/null 2>&1
}

install_ollama() {
  curl -fsSL https://ollama.com/install.sh | sh
}

echo "[agent-provider-bootstrap] profile=$PROFILE install_missing=$INSTALL_MISSING"

if have opencode; then
  echo "[ok] opencode installed: $(command -v opencode)"
else
  echo "[warn] opencode not installed"
fi

if have ollama; then
  echo "[ok] ollama binary installed: $(command -v ollama)"
else
  echo "[warn] ollama not installed"
  if [[ "$INSTALL_MISSING" == "1" ]]; then
    echo "[action] installing ollama"
    install_ollama
  fi
fi

if have ollama; then
  if start_ollama_if_needed; then
    echo "[ok] ollama server ready"
  else
    echo "[warn] ollama server not ready"
  fi
fi

if have openclaw; then
  echo "[ok] openclaw binary installed"
elif [[ -n "${OPENCLAW_ADAPTER_CMD:-}" ]]; then
  echo "[ok] openclaw adapter command configured"
else
  echo "[info] openclaw adapter not configured (optional in v0)"
fi

echo "[next] run: python3 tools/agent_provider_router_v0.py --profile $PROFILE"
