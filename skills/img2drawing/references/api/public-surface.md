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
from img2drawing.vnext import retune_stroke, retune_strokes, sample_catmull_rom
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

For value regions, use the session's fill/replace-fill surface rather than manually generating
a cloud of synthetic value strokes.

## Markmaking and future public presets

The instruction graph may describe semantic line roles and intended style/tool preset families
before every 1.0.3 runtime name is implemented. Treat those documents as drawing intent, not as
permission to import private renderer helpers or invent unsupported keyword arguments.

When a public style/tool API lands, discover and use it through this documented surface. Until then,
express supported local variation with the existing public stroke/tool arguments and retune helpers.
If the runtime cannot express the requested line language, record that as a capability gap for
framework work.

## Residual provenance

`record_residual()`, the corrective edits, and `resolve_residual()` form one provenance chain.
For new corrections, the repairing mutation must carry the residual's own `observation_id`; do
not let a later observation become the mutation's implicit provenance. The after-inspection must
be taken after the edit and must match the current drawing. See `review/residual-correction.md`
for a complete executable pattern and the compatibility note for older persisted actions.

## Evidence and completion

`session.inspect()` only produces an inspection artifact; it does not by itself mean the Agent
has seen it. Call `session.record_evidence_read(inspection_id)` after actually viewing the
returned artifact, and only then call `session.finish(...)`. `finish()` rejects a canvas with no
current authored strokes, including a canvas whose earlier marks were all erased again. It also
rejects finishing on an inspection that was never confirmed read, a stale inspection, or any
session with an open residual.

`accepted_limitations` records acknowledged non-blocking limitations in the Agent's finish
decision. It does **not** bypass an open residual: close or reclassify the finding through the
correction workflow before finishing. See `review/completion.md`.

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
