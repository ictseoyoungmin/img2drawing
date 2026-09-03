# Public runtime surface

Read this file only when code must operate the runtime. Drawing knowledge belongs in the
visual instruction leaves, not in implementation details.

## Session and intent

Use public root imports such as:

- `DrawingSession`
- `DrawingIntent`
- `ReferenceAuthority`, `ReferenceConstraint`
- `PoseObservation`, `InitialConstruct`, `ConstructionMark`
- `author_initial_construct()`, `inspect_initial_construct()`
- `SubjectPalette`
- public inspection types/helpers such as `ROI`, `PlumbLine`, `GroundGuide`, `angle`, and
  `distance`

A minimal session begins without hard-coded drawing geometry:

```python
from img2drawing import DrawingIntent, DrawingSession

intent = DrawingIntent(drawing_mode="croquis", finish_intent="subject")
session = DrawingSession.create(subject="subject.png", output_dir="out", intent=intent)
```

The Agent must observe the current subject and author all geometry from that task. Do not
copy coordinates from documentation or unrelated runs.

## Current-state operations

The public session supports the stage-free workflow used by the skill: inspect the current
state, record a residual, apply history-safe stroke/fill edits, re-inspect, resolve or revise
the residual, and finish from current evidence.

Use public authored-element lookup when a later correction must locate an existing stroke
or fill. Use the supported replace/soften/delete operations rather than raster editing the
rendered PNG.

For value regions, use the public fill/replace-fill surface rather than manually generating
a cloud of synthetic value strokes.

## Output

Use the session's public final render, cursor render, and timelapse export operations so all
outputs share the persisted render profile and history.

## Boundary

Do not depend on private modules, compatibility shims, hidden attributes, or implementation
class names in skill-facing instructions. If a capability is not available through the
public root surface or a documented public session method, treat it as unavailable to the
skill until the runtime exposes it deliberately.
