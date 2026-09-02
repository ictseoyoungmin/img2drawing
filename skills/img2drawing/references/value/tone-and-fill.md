# Tone, value and fill

Creating value means declaring a region, not accumulating many strokes.

## Form before value

Value is **a means of reinforcing form that is already established**. Do not hide
incorrect silhouette, contour, or overlap with dark hatching or reserved light.

Before adding a fill, reread the current drawing as though it were in a line-only,
tone-off state. The following must still read:

- the actual thickness and near/far relationships of arms and legs;
- the separation and connection of torso and limbs;
- the volume of large garment masses such as jackets, skirts, and boots; and
- hand/prop contact and major overlaps.

If any of these reads only when value is present, the current bottleneck is form,
not value. First correct the contour or overlap premise with `replace_stroke()`,
`replace_segment()`, `soft_lift()`, or a related explicit action, then inspect
again. Add tone only afterward.

`ReservedLight` follows the same principle. It preserves rim light, fold light, or
reflected light actually observed in the subject inside forms that are already
separated correctly. It does not create a nonexistent arm–torso boundary or
volume.

## Create value with region fills

Create broad value areas—black clothing, stockings, boots, or hair shadow—with
one `DrawingSession.fill_region()` call. Do not build them by manually repeating
individual value lines.

```python
fill_id = session.fill_region(
    jacket_polygon,
    value=120,                    # mean value read from subject (0 black - 255 paper)
    part="jacket_tone",
    angle=74.0,
    observation_id="observation-0001",
    reason="black tactical jacket, lit from image-right",
)
```

## If the value is wrong, revise the region itself

When a fresh inspection disproves the previous value premise, do not stack another
fill over the same area. Use `session.replace_fill_region()` to append a new definition
while preserving the existing fill identity.

```python
correction_action_id = session.replace_fill_region(
    fill_id,
    value=90,
    reason="fresh inspection shows the jacket is darker than the first estimate",
    observation_id="observation-0001",
)
```

`session.replace_fill_region()` returns a new `action_id`. The historical root function
`replace_fill_region(session, ...)` delegates to this method for compatibility and is not
a second implementation. When recording the residual
correction, pass that value directly to
`record_correction(..., action_ids=[correction_action_id])`. Do not enumerate
hundreds of generated hatch strokes as correction actions.

## Preserve light; do not erase it back out

Do not fill and then erase light areas actually observed inside a dark mass, such
as clothing highlights, rim light on an arm or garment already separated by
contour and overlap, or a boot's lace panel. Make the fill leave them open from
the start.

```python
session.fill_region(
    sock_polygon, value=65, part="sock_tone", angle=82.0,
    reserved=[{"path": [(338, 950), (330, 1120), (336, 1232)],
               "width": 6.0, "strength": 1.0, "note": "rim light down the shin"}],
    observation_id="observation-0001",
    reason="black over-knee sock with a rim light on the leading edge",
)
```

`strength=1.0` preserves the reserved light completely; lower values allow some
tone to pass through.

## Value hierarchy

Three or four value families are sufficient in one drawing. Use `fill_region`
once for each family; do not build value by repeatedly layering the same area.
Control a region's tonal density with `value` alone. Use `session.replace_fill_region()`
when revising the judgment behind an existing region.

## Do not

- Substitute hatching for thickness or separation when form does not read in a
  line-only state.
- Generate individual value lines in a `for` loop and pass them to `draw_many()`;
  use `fill_region()`.
- Sample straight value lines at fixed intervals and store each as 10–20 points.
- Stack fills repeatedly over the same area because the value did not appear;
  revise the existing region.
- Tune value by combining opacity, pressure, and grade manually; express it with
  `value`.
