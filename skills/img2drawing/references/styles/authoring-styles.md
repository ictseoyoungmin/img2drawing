# Authoring styles

`StyleGuide` tells the Agent how to author marks. `RenderProfile` tells the runtime how to
materialize already-authored marks. Selecting a style never edits geometry, changes the
renderer, or applies a filter to a PNG.

## Retained presets

Use the smallest preset that expresses the requested policy:

- `pencil_loose`: pressure/speed variation, economical searching lines, visible useful
  construction, sparse value, lively selective edges;
- `graphite_academic`: measured strokes, connected form, controlled construction,
  grouped values, observed edge turns; and
- `graphite_tonal`: form-directed boundaries, compact calibrated value regions,
  preserved lights, grouped detail, and hard/soft/lost edge hierarchy.

Resolve one base and replace only named fields:

```python
style = resolve_style_guide(
    "graphite_academic",
    {"edge_policy": ("sharpen only the observed contact edge",)},
)
```

Unknown fields, another base, inheritance, and registry/plugin composition are rejected.
The result is a complete portable `StyleGuide`, not a chain of parents.

## Structured custom guidance

The Agent structures requested prose explicitly; the runtime does not infer a style from
free text:

```python
custom = StyleGuide.custom(
    "custom:angular-quiet",
    line_behavior=("use angular deliberate line changes",),
    construction_visibility=("retain only composition-bearing axes",),
    detail_policy=("keep detail sparse outside the focal shape",),
    value_policy=("use one quiet supporting value family",),
    edge_policy=("reserve the sharpest edge for the focal turn",),
    authoring_notes=("preserve subject geometry and declared constraints",),
)
style = resolve_style_guide("custom:angular-quiet", custom=custom)
```

If the request contains unresolved language, pass the terms as `unresolved_terms`; the
resolver raises `StyleClarificationRequired`. If a requested style instruction conflicts
with task, reference, preserved hybrid constraint, or geometry truth, pass the named
conflict as `conflicts`; it raises `StyleConflictError`. These are explicit Agent-authored
facts, not automatic semantic classification.

## Precedence and mid-session changes

```text
task/reference/geometry truth > finish policy > style preference
```

Use `session.set_intent()` to record a style-profile change. That event changes no action,
stroke, value region, renderer, or existing pixel. Decide which marks to keep, retire,
replace, or add, then perform those choices through the ordinary explicit edit API. The
result remains one append-only history with normal checkpoint, replay, resume, inspection,
and correction provenance.

For graphite material behavior and grade/contact guidance, read
[`../pencil/graphite.md`](../pencil/graphite.md). That material reference does not define
a second style registry.
