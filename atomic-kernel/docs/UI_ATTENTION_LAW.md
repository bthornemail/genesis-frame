# UI Attention Law (Normative)

The primary interaction surface SHALL expose exactly these controls:

1. `Mode`
2. `Frame`
3. `Attention` (`Narrow` / `Expand`)
4. `Depth` (`More` / `Less`)

Formal rule:

> Every interactive entity MUST be reachable through `Mode + Frame + Attention + Depth`.  
> No additional always-visible primary controls are permitted.

Constraints:

- Secondary tools MUST be hidden by default.
- Secondary tools MAY be revealed only through `More`.
- Secondary tools MUST NOT create a second primary navigation grammar.
- `Attention` and `Depth` are projection controls only and MUST NOT mutate canonical replay truth.

Verification target:

- Startup strict snapshot: `docs/screenshots/ui-strict-startup-v2.png`
- Expected visible primary controls: `Mode`, `Frame`, `Narrow`, `Expand`, `More` (or `Less` when expanded).

