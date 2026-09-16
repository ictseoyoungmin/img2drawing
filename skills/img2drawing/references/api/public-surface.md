# Public runtime surface

Read this file before authoring the first programmatic drawing mark. Drawing knowledge belongs in
the visual and markmaking instruction leaves; this file only tells the Agent how to operate the
supported runtime without reading its implementation.

## Worker discovery contract

The ordinary drawing worker is **runtime-aware and implementation-blind**.

The worker must know that `img2drawing` already provides the drawing runtime. Final authored marks
must enter through `DrawingSession` and documented public helpers so history, inspection, replay,
render-profile authority, and finish provenance remain intact.

Do **not** replace the runtime with a hand-written Pillow/ImageDraw script, raw OpenCV raster edits,
SVG/canvas drawing, a custom `StrokeCanvas`, or another bespoke rasterizer. Pillow, NumPy, OpenCV,
crops, overlays, and similar tools may support bounded observation/evidence work where allowed, but
they are not alternative final-authoring runtimes.

The ordinary worker also does **not** need to inspect the full `src/` tree, private renderer classes,
cache internals, or persistence implementation before drawing. Read implementation only when the
user explicitly asks for framework work, or when a demonstrated runtime defect requires debugging.
If the public surface cannot express a required mark, record a runtime capability gap instead of
silently bypassing it.

For a compact machine-readable confirmation of this boundary, read
[`runtime-discovery.md`](runtime-discovery.md) or call:

```python
from img2drawing.runtime import runtime_capabilities

caps = runtime_capabilities()
assert caps.orchestration == "DrawingSession"
assert caps.final_authoring_runtime
assert not caps.implementation_read_required
assert caps.capability_gap_policy == "report-not-bypass"
```

This manifest is deliberately source-opaque. It exists to prevent both failure modes: forgetting
that the runtime exists and crawling private implementation merely to discover ordinary drawing
capabilities.

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
from img2drawing.runtime import runtime_capabilities
from img2drawing.vnext import (
    resolve_mark_for_intent,
    retune_stroke,
    retune_strokes,
    sample_catmull_rom,
)
```

Advanced vNext records, guide objects, schemas, derived authoring records, and authoring helpers
remain available from `img2drawing.vnext` when a framework/debugging task actually needs them.
Low-level stroke/history types live under `img2drawing.core`. These are not alternative
orchestration routes and ordinary drawing workers should not start there.

Pre-0.6.0rc2 direct root imports for those still-owned specialized names resolve through deprecated
compatibility shims for existing callers, but they are intentionally absent from
`img2drawing.__all__` and normal discovery.

Historical R23 orchestration is different: the post-v1.0.2 source tree no longer ships
`img2drawing.legacy.r23`, and R23-only root names such as `DrawingRun` and `StageContract` no longer
resolve through a hidden fallback. The immutable v1.0.2 release remains the reference point for
that retired compatibility namespace.

## Current-state operations

The public session supports the stage-free workflow used by the skill: inspect the current
state, record a residual, apply history-safe stroke edits, re-inspect, resolve or revise
the residual, and finish from current evidence.

Use public authored-element lookup when a later correction must locate an existing stroke.
Use the supported replace/soften/delete operations rather than raster editing the rendered PNG.

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

When several strokes share one coherent material residual, use `retune_strokes()` rather than
repeating manual geometry submissions:

```python
from img2drawing.vnext import retune_strokes

retune_strokes(
    session,
    connected_edge_ids,
    reason="one continuous boundary is broken by premature endpoint taper",
    tool_overrides={"taper_in": 0.01, "taper_out": 0.02},
    metadata={"semantic_group": "continuous-boundary"},
)
```

The helper resolves all requested current descendants before the first edit, rejects duplicate
current strokes, and then records one ordinary explicit replacement action per stroke. The group
is convenience and provenance context, not a new batch action, runtime stage, or lifecycle state.

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

For value work, author the visible mark language explicitly through `draw()` or `draw_many()`.
Group directional hatching or other value strokes by observed form/light family, keep each stroke
addressable in history, and revise the responsible strokes when the value read is disproved. Do not
substitute a region-to-hatch generator for those artistic decisions.

## WIP guide visibility

Construction/search marks must remain visually readable while they are still carrying a live
hypothesis. Do not make an authored guide permanently dark merely so the Agent can see it, and do
not weaken the final pencil renderer to expose it. After a **fresh** `session.inspect()`, create a
display-only WIP view for the explicit current stroke IDs that need stronger visibility:

```python
from img2drawing.inspection import render_wip_guides

inspection_id = session.inspection_history[-1]["inspection_id"]
wip = render_wip_guides(
    session,
    (shoulder_axis_id, pelvis_axis_id, face_cross_id),
    inspection_id=inspection_id,
    color=(40, 120, 255),       # Agent-selected contrast colour
    width_scale=2.2,
    opacity=0.78,
)
```

The runtime deliberately does **not** infer which lines are guides from role names, geometry, or
stage labels. The Agent chooses the stroke IDs and may choose a contrasting RGB colour, width boost,
and opacity. The helper rejects stale inspections and stroke IDs that are no longer current.

`render_wip_guides()` is inspection-only. It writes a derived WIP PNG + manifest under the session
output directory and does not mutate history, current geometry, `RenderProfile`, canonical
`raw_drawing.png`, replay, or final output. Different style choices receive different artifact
names instead of overwriting one another.

This visibility boost is temporary evidence, not permission to keep construction clutter in the
finished drawing. Once a stronger description supersedes the guide, use the normal
KEEP/SOFTEN/RETIRE decision and edit the authored stroke itself when appropriate.

## Markmaking presets and the draw adapter

The 1.0.3 runtime exposes semantic markmaking roles/presets through the public vNext resolver. Names
such as `gesture-flow`, `contour-weighted`, and `broad-graphite` describe semantic mark behavior;
they are **not automatically literal `DrawingSession.draw(tool=...)` values**.

Resolve semantic intent first, then pass the returned public draw kwargs to the session:

```python
from img2drawing.vnext import resolve_mark_for_intent

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

`ResolvedMark.draw_kwargs()` maps the semantic preset onto the supported runtime tool/grade/
overrides and records markmaking provenance. Do not guess that `tool="gesture-flow"` or
`tool="broad-graphite"` is valid merely because that semantic preset appears in the instruction
graph. Direct `tool=` values such as `continuous_pencil` are valid only when this public surface or
the runtime explicitly documents them as direct draw tools.

If the runtime cannot express the requested line language through the public resolver, supported
stroke/tool arguments, or retune helpers, record that as a capability gap for framework work rather
than importing a private renderer helper or inventing unsupported keyword arguments.

## Residual provenance

`record_residual()`, the corrective mutation, fresh inspection, and `resolve_residual()` form one
public provenance chain. Artistic diagnosis stays in `../review/residual-correction.md`; this
section owns how to record and execute that decision.

Bind the corrective edit to the **same `observation_id` passed to `record_residual()`**:

```python
observation_id = session.observe({"jaw": "contour sits too low at the cheek handoff"})
before_inspection_id = session.inspection_history[-1]["inspection_id"]

residual_id = session.record_residual(
    observation_id=observation_id,
    observation="jaw contour sits too low at the cheek handoff",
    scope="head/jaw",
    severity="material",
    impact_rationale="the face shape reads heavier than the reference",
    responsible_premise="jaw contour placement",
    responsible_stroke_ids=(jaw_stroke_id,),
    planned_edit="raise the jaw contour while preserving the cheek anchor",
    before_inspection_id=before_inspection_id,
)

fix_action_id = session.replace_stroke(
    jaw_stroke_id,
    corrected_jaw_points,
    observation_id=observation_id,
    reason="raise the jaw contour to the observed cheek-to-chin relation",
)
session.inspect()
after_inspection_id = session.inspection_history[-1]["inspection_id"]

session.resolve_residual(
    residual_id,
    action_ids=(fix_action_id,),
    after_inspection_id=after_inspection_id,
    rationale="the fresh inspection now matches the observed jaw handoff",
)
```

If a later `session.observe(...)` call occurs before the repair, do **not** rely on a mutation
method's default-to-latest observation behavior for the older residual. Pass that residual's
original `observation_id` explicitly. A repairing edit authored under a different later observation
is rejected with `correction action observation mismatch`.

If the finding itself materially changes before repair, record a new residual under the new
observation instead of pretending the old provenance still owns the fix. Persisted historical
actions may contain legacy/unobserved provenance tolerated for compatibility; that tolerance is not
the authoring contract for new corrections.

`resolve_residual()` requires an after-inspection whose drawing state differs from the before-state
and matches the current drawing. Inspect **after** the edit, then actually view that artifact before
deciding the visual mismatch is resolved. The runtime checks provenance freshness; it does not make
the artistic verdict.

## Evidence and completion mechanics

`session.inspect()` only produces an inspection artifact; it does not by itself mean the Agent has
seen it. After actually viewing the artifact, call:

```python
inspection_id = session.inspection_history[-1]["inspection_id"]
session.record_evidence_read(inspection_id)
```

`DrawingSession.finish()` then binds the Agent's completion decision to current evidence. It rejects
finishing when:

- the current drawing has no authored strokes, including a session whose earlier marks were all
  erased again;
- the final inspection has not been explicitly recorded as read;
- the inspection is stale, superseded, or predates the current intent;
- any residual record remains open.

These checks are mechanical. They do not certify artistic quality. Decide whether the drawing is
actually finished through `../review/completion.md`, then use the public finish call.

`accepted_limitations` records acknowledged non-blocking limitations in that Agent decision. It does
**not** bypass an open residual: resolve or re-record the finding through the residual provenance
chain before finishing.

## Output

Use the session's public final render, cursor render, and timelapse export operations so all
outputs share the persisted render profile and history. `inspect()` renders through the same
persisted `RenderProfile` (paper, background, graphite) as the final export; only its output
scale is pinned to 1x canvas space for registration/ROI/measurement geometry.

## Boundary

Do not depend on private modules, compatibility shims, hidden attributes, or implementation
class names in skill-facing instructions. The package root is the normal orchestration surface;
specialized documented namespaces are capability libraries, not competing session frameworks.

The intended operational sequence is therefore:

```text
visual / artistic decision
  -> instruction-graph routing
  -> documented public runtime operation
  -> render / inspect
  -> residual correction
```

not:

```text
read renderer internals
  -> imitate implementation details
  -> draw through a bespoke raster script
```
