# The Atomic Projection Law

## A Reduction of a Narrative-Computational System to a Minimal Deterministic Kernel

**Author:** Brian Thorne et al.  
**Status:** Formal Draft  
**Authority:** The algorithm is the only source of truth. All representations are projections.

---

## Abstract

The system is reduced by quotient analysis: remove any structure that can be removed while preserving canonical unfold, replay, and projection. The irreducible law is the deterministic delta transformation over bounded state. Narrative, semantic graph, avatars, geometry, UI, and transport are derived projection layers.

---

## 1. Reduction Principle

Question:

> What structure can be removed while the same canonical unfold, replay, and projection still results?

Classification:

- Fundamental: removing it changes canonical output.
- Derived: removing it does not change canonical output and it can be reconstructed.

---

## 2. Minimal Kernel Law

\[
\delta(x) = \mathrm{rotl}(x,1)\oplus\mathrm{rotl}(x,3)\oplus\mathrm{rotr}(x,2)\oplus C
\]

with fixed-width masking by \(2^n-1\).

Properties:

- Closed finite state space.
- Deterministic replay.
- No external wall-clock dependency (time = iteration index).

---

## 3. Derived Numeric Structure

Empirical 16-bit result:

- period \(= 8\)

Prime coupling:

- smallest prime with decimal period 8 is \(73\)
- \(1/73 = 0.\overline{01369863}\)
- \(B = [0,1,3,6,9,8,6,3]\)
- \(W = \sum B = 36\)

Orbit encoding:

\[
(\mathrm{orbit},\mathrm{offset})=\mathrm{divmod}(t,W)
\]

---

## 4. Projection Law

All higher outputs are projections of invariant state.

- narrative: \(f(x_t)\)
- semantic graph: \(g(x_t)\)
- visual chain: artifact -> graph -> SVG -> OBJ/MTL -> GLB -> XR
- embodiment: entity invariant, avatar projection

Frame rule:

- no mutation inside a frame
- apply changes on transition boundary

---

## 5. Stateless Projection Surface

Runtime rendering:

\[
\mathrm{render}(x_t,P)
\]

where \(x_t\) is canonical state and \(P\) is projection parameters (frame, basis, mode, avatar, etc.).

Canonical truth lives in the law/state, not the renderer.

---

## 6. Final Reduction Statement

Removing UI, assets, narrative text, graph views, avatars, and carriers still leaves the generating law:

\[
\delta(x)
\]

Everything else is reconstructible projection.

---

## 7. Conclusion

This system is a deterministic orbit generator with multiple projection families. If two systems share the same delta law and replay inputs, they produce the same canonical unfold regardless of representation.

