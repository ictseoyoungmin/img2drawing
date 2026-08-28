# P1 reference run

The canonical example carried through the skill's own closeout, so this folder holds a
complete run record rather than only review artifacts.

Rebuild with:

```bash
python3 dev/p1_reference_run/build.py
```

## What is here

| path | what it is |
|---|---|
| `run/reviews/P1_gesture/pass_01`, `pass_02` | worker packets, pass memory, stage contract, review records, comparison boards, Agent-selected local reviews |
| `run/session/session.json` | the authoritative action history |
| `run/session/checkpoint.json` | resumable state — `DrawingRun.resume(run/)` |
| `run/observation/pre_draw_observation.json` | the immutable pre-draw observation lock |
| `run/final/drawing.png` | the closeout render |
| `run/compare/subject_vs_final.png` | subject beside the final render |
| `run/timelapse/timelapse.gif` | 47-frame action timelapse (`timelapse_mode="action"`) |
| `run/timelapse/manifest.json` | frame-to-action provenance |
| `canonical_trace.json` | the example's own trace, validating against `dev/schemas/canonical_example_trace.schema.json` |
| `compare.png`, `overlay.png` | raw-render comparison and the translucent-paper overlay |

`run/timelapse/frames/` is deleted after the GIF is built; it regenerates from the
checkpoint.

## What the run demonstrates

`P1 draw → subject/target/drawing review → Agent-selected local reviews → REVISE → explicit
pelvis/hip/leg replacement → fresh review → pass-memory continuation → ADVANCE`, then
`finish()`.

`ideal_overlay_preview.png` is copied into the canonical example as `p1_target.png` and
registered as the P1 task-stage target. Pass 1 deliberately leaves the pelvis line through
the provisional hip row, with medial hip centres and a low support knee. Pass 2 raises the
pelvic crest, moves both femoral heads laterally, raises the support knee and redraws both
leg paths through the corrected joints. It then clears all carried concerns against fresh
three-way evidence before advancing.

The observation lock is semantic rather than placeholder data, and every local subject
box is derived from the same normalized transform as its drawing box. Local overlays can
no longer improve apparent registration by shifting or stretching a hand-picked crop.

## Reading the result

Judge tone on **`run/reviews/P1_gesture/pass_02/current_drawing.png`** and
`run/final/drawing.png` — the raw renders, never a contrast-boosted view.

Judge registration on **`overlay.png`**, which lays the drawing over the subject like
translucent paper. That is what shows whether the crown, the joint centres and the foot
landings actually sit on the subject; a drawing that looks plausible on its own will not
survive it. The overlay preserves raw graphite density; it applies no contrast gain.

## Stroke weights

Calibrated against a completed dogfood run, not guessed:

| element | grade | pressure | width | opacity |
|---|---|---|---|---|
| dashed spine centreline | HB | 0.40 | 1.9 | 0.54 |
| facial centreline | B | 0.62 | 2.65 | 0.80 |
| limb centre-path curves | HB | 0.56–0.58 | 2.45–2.5 | 0.70–0.72 |
| construction (head, shoulder, pelvis, joints, feet) | HB | 0.44–0.54 | 2.0–2.35 | 0.55–0.68 |
| ground contact | 2H | 0.36 | 1.7 | 0.42 |

An early stage is not a faint stage, and the pencil grade decides more than the numbers:
a 2H stroke stays pale whatever the pressure.
