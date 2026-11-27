# Optional layers, shared edits, and exchange

Open this leaf when the task needs layer organization, mixed-material group changes,
or editable raster delivery. Ordinary line art and hand-drawn work can keep using
`DrawingSession.draw()` without enabling layers. Choose the editing structure the task
needs; a professional workflow is not a prerequisite for drawing.

## Enable and organize

Layers use the existing session, history and checkpoint. Resume never enables them
automatically. Convert explicitly:

```python
session.enable_layers(layer_id="drawing", name="Imported Drawing")
session.create_layer("character", "Character", kind="group")
session.create_layer("ink", "Ink", parent_id="character")
session.create_layer("tone", "Tone", parent_id="character")
session.assign_elements(["outline", "detail"], "ink")
session.set_active_layer("tone")
```

Conversion puts every current mark, including erasers, in one paint layer in the existing
draw order. Neutral conversion preserves the image exactly. Later splitting or rearranging
content is an explicit compositing edit and can change integer alpha rounding. The native
mark's numeric `layer`, ID, geometry and material are retained. Use document operations
for stacking; do not rewrite numeric `layer` values to reorganize an existing drawing.

Read `session.layer_document` for the immutable current tree and membership. It is `None`
until enabled. Paint layers own ordered element IDs; groups own child layers. Sibling
indices are bottom-to-top. IDs are stable and cannot be reused after deletion in retained
history. Visible names may contain spaces and are separate from IDs.

```python
session.update_layer("ink", name="Final ink", visible=True, opacity=0.8)
session.update_layer("drawing", locked=True)
session.move_layer("tone", parent_id="character", index=0)
session.assign_elements(["detail"], "ink", index=0)
```

Lock inherits through groups and prevents content changes, membership moves and structural
edits. Name, visibility and opacity remain explicit display controls. A child cannot unlock
through a locked parent. Hidden layers retain their marks and are editable unless locked.
Opacity applies once to the completed layer/group, including overlapping children.
Normal is the supported blend mode; other modes are rejected. Groups are isolated.

New marks use the active paint layer. To choose a destination per call, pass `layer_id=`
to `draw`, items in `draw_many`, `erase_path`, or `apply_ink_actions`. Ink preview accepts
the same route; its action digest binds that choice. Replacements preserve membership.
Split fragments inherit their source layer. Erasers lift earlier graphite in their own
paint layer and do not remove ink or marks in other layers. White ink remains paint.

`delete_layer(id)` only accepts empty inactive nodes. Move/delete content and select another
active layer explicitly first. These operations are recorded, not flattened into pixels.
For an advanced atomic document batch, use typed `LayerAction` values with
`session.apply_layer_actions(..., expected_cursor=..., expected_state_hash=...)`.

## Transform one mixed selection

`img2drawing.authoring` provides the shared path for graphite, ink paths, solid areas and
tones. It also works in an unlayered session. Existing stroke-only and ink-only helper
defaults remain unchanged.

```python
from img2drawing.authoring import (
    prepare_element_transform, preview_element_edits, apply_element_edits,
)

edit = prepare_element_transform(
    session, ["pencil-guide", "outline", "tone-fill"],
    (1, 0, 0, 1, 8, 3),
    action_ids=["move-guide", "move-outline", "move-tone"],
    observation_id=observation_id,
    reason="move the selected shape together",
    width_policy="preserve", tone_policy="page",
)
preview = preview_element_edits(session, edit, "move-preview.png")
# Read the preview and accept the intended change before applying it.
apply_element_edits(session, edit)
```

The matrix is `(a, b, c, d, tx, ty)`: `x' = a*x + b*y + tx`,
`y' = c*x + d*y + ty`. For example, `(0, -1, 1, 0, tx, ty)` rotates
90 degrees in canvas coordinates, then translates. Choose explicit fresh action IDs and a recorded observation.
`prepare_element_group_transform(session, plan_id, group_id, matrix, ...)` resolves an
existing `SemanticGroup` and uses the same policies. Missing members and unassigned split
fragments must be resolved explicitly first.

| Policy | Result |
| --- | --- |
| `width_policy="preserve"` (default) | Keep graphite and ink widths; preserve pressure and relative contact width. |
| `width_policy="scale"` | Scale graphite and ink widths uniformly with the geometry. |
| `tone_policy="page"` (default) | Move boundaries/holes while the page-space tone pattern stays fixed. |
| `tone_policy="object"` | Move/rotate/reflect the pattern and gradient with the object; scale pitch. |

Paths and object-following tone require a nonsingular similarity transform: translation,
rotation, reflection or uniform scaling. Area/page-tone-only selections can use nonsingular
affine transforms. Authored path erasers are not supported in shared transforms; re-author
an explicit eraser instead. No automatic geometry selection or deformation is inferred.

The proposal binds cursor, drawing state, render profile and action contents. Any change
after preparation makes it stale. Preview leaves the session/checkpoint untouched. Apply
is atomic: one invalid or locked member rejects the entire batch. To prepare other explicit
mixed replacements/deletions, use `prepare_element_edits(session, typed_actions)`.

## Undo, redo, and retained evidence

`session.undo(steps=1)` and `session.redo(steps=1)` move through action cursors and save
the checkpoint atomically. Pass `steps=len(edit.actions)` to undo/redo a complete mixed
proposal at once. These methods do not undo observations, inspections or intent records.
Optional cursor/state-hash guards reject stale navigation.

New edits after undo discard the redo tail only when that would not orphan retained audit
evidence. If an inspection, correction, finish or intent record references the future tail,
the new edit is rejected. Redo to that evidence, then author an explicit correction. The
runtime does not silently erase evidence to make branching succeed. If undo moves before
the current intent was selected, redo or explicitly call `set_intent` at the current cursor
before making a new inspection under that intent.

## Choose a supported working size

The current document contract permits 256 paint/group nodes and 32 hierarchy levels.
Its working raster is `width * height * (output_scale * supersample) ** 2`, limited to
16,777,216 pixels with a combined scale factor at most 16. A 1024×1536 page at scale 1
and supersample 2 uses 6,291,456 working pixels. Simultaneously live surfaces are bounded
at 100,663,296 pixels, and material/composition work at 268,435,456 cumulative working-pixel
operations per render. These guards have no public override argument. Choose dimensions
and supersampling when creating the session; retain its profile throughout replay.

Layer mutations preflight membership and surface dimensions. Actual material/composition
work is checked while rendering, and a work-limit error reports the consumed work and cap.
Sparse layers composite their occupied alpha regions while retaining full native membership
and exact source-over pixels. Timelapse has additional whole-export limits described in
[render profile and replay](../output/render-profile-and-replay.md).

## Deliver editable layers and the native session

```python
pngs = session.export_layer_pngs("delivery-layers")
ora = session.export_openraster("delivery.ora")
print(ora.canonical_pixel_sha256, ora.recomposition_exact,
      ora.differing_pixels, ora.max_channel_error)
```

Both operations require an enabled layer document and new destinations. They include:

- Raw transparent paint-layer PNGs, retaining hidden content; opacity is recorded once.
- Layer names, order, visibility, opacity and isolated hierarchy.
- An exact canonical `mergedimage.png`, thumbnail and fidelity manifest.
- A native checkpoint and its retained inspection evidence by default, in the PNG bundle or
  beside the ORA (`delivery.checkpoint.json` and `delivery.native/`). The manifest records
  the checkpoint digest. A reference-bound checkpoint still needs the original reference
  to resume; evidence is copied so native editing does not depend on the old output folder.

The ORA can be opened by a compatible application such as Krita. Final-size layer PNGs are
downsampled separately, so recompositing them may differ from the canonical merged image.
The manifest measures that difference using this runtime's compositor; another editor's
rounding or color handling can differ further. Do not claim identical external flattening
unless it has been checked in that application.

For ongoing raster work in Krita, save a native `.kra` project and retain the original ORA
delivery and img2drawing checkpoint. In the measured Krita 5.2.9 document-engine checks,
fractional input opacity was quantized to the editor's 8-bit opacity. Layer edits then
survived KRA save/reopen with identical properties and pixels. Krita's own ORA save/reopen
reduced some opacities by another level: 127→126 in a synthetic group and 150→149,
178→177, 224→223 in a real page. Other tested structure and raw layer pixels were retained.
These are version-specific observations, not a universal error bound. Keep native working
projects when repeated exchange saves would make such rounding significant.

Raster exchange preserves editable raster layers. Points, pressure, tools, procedural tone
parameters and action replay remain in the native checkpoint. External raster modifications
are not imported back as original strokes. Keep the original session when continued native
editing matters. `include_native=False` is an explicit choice for raster-only handoff.

Resume the native checkpoint using its saved evidence location:

```python
from img2drawing import DrawingSession

checkpoint = ora.manifest_path.parent / ora.manifest["native_checkpoint"]["file"]
restored = DrawingSession.resume(checkpoint, subject=session.subject)
```

`resume(output_dir=...)` selects an existing evidence root; it does not relocate or copy
inspection files into an empty folder. The exported checkpoint already points to its copied
evidence. To relocate a delivery, keep the checkpoint and its evidence folder together.

Layer histories currently use canonical timelapse rendering. PSD, raster import, masks,
pass-through groups and a visual layer editor are outside this version's initial scope.
Use `runtime_capabilities(session.render_profile, layered=True)` for public discovery.
