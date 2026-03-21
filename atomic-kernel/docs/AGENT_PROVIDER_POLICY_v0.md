# Agent Provider Policy v0

Status: Normative Draft  
Authority: Advisory Routing Policy

## Purpose

Select an external agent provider (`opencode`, `ollama`, `openclaw_adapter`) based on bandwidth and host capability while preserving proposal-only mutation boundaries.

## Profiles

- `small`: lowest network and compute envelope
- `medium`: balanced envelope
- `large`: highest local compute envelope

## Routing Order

### small
1. `opencode`
2. `openclaw_adapter`
3. `mock`

### medium
1. `opencode`
2. `ollama`
3. `openclaw_adapter`
4. `mock`

### large
1. `ollama`
2. `opencode`
3. `openclaw_adapter`
4. `mock`

## Readiness Constraints

`ollama` is considered ready only when:

- binary exists
- server responds

If server is not responding, router must fall back to next provider.

## Invariants

- provider routing is advisory and non-authoritative
- proposal envelope remains `agent_action_proposal.v0`
- canonical mutation remains outside provider routing
- unknown profile/provider must fail closed
