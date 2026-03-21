# Resident Agent Spec v1

Status: Advisory (runtime behavior contract)
Authority: Advisory
Depends on: `docs/WITNESS_PLANE_SPEC.md`, `docs/CHARACTER_PROGRESSION_TEMPLATES.md`, `narrative_data/cues/*.cinematic_cues.v1.json`

## Purpose

Define deterministic autonomous resident behavior for immersive narrative playback without direct canonical mutation.

Residents are lawful participants:
- observe chapter/cue context
- select bounded action intent
- emit proposal artifacts
- never commit canonical state directly

## Invariants

1. Proposal-only mutation path
- Resident outputs are `pending` proposals only.
- No resident output can mark `accepted` or mutate canonical event logs.

2. Determinism
- For identical `(seed, chapter_id, tick range, resident roster)` inputs, outputs are byte-stable.

3. Fail-closed action vocabulary
- Only these actions are valid:
  - `choice_select`
  - `camera_branch`
  - `avatar_swap`
  - `scene_pace_change`

4. Advisory authority
- Runtime artifacts emitted by resident simulation must include `authority: "advisory"`.

## Runtime Inputs

- `seed` (string)
- `chapter_id` (`ch_*` id)
- `start_tick` (integer >= 0)
- `ticks` (integer > 0)
- `residents` (fixed deterministic roster)

## Runtime Outputs

- `resident_agent_tick.v1` normalized artifact
- proposal list (`status: pending` only)
- replay hash digest
- proof receipt from gate execution

## Step Law (Per Tick)

For each resident in stable sorted order:

1. Build deterministic decision key:
- `sha256(seed|chapter_id|tick|resident_id)`

2. Select one action from bounded action enum.

3. Build one proposal:
- includes actor id, action, target, requested state, tick
- `status: pending`

4. Append proposal to output list.

## Boundary

This spec does not define proposal acceptance.
Acceptance remains in witness/proposal governance flows and frame-boundary commit checks.
