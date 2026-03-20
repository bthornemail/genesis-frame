# Semantic Graph Schema (Canonical Runtime Artifact)

Status: Normative Draft

## Purpose
Define a canonical semantic layer derived from narrative text + ontology hints and projected in GUI frames without mutating kernel law.

## Layers
- WordNet Prolog (5WN): ontology/type substrate.
- winkNLP: surface extraction substrate.
- Semantic Graph Artifact: runtime truth for semantic rendering.

## Node Kinds
- `entity`
- `place`
- `artifact`
- `law`
- `concept`
- `event`
- `role`

## Edge Kinds
- `seeks`
- `binds`
- `enters`
- `reveals`
- `opposes`
- `unlocks`
- `remembers`
- `causes`
- `requires`
- `grants`
- `relates_to`

## Records
### semantic_node
```json
{
  "type": "semantic_node",
  "id": "sn_x",
  "scene_id": "sc_x",
  "chapter_id": "ch_x",
  "label": "witness",
  "kind": "role"
}
```

### semantic_edge
```json
{
  "type": "semantic_edge",
  "id": "se_x",
  "scene_id": "sc_x",
  "chapter_id": "ch_x",
  "subject": "sn_a",
  "predicate": "enters",
  "object": "sn_b",
  "weight": 1.0
}
```

### semantic_transition
```json
{
  "type": "semantic_transition",
  "id": "stx_x",
  "scene_id": "sc_x",
  "op": "add_edge",
  "target_id": "se_x"
}
```

## Runtime Artifact Shape
```json
{
  "version": 1,
  "scene_id": "sc_x",
  "chapter_id": "ch_x",
  "nodes": [],
  "edges": [],
  "transitions": []
}
```

## Triplet Scoring Rule (v1)
Given candidate triples from parser/ontology resolution:
- Base score: `1.0`
- +`0.2` if both subject/object resolve to known ontology kinds
- +`0.1` if predicate in canonical edge kinds
- Cap: `1.5`

In v1 runtime, scores default to `1.0`; scoring extension may be enabled without changing schema.

## Law Boundary
Frame switching and semantic rendering are projection-only operations. They do not alter kernel replay law, canonical event truth, or saved deterministic state beyond UI projection fields.
