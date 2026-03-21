# Canonical Time Algorithm v0

Status: Normative Draft
Authority: Algorithmic
Depends on: `docs/PURE_ALGORITHMS.md`, `docs/WITNESS_PLANE_SPEC.md`, `docs/ROLE_TOOLSET_MATRIX_v0.md`

## Canonical Time Source

Canonical time is a singular algorithmic tick surface.

- `canonical_tick` is authoritative for ordering and acceptance boundaries.
- server wall clock, browser clock, and network arrival order are operational only.
- projection/render timing is non-authoritative.

## Tick Advancement Rule

`canonical_tick` advances only through lawful transition steps in canonical state evaluation.

```text
tick_next = tick_current + 1
```

Advancement is invalid unless the current cycle's eligibility and proposal rules were evaluated.

## Candidate Ordering Rule

Candidate ordering is algorithmic, not representational:

- partition structure from lane logic
- orientation from chirality selection
- no ordering authority from UI position, lexical order, or network arrival

## Eligibility Rule (A14)

Eligibility is a pure function of canonical state and tick:

```text
eligible(action, state, canonical_tick) -> true|false
```

Ineligible actions MUST be rejected or deferred explicitly (never silently applied).

## Proposal Acceptance Rule

Proposal lifecycle is canonical-tick bound:

1. proposal created (pending)
2. acceptance/rejection decision recorded
3. accepted proposals apply only at lawful frame/tick boundary
4. receipt emitted with lineage and tick reference

Direct canonical mutation through projection/UI is forbidden.

## Reject Conditions

System MUST reject if any of these occur:

1. multiple competing canonical time sources
2. proposal acceptance by wall-clock arrival order
3. projection/render lag changing canonical truth
4. server-local clock drift changing canonical ordering
5. chirality introducing independent clock semantics
6. acceptance without receipt lineage

## Time Authority Test

Two honest nodes with different wall-clock timing MUST derive identical canonical order from identical canonical state.

If not, algorithm is non-conforming.
