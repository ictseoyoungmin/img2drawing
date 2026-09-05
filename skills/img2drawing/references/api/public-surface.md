# Public runtime surface

Read this file only when code must operate the runtime. Drawing knowledge belongs in the
visual instruction leaves, not in implementation details.

## Canonical package root

Normal Agent/user code should discover one orchestration route. The package root intentionally
contains only the session, its declarative inputs, and the small observed-construction facade:

- `DrawingSession`
- `DrawingIntent`
- `ReferenceAuthority`, `ReferenceConstraint`, `ReferenceUnavailableError`
- `RenderProfile`
- `PoseObservation`, `InitialConstruct`, `ConstructionMark`
- `observe_pose()`, `author_initial_construct()`, `inspect_initial_construct()`

A minimal session begins without hard-coded drawing geometry:

```python
from img2drawing import DrawingIntent, DrawingSession

intent = DrawingIntent(drawing_mode="croquis", finish_intent="subject")
session = DrawingSession.create(subject="subject.png", output_dir="out", intent=intent)
```

The Agent must observe the current subject and author all geometry from that task. Do not
copy coordinates from documentation or unrelated runs.

## Specialized public namespaces

Do not widen the root merely because a utility is public. Import specialized tools from the
namespace that owns them:

```python
from img2drawing.inspection import GroundGuide, PlumbLine, ROI, angle, distance
from img2drawing.observation import SubjectPalette
from img2drawing.vnext import retune_stroke, sample_catmull_rom
```

Advanced vNext records, guide objects, schemas, derived authoring records, and authoring helpers
remain available from `img2drawing.vnext` when a framework/debugging task actually needs them.
Low-level stroke/history types live under `img2drawing.core`. These are not alternative
orchestration routes and ordinary drawing workers should not start there.

Pre-0.6.0rc2 direct root imports for those specialized names resolve through deprecated
compatibility shims for existing callers, but they are intentionally absent from
`img2drawing.__all__` and normal discovery.

## Current-state operations

The public session supports the stage-free workflow used by the skill: inspect the current
state, record a residual, apply history-safe stroke/fill edits, re-inspect, resolve or revise
the residual, and finish from current evidence.

Use public authored-element lookup when a later correction must locate an existing stroke
or fill. Use the supported replace/soften/delete operations rather than raster editing the
rendered PNG.

When only stroke material is wrong and the path is already correct, prefer:

```python
from img2drawing.vnext import retune_stroke

retune_stroke(
    session,
    stroke_id,
    reason="connected edge is geometrically correct but endpoint taper breaks continuity",
    tool_overrides={"taper_in": 0.02, "taper_out": 0.03},
)
```

`retune_stroke()` resolves the current replacement descendant and emits the existing
`replace_stroke` history action while preserving points, role, part, confidence, layer, stable
stroke identity, and explicitly authored pressure. Derived pressure is regenerated so a taper or
pressure retune can actually change the rendered material. It does not create a new persistence
schema.

For a smooth observed interval, a worker may use the deterministic shared sampler instead of
reimplementing spline math per run:

```python
from img2drawing.vnext import sample_catmull_rom

points = sample_catmull_rom(control_points, spacing=3.0)
session.draw(points, role="contour", part="observed-boundary")
```

Do not run the sampler through an observed cusp, corner, component join, or tangency break. Split
those intervals and author the topology explicitly.

For boundaries whose endpoints should read continuously, `tool="continuous_pencil"` provides the
form-pencil material family with very low endpoint taper. Use it only when the observed boundary
is actually continuous; it is not a subject-specific or mechanical-object preset.

For value regions, use the session's fill/replace-fill surface rather than manually generating
a cloud of synthetic value strokes.

## Output

Use the session's public final render, cursor render, and timelapse export operations so all
outputs share the persisted render profile and history.

## Boundary

Do not depend on private modules, compatibility shims, hidden attributes, or implementation
class names in skill-facing instructions. The package root is the normal orchestration surface;
specialized documented namespaces are capability libraries, not competing session frameworks.