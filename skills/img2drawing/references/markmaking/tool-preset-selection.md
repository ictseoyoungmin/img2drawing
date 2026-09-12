# Tool preset selection

Tool presets provide reusable mark behavior. They are a vocabulary layer between semantic role and
per-stroke authored dynamics. A preset does not choose the path; the Agent still authors geometry
from the current task.

## Initial builtin vocabulary

The 1.0.3 runtime should expose equivalents of these roles as stable public presets:

- `construction-light` — light provisional construction with low visual authority;
- `gesture-flow` — pressure swell with a clean release for major motion;
- `form-pencil` — stable default descriptive pencil;
- `contour-weighted` — stronger ownership/overlap contour without turning every edge equally dark;
- `accent-dark` — short deliberate high-value emphasis;
- `hair-flick` — narrow directional mark with a fast terminal;
- `broad-graphite` — broad contact with paper/tooth material behavior;
- `hatch-light` — light value-building hatch;
- `hatch-heavy` — stronger hatch for deeper value while preserving line structure;
- `environment-line` — lower-priority contextual linework.

The exact runtime names become authoritative only when the public API implements them. Until then,
this leaf defines semantic intent, not permission to invent private renderer imports.

## Selection rule

Prefer the smallest preset that already expresses the intended line language. Then use per-stroke
modifiers for local variation.

Examples:

```text
face outline              -> form-pencil or contour-weighted
important overlap/contact -> contour-weighted
small eye/contact accent  -> accent-dark
fast hair terminal        -> hair-flick
large graphite shadow     -> broad-graphite
light construction axis   -> construction-light
repeated light value      -> hatch-light
background architecture   -> environment-line
```

These examples are routing hints, not automatic subject rules. Reference evidence and declared
intent outrank the example mapping.

## Do not collapse the vocabulary

A worker should not use one preset for an entire drawing simply because that is convenient. If the
reference requires multiple line behaviors, represent them explicitly. Conversely, do not create a
new preset for every stroke: ordinary local variation belongs in authored dynamics or modifiers.

## Runtime boundary

Use only documented public preset/tool names. If a needed behavior is not available, follow
`custom-tools.md` rather than importing a private renderer helper or reimplementing the pencil in
Pillow.
