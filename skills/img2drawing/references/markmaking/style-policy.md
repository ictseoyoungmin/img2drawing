# Style policy

Style policy controls how the drawing runtime interprets authored marks at the whole-drawing level.
It does not decide geometry. The reference or declared drawing intent remains the authority for
shape, pose, topology, placement, and visible structure.

Use this leaf when the question is not **where should the line go?** but **how should an otherwise
correct mark read?**

## Default

If the user does not request a stylized line language, use `canonical-pencil`.

Do not infer a decorative style merely because one renderer behavior happens to look attractive.
Choose a non-canonical style only when the user explicitly requests it or when the declared drawing
intent clearly depends on that material language.

## Initial policy families

### `canonical-pencil`

Use for observation drawing, croquis completion, figure drawing, and other work where authored
pressure, opacity, and value intent should remain legible.

Priority:

1. reference/declaration fidelity;
2. authored value authority;
3. coherent line weight and pressure;
4. graphite material expression.

Broad graphite may add tooth, shoulder breakup, and local deposition variation, but material
behavior should not casually erase a deliberately strong authored value.

### `manga-light`

Use for explicitly requested airy monochrome, delicate romance/shojo-like line language, or other
work where elegance and lightness may outrank strict broad-stroke value preservation.

This policy may intentionally allow a broad contact to remain lighter in its center than
`canonical-pencil`. That behavior is not automatically a defect under this preset. It becomes a
defect only when it contradicts the requested style, loses continuity, or makes important forms
unreadable.

### `dry-graphite-expressive`

Use when broad graphite texture, paper tooth, grain, edge breakup, and local deposition variation
are part of the requested visual language.

Do not use this preset to hide weak structure. Strong material expression still follows the same
geometry and residual-routing rules as the rest of the skill.

## Style is not a stroke vocabulary

A style policy does not force every mark to behave the same way. One `canonical-pencil` drawing may
mix construction lines, gesture sweeps, weighted contours, dark accents, hair flicks, hatching, and
broad graphite. The semantic role and tool preset for each mark are separate decisions.

Likewise, the same semantic role may be resolved differently by different style policies. A hair
mark can remain semantically `hair` while `canonical-pencil` and `manga-light` give it different
material defaults.

## Authority ordering

For ordinary observed work:

```text
reference / declared intent
  > geometry and topology
  > semantic role of the mark
  > explicitly authored dynamics
  > style material policy
  > renderer incidental behavior
```

A renderer artifact is never promoted into geometry truth. If a style materially changes the
meaning of a correct mark, first ask whether that change is intentional under the active policy.
If not, route it as a markmaking/material residual rather than redrawing the geometry by accident.
