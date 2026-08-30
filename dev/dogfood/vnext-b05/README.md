# B05 early structural dogfood

This fixture exercises the new vNext start sequence on the existing sniper-girl
subject, rebuilt from `ideal-stroke-reference.png`:

`PoseObservation → line of action → head/ribcage/pelvis masses → depth-aware limbs/feet/prop`

Run from the repository root:

```bash
PYTHONPATH=skills/img2drawing/src python3 dev/dogfood/vnext-b05/run.py
```

The script refuses to overwrite an existing run. Inspect these outputs directly:

- `ideal-stroke-reference.png` — Imagen visual reference for the intended sparse
  back/side construction;
- `run-from-ideal-stroke/inspections/000001/raw_drawing.png` — the rebuilt initial whole-figure drawing;
- `run-from-ideal-stroke/inspections/000001/inspection_sheet.png` — subject, drawing, contrast overlay,
  and three focused crops;
- `run-from-ideal-stroke/session.checkpoint.json` — the normal B04 checkpoint, included only as the
  session's persistence boundary.

This is intentionally an unfinished initial construct. B05 is concerned with whether
the macro pose already reads before contour/detail work; corrections and correction
memory belong to B06.
