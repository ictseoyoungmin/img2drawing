# B05 early structural dogfood

This fixture exercises the new vNext start sequence with a fresh worker receiving
only the subject reference and drawing mode. The construction geometry is authored
in `run.py`; it does not load a same-subject answer image.

`PoseObservation → line of action → head/ribcage/pelvis masses → depth-aware limbs/feet/prop`

Run from the repository root:

```bash
PYTHONPATH=skills/img2drawing/src python3 dev/dogfood/vnext-b05/run.py
```

The script refuses to overwrite an existing run. Inspect these outputs directly:

- `ideal-stroke-reference.png` — capability exemplar only; it is not an input to the
  canonical subject-only run;
- `run-subject-only/inspections/000001/raw_drawing.png` — the initial whole-figure drawing;
- `run-subject-only/inspections/000001/inspection_sheet.png` — subject, drawing, contrast overlay,
  and three focused crops;
- `run-subject-only/session.checkpoint.json` — the normal B04 checkpoint, included only as the
  session's persistence boundary.

Committed representative review evidence is kept separately under
`dev/evidence/vnext/b05/`: `initial_construct.png`, `inspection_sheet.png`, and `REVIEW.md`.

This is intentionally an unfinished initial construct. B05 is concerned with whether
the macro pose already reads before contour/detail work; corrections and correction
memory belong to B06.
