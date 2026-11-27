# Mixed-media public API

Use this leaf only with requested ink or mixed-media authoring. The existing
[public surface](public-surface.md) owns session, observation, inspection and completion;
[mixed-media markmaking](../markmaking/mixed-media.md) owns visual decisions.
All marks use the same session and ordered history. Coordinates/widths are logical pixels.

## Discover and select before authoring

For a new mixed drawing select `RenderProfile.mixed_media(width, height)` explicitly.
It selects the current mixed contract (v3); `screentones=False` selects v2 (styled
paths without tones), `styled_paths=False` selects v1 (round paths and solid areas).
For resumed work keep the stored profile. Call `runtime_capabilities(session.render_profile)`;
the unscoped manifest describes pencil defaults. Do not silently migrate older profiles.
Inspect the available helpers before choosing an unsupported mark. For new mixed sessions
the graphite contact sub-contract is normalized v3. No special style name selects this profile.

## Author explicit material and geometry

All helpers below are exported from `img2drawing.authoring`.

- `g_pen(controls, pressure_knots=..., max_width=..., min_width=..., gamma=...)`:
  piecewise pressure knots `(normalized_arc_position, pressure)` include 0 and 1.
  Choose polyline or `geometry="bezier"` (explicit cubic chain, 3n+1 controls).
  `start_cap`/`end_cap`: round, butt, square or point; point requires zero endpoint width
  and sufficient taper. Join round, miter or bevel; miter_limit 1–16, default 4.
- `fineliner(controls, width=..., geometry=..., cap=..., join=...)`: constant width,
  round/butt/square caps. Styled joins/caps require v2 or later.
- `ink_brush(controls, pressure_knots=..., max_width=..., min_width=...)`: opaque
  wet brush, round/point tips, round joins. All three return editable `PenDefinition`;
  use `.action(...)` to resolve once and retain the recipe.
- `solid_ink(outer, holes=(), paint="black")`: explicitly closed simple rings, with
  disjoint, strictly interior holes. Use `sample_ink_contour(controls, tolerance=.05)`
  for a deliberately closed cubic chain; its sampled ring is the area authority.
  No automatic closure, inferred boundary, flood fill or source-pixel mask.
- `dot_screentone(outer, holes=(), pitch=6., coverage=.3, angle_degrees=45.,
  phase_origin=(0., 0.))`: v3 only. Pitch 4–512 logical pixels, at least 8 working
  samples per period. Coverage 0–1, not alpha. The origin is a dot centre, angles
  clockwise in page coordinates. Or omit coverage and pass
  `gradient=ToneGradient(start, end, start_coverage, end_coverage)`.
  Tones are black; white is a separate ink path/area. No dot-per-action expansion.
- For pen/brush/solid ink, `paint="white"` is opaque white, not erase.

`InkElement(element_id, mark, role, part=None, layer=0)` binds one explicit mark
to its semantic owner. `InkAction(action_id, kind, element_id, element, observation_id,
source_observation, reason)` accepts ink.add, ink.replace, ink.delete. Add/replace
carry a matching element; delete carries None. Use unique action IDs and the same
element ID for corrections. Observe first; supply recorded observation ID, reason
and source explicitly. Layer sorts first; insertion order within a layer is stable.
The pen recipe's `.action` takes the same identity, observation, source, reason,
role, part, layer and optional kind. Ink is not a pencil grade.

## Runnable API smoke example

This synthetic, subjectless swatch demonstrates signatures, not a drawing template.
Never reuse its coordinates as observed subject geometry. Run in a fresh working
directory; no reference file or renderer-source inspection is needed. In real
drawing, actually inspect the preview before committing and judge the current image
before recording an evidence read or finish.

```python
# mixed-media-smoke
from dataclasses import replace
from pathlib import Path
from img2drawing import DrawingSession, DrawingIntent, ReferenceAuthority, RenderProfile
from img2drawing.runtime import runtime_capabilities
from img2drawing.authoring import (
    g_pen, fineliner, ink_brush, solid_ink, dot_screentone, ToneGradient,
    InkElement, InkAction, apply_ink_actions, preview_ink_actions,
    current_ink_element,
)

out = Path("mixed-demo")
profile = RenderProfile.mixed_media(128, 96, supersample=4)
caps = runtime_capabilities(profile)
assert "img2drawing.authoring.dot_screentone" in caps.authoring_helpers
s = DrawingSession.create(
    canvas=(128, 96), output_dir=out, render_profile=profile,
    intent=DrawingIntent(reference_mode="imaginative", drawing_mode="free_draw",
                         finish_intent="expressive", style_profile="custom:ink-study"),
    reference_authority=ReferenceAuthority.imaginative(("explicit API swatch",)),
)
oid = s.observe({"decision": "synthetic contour, shadow and tone samples"})
guide = s.draw(((8, 48), (120, 48)), stroke_id="guide", observation_id=oid)

def rect(x0, y0, x1, y1):
    return ((x0,y0), (x1,y0), (x1,y1), (x0,y1), (x0,y0))

def add(aid, sid, mark, role, layer=0):
    return InkAction(aid, "ink.add", sid, InkElement(sid, mark, role, "swatch", layer),
                     oid, "declared swatch", "explicit material probe")

pen = g_pen(((10, 25), (45, 10), (85, 40), (118, 22)), geometry="bezier",
            pressure_knots=((0,.25), (.5,1), (1,.25)), min_width=.4, max_width=5)
brush = ink_brush(((12, 38), (45, 38)), pressure_knots=((0,1),(1,1)), max_width=8)
actions = [
    pen.action(action_id="ink-1", element_id="contour", observation_id=oid,
               source_observation="declared swatch", reason="variable weight", role="contour"),
    add("ink-2", "fine", fineliner(((72,12),(115,12)), width=1.2, cap="butt").resolve(), "detail"),
    brush.action(action_id="ink-3", element_id="brush", observation_id=oid,
                 source_observation="declared swatch", reason="opaque contact", role="value"),
    add("ink-4", "shadow", solid_ink(rect(8,52,54,88), holes=(rect(20,62,32,76),)), "value"),
    add("ink-5", "tone", dot_screentone(rect(64,52,120,88), pitch=6,
        gradient=ToneGradient((64,52),(120,52),.15,.85), angle_degrees=30), "value"),
    add("ink-6", "light", solid_ink(rect(40,60,48,70), paint="white"), "highlight", 1),
]
apply_ink_actions(s, actions)
old = current_ink_element(s, "tone")
changed = replace(old, mark=replace(old.mark, gradient=None, coverage=.45))
edit = InkAction("ink-7", "ink.replace", "tone", changed, oid,
                 "declared swatch", "test explicit coverage correction")
p = preview_ink_actions(s, [edit], out / "tone-preview.png")
# Real worker: view the preview and commit only if it supports the correction.
apply_ink_actions(s, [edit], expected_cursor=p["base_cursor"],
    expected_state_hash=p["base_state_hash"], expected_action_digest=p["action_digest"],
    expected_profile_digest=p["profile_digest"])
assert s.render_final(out / "checked.png").pixel_sha256 == p["pixel_sha256"]
s.delete_stroke(guide, observation_id=oid, reason="retire provisional guide")
s.inspect(supersample=profile.supersample)
# Inspect the sheet yourself; this mechanical example makes no artistic finish claim.
final = s.render_final(out / "final.png")
s = DrawingSession.resume(s.checkpoint())
assert s.render_final(out / "resumed.png").pixel_sha256 == final.pixel_sha256
assert len(s.authored_elements(element_type="ink")) == 6
tl = s.export_timelapse(out / "timelapse", every_n=2, backend="canonical")
assert tl.manifest["final"]["pixel_sha256"] == final.pixel_sha256
assert tl.manifest["frames"][0]["cursor"] == 0
assert tl.manifest["frames"][-1]["cursor"] == s.history_cursor
assert tl.manifest["gif"]["within_tolerance"]
print("MIXED_MEDIA_PUBLIC_EXAMPLE_PASS")
```

## Corrections and limitations

`apply_ink_actions(session, actions)` commits 1–256 explicit actions atomically and
returns action IDs. Use `preview_ink_actions(session, actions, new_png_path)` and its
four guards as above for prospective changes. The preview is not a mutation. After
commit inspect again; use the accepted action IDs and the original residual observation
with the existing residual/resolve methods. The compatibility field
`responsible_stroke_ids` may carry explicit ink element IDs in a mixed session.

Use `session.authored_elements(element_type="ink", part=..., role=...)` and
`current_ink_element(session, element_id)` to find the owner. `read_pen_definition`
recovers the recipe if the current path still has one; a raw replacement or transform
can invalidate it. To retire, submit ink.delete with element=None, never graphite
soft_lift/delete_stroke for ink. Graphite guides still use the ordinary pencil APIs.

`prepare_ink_transform(session, element_ids, matrix, action_ids=..., observation_id=...,
reason=...)` prepares actions and guards; preview and apply through the same route.
Matrix order is (a,b,c,d,tx,ty): (ax+by+tx, cx+dy+ty). Solid areas allow nonsingular
affine transforms; paths require similarities and scale the diameter uniformly.
Tone transforms move rings/holes only; pitch, phase, angle and gradient axis stay page
fixed. Reject nonuniform tone/path transforms. `prepare_ink_group_transform` adds
explicit group selection; mixed graphite/ink groups cannot be transformed atomically
by that helper. Re-author explicit replacement geometry when a transform is insufficient.

Existing profile work limits apply: factor = supersample times output_scale, at most
16,777,216 working pixels and factor at most 16. Choose a supported canvas/profile
before authoring; do not switch a persisted profile to hide a limit. Fast replay is eligible
for opaque-background ink-only history; graphite/eraser actions or transparency require
canonical. Use auto; PNG retains RGBA and GIF displays alpha over white. See
[render and replay](../output/render-profile-and-replay.md).
For differing subject and canvas sizes, explicitly choose whole-image
`Registration.fit(subject_size, canvas_size, mode="contain")` (or a justified
cover/stretch/explicit mapping); see [measurement and registration](../observation/measuring-boundaries.md).
Call `session.inspect(registration=registration)`. This changes evidence coordinates,
not authored geometry. Report unsupported requests instead of bypassing the runtime.
