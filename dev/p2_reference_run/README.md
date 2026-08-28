# P2 reference run

The canonical example carried through the skill's own closeout, so this folder holds a
complete run record rather than only review artifacts.

Rebuild with:

```bash
python3 dev/p2_reference_run/build.py
```

## What is here

| path | what it is |
|---|---|
| `run.py` | the P1→P2 runner; it reads the shared subject asset but keeps P2 execution outside the public skill example |
| `build.py` | rebuilds the run record, comparisons and timelapse |
| `run/reviews/P1_gesture/pass_01`, `pass_02` | P1 worker packets, pass memory, stage contract, review records, comparison boards and Agent-selected local reviews |
| `run/reviews/P2_primary_axes/pass_01`, `pass_02` | P2 measured-axis worker packets, pass memory, open ribcage/pelvis boxes, endpoint blocks and registered local reviews |
| `run/session/session.json` | the authoritative action history |
| `run/session/checkpoint.json` | resumable state — `DrawingRun.resume(run/)` |
| `run/observation/pre_draw_observation.json` | the immutable pre-draw observation lock |
| `run/final/drawing.png` | the closeout render |
| `run/compare/subject_vs_final.png` | subject beside the final render |
| `run/timelapse/timelapse.gif` | 73-frame action timelapse (`timelapse_mode="action"`) |
| `run/timelapse/manifest.json` | frame-to-action provenance |
| `canonical_trace.json` | the P1→P2 trace, validating against `dev/schemas/p2_reference_trace.schema.json` |
| `compare.png`, `overlay.png` | raw-render comparison and the translucent-paper overlay |

`run/timelapse/frames/` is deleted after the GIF is built; it regenerates from the
checkpoint.

## What the run demonstrates

`P1 draw → subject/target/drawing review → Agent-selected local reviews → REVISE → explicit
pelvis/hip/leg replacement → fresh review → pass-memory continuation → ADVANCE`, followed by
`P2 measured axes → registered local review → REVISE → axis replacement → fresh review →
ADVANCE`, then `finish()`.

`ideal_overlay_preview.png` is used as the P1 task-stage target. Pass 1 deliberately leaves the pelvis line through
the provisional hip row, with medial hip centres and a low support knee. Pass 2 raises the
pelvic crest, moves both femoral heads laterally, raises the support knee and redraws both
leg paths through the corrected joints. It then clears all carried concerns against fresh
three-way evidence before advancing. P2 independently measures the neck, ribcage and pelvis
turn, both limb chains, and simple hand and foot placement blocks; it stops at
`P3_primary_masses` ready for the next stage.

The P2 review also catches the common handoff error at the shoes: once the P2 placement
blocks are drawn, the superseded P1 ankle links and direction wedges are deleted from the
active canvas with `delete_stroke`. They were valid P1 gesture evidence, but P2 now owns
the visible placement. Their history and P1 artifact remain replayable; the P1
ground-contact marks remain.

The observation lock is semantic rather than placeholder data, and every local subject
box is derived from the same normalized transform as its drawing box. Local overlays can
no longer improve apparent registration by shifting or stretching a hand-picked crop.

## Reading the result

Judge tone on **`run/reviews/P2_primary_axes/pass_02/current_drawing.png`** and
`run/final/drawing.png` — the raw renders, never a contrast-boosted view.

Judge the P2 change directly by comparing **`P2 pass 1`** and **`P2 pass 2`** in
`compare.png`; the latter is the raw post-deletion drawing. Judge registration on
**`overlay.png`**, which lays the drawing over the subject like
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

P2 axes use a subordinate HB/H construction range; the boxes and endpoint blocks remain
lighter than the P1 gesture so measured structure does not replace the pose hypothesis.

An early stage is not a faint stage, and the pencil grade decides more than the numbers:
a 2H stroke stays pale whatever the pressure.
