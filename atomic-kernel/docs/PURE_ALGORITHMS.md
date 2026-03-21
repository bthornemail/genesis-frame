# Atomic Kernel — Pure Algorithms
## Single-Notation Pseudocode (Normative Draft)

Status: Normative Draft  
Authority: Algorithms and verified outputs only  
Date: 2026

---

## A1. Kernel Transition

Inputs:
- width `n`
- constant `C`
- state `x`

```text
mask = 2^n - 1

rotl(x,k,n) = ((x << k) | (x >> (n-k))) & mask
rotr(x,k,n) = ((x >> k) | (x << (n-k))) & mask

delta(x,C,n) =
  (rotl(x,1,n) XOR rotl(x,3,n) XOR rotr(x,2,n) XOR C) & mask
```

Replay:

```text
replay(x0, steps, C, n):
  x := x0
  repeat steps times:
    emit x
    x := delta(x,C,n)
```

---

## A2. Mixed-Radix Encode

Inputs:
- integer `v >= 0`
- radix list `R = [r0, r1, ..., rk-1]`, each `ri >= 2`

Output:
- coordinate list `coords = [c0, c1, ..., ck]`

```text
mixed_encode(v, R):
  coords := []
  for r in R:
    coords.append(v mod r)
    v := floor(v / r)
  coords.append(v)
  return coords
```

---

## A3. Mixed-Radix Decode

Inputs:
- coordinate list `coords = [c0, c1, ..., ck]`
- radix list `R = [r0, r1, ..., rk-1]`

Output:
- integer `v`

```text
mixed_decode(coords, R):
  v := coords[last]
  for i from len(R)-1 down to 0:
    v := coords[i] + R[i] * v
  return v
```

Invariant:

```text
mixed_decode(mixed_encode(v,R), R) = v
```

---

## A4. Basis Projection / Interpretation

Inputs:
- value `v`
- plane `p`
- basis spec `b`

Basis kinds:
- `2`, `8`, `10`, `16`, `36`, `codepoint`, `mixed`

Projection:

```text
project_value(v, p, b):
  if b.kind = "2"         return ("2",         binary(v))
  if b.kind = "8"         return ("8",         octal(v))
  if b.kind = "10"        return ("10",        decimal(v))
  if b.kind = "16"        return ("16",        hex(v))
  if b.kind = "36"        return ("36",        base36(v))
  if b.kind = "codepoint" return ("codepoint", [v mod 65536, floor(v/65536)])
  if b.kind = "mixed"     return ("mixed",     mixed_encode(v, b.radices))
```

Interpretation:

```text
interpret_value(repr, p, b):
  if b.kind = "2"         return parse_binary(repr)
  if b.kind = "8"         return parse_octal(repr)
  if b.kind = "10"        return parse_decimal(repr)
  if b.kind = "16"        return parse_hex(repr)
  if b.kind = "36"        return parse_base36(repr)
  if b.kind = "codepoint" return repr[0] + 65536 * repr[1]
  if b.kind = "mixed"     return mixed_decode(repr, b.radices)
```

Invariant:

```text
interpret_value(project_value(v,p,b), p, b) = v
```

---

## A5. Structural Plane Projection

Planes:

```text
P = [FS, GS, RS, US]
```

Inputs:
- entity state `e`
- frame `f`

```text
project_entity(e, plane, frame):
  return projection_function(e, plane, frame)
```

```text
projection_vector(e, frame):
  return [
    project_entity(e, FS, frame),
    project_entity(e, GS, frame),
    project_entity(e, RS, frame),
    project_entity(e, US, frame)
  ]
```

```text
is_collapsed(V):
  return all elements of V are equal
```

```text
is_divergent(V):
  return not is_collapsed(V)
```

```text
continuation_surface(V):
  return unique elements of V in deterministic order
```

---

## A6. Incidence Schedule

Canonical 7-line schedule:

```text
L0 = (0,1,3)
L1 = (0,2,5)
L2 = (0,4,6)
L3 = (1,2,4)
L4 = (1,5,6)
L5 = (2,3,6)
L6 = (3,4,5)
```

```text
fano_triplet(tick):
  return L[tick mod 7]
```

```text
frame_at_tick(tick, basis_spec, plane):
  return {
    tick: tick,
    plane: plane,
    basis_spec: basis_spec,
    triplet: fano_triplet(tick)
  }
```

```text
step_projection(e, tick, basis_spec):
  f := frame_at_tick(tick, basis_spec, RS)
  V := projection_vector(e, f)

  if is_collapsed(V):
    return ("collapsed", V[0])
  else:
    return ("divergent", continuation_surface(V))
```

---

## A7. Carrier Verification

Package shape:

```text
pkg = {
  type,
  version,
  artifact_kind,
  payload_bytes,
  fingerprint_algo,
  fingerprint
}
```

```text
verify_package(pkg):
  computed := hash(pkg.payload_bytes, pkg.fingerprint_algo)
  return computed = pkg.fingerprint
```

```text
apply_package(pkg):
  if verify_package(pkg) = false:
    reject
  else:
    parse payload
    validate kind/schema
    apply
```

---

## Minimal Composition

```text
x(t+1) = delta(x(t), C, n)

frame(t) = {
  plane,
  basis_spec,
  triplet = fano_triplet(t)
}

repr = project_value(value, plane, basis_spec)
value = interpret_value(repr, plane, basis_spec)

V = projection_vector(entity_state, frame(t))

if all equal(V):
  output = single projection
else:
  output = deterministic unique set(V)

shared_payload_valid = verify_package(pkg)
```

---

## Pure Invariants

```text
1. delta is deterministic
2. replay is deterministic
3. mixed_decode(mixed_encode(v,R),R) = v
4. interpret_value(project_value(v,p,b),p,b) = v
5. fano_triplet(t+7) = fano_triplet(t)
6. projection_vector is deterministic
7. continuation_surface is deterministic
8. invalid package verification rejects
```

---

## Smallest Complete Form

```text
A1. delta
A2. replay
A3. mixed_encode
A4. mixed_decode
A5. project_value
A6. interpret_value
A7. fano_triplet
A8. frame_at_tick
A9. projection_vector
A10. is_collapsed / continuation_surface
A11. verify_package
```
