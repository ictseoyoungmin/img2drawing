# Tool preset selection

Tool presets provide reusable mark behavior. They are a vocabulary layer between semantic role and
per-stroke authored dynamics. A preset does not choose the path; the Agent still authors geometry
from the current task.

## Initial builtin vocabulary

The 1.0.3 runtime exposes these semantic preset roles through the public markmaking resolver:

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

These are **semantic markmaking preset IDs**, not necessarily literal values accepted by
`DrawingSession.draw(tool=...)`. The resolver maps them onto the supported runtime tool plus grade,
overrides, and provenance. Do not pass `tool="gesture-flow"`, `tool="broad-graphite"`, or another
semantic preset ID directly to `session.draw()` unless the documented draw surface explicitly names
that same string as a runtime tool.

## Selection rule

Prefer the smallest semantic preset that already expresses the intended line language. Then use
per-stroke modifiers for local variation.

Examples:

```text
face outline              -> form-pencil or contour-weighted
important overlap/contact -> contour-weighted
small eye/contact accent  -> accent-dark
fast hair terminal        -> hair-flick
large graphite shadow     -> broad-graphite
light construction axis   -> construction-light
major motion sweep        -> gesture-flow
repeated light value      -> hatch-light
background architecture   -> environment-line
```

These examples are routing hints, not automatic subject rules. Reference evidence and declared
intent outrank the example mapping.

## Runtime adapter

Resolve semantic markmaking through the public authoring API, then pass the resolved draw kwargs to the
session:

```python
from img2drawing.authoring import resolve_mark_for_intent

mark = resolve_mark_for_intent(
    session.intent,
    "gesture",
    tool_preset="gesture-flow",
)

session.draw(
    points,
    part="dominant-action",
    **mark.draw_kwargs(),
)
```

`ResolvedMark.draw_kwargs()` supplies the supported runtime tool representation and records the
markmaking digest/provenance. This adapter boundary prevents semantic vocabulary from being confused
with low-level tool preset names such as `form_pencil`, `construction_pencil`, or
`continuous_pencil`.

If the path is already observed correctly but a local pressure value must be authored explicitly,
keep the geometry decision separate and use only supported public modifiers/retune operations rather
than bypassing the resolver with a private renderer setting.

## Do not collapse the vocabulary

A worker should not use one preset for an entire drawing simply because that is convenient. If the
reference requires multiple line behaviors, represent them explicitly. Conversely, do not create a
new preset for every stroke: ordinary local variation belongs in authored dynamics or modifiers.

## Runtime boundary

Use only documented semantic presets and public runtime tool names. If a needed behavior is not
available, follow `custom-tools.md` rather than importing a private renderer helper or reimplementing
the pencil in Pillow.
