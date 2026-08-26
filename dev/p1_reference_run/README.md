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
| `run/timelapse/timelapse.gif` | 35-frame action timelapse (`timelapse_mode="action"`) |
| `run/timelapse/manifest.json` | frame-to-action provenance |
| `canonical_trace.json` | the example's own trace, validating against `dev/schemas/canonical_example_trace.schema.json` |
| `compare.png`, `overlay.png` | raw-render comparison and the translucent-paper overlay |
| `smoothing.png` | the faceted polylines beside the Catmull-Rom resampled strokes |

`run/timelapse/frames/` is deleted after the GIF is built; it regenerates from the
checkpoint.

## What the run demonstrates

`P1 draw → prepare review → Agent-selected local reviews → REVISE → explicit
replace_stroke → fresh review → pass-memory continuation → ADVANCE`, then `finish()`.

Pass 1 stands a borrowed narrow ellipse in for the cranium — the form the P1.v3 contract
forbids as "a generic ellipse standing in for an observed head or foot". It is about a
third too narrow and sits left of the subject's head, so its edge cuts through her eye and
its lower end stops at the mouth. Review catches it against the subject, the correction
**replaces** the structure rather than nudging it, and pass 2 clears the carried concerns
and runs a residual sweep before advancing.

`head-revise.png` shows both passes laid over the subject.

## Reading the result

Judge tone on **`run/reviews/P1_gesture/pass_02/current_drawing.png`** and
`run/final/drawing.png` — the raw renders, never a contrast-boosted view.

Judge registration on **`overlay.png`**, which lays the drawing over the subject like
translucent paper. That is what shows whether the crown, the joint centres and the foot
landings actually sit on the subject; a drawing that looks plausible on its own will not
survive it.

## Stroke weights

Calibrated against a completed dogfood run, not guessed:

| element | grade | pressure | width | opacity |
|---|---|---|---|---|
| spine centreline (dominant gesture) | B | 0.72 | 3.1 | 0.90 |
| facial centreline | B | 0.66 | 2.8 | 0.84 |
| construction (head, shoulder, pelvis, limbs, feet) | HB | 0.44–0.52 | 2.0–2.3 | 0.55–0.66 |
| ground contact | 2H | 0.36 | 1.7 | 0.42 |

An early stage is not a faint stage, and the pencil grade decides more than the numbers:
a 2H stroke stays pale whatever the pressure.
