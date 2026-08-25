# S1S9 dogfood — R22 img2drawing

Reference: [`subject.png`](subject.png)

Run output: [`croquis_run/`](croquis_run/)

## What the revised protocol exercised

- immutable pre-draw observation lock: `back_three_quarter`, `image_right` near side, fully visible near arm, rifle-over-torso overlap;
- autonomous P1→P5 stage progression with real revise/re-review passes on P1, P2, P3, and P4;
- P3 eight-region blind visual-fidelity closure plus independent envelope/orientation/lower-body/head-hair/prop evidence;
- P5 residual mismatch recovery through `reopen_01`, archived review evidence, and a fresh clean-block-in review;
- final drawing, checkpoint/session, comparison board, and full timelapse GIF.
- mechanical audit: `FRESH_WORKER_MECHANICAL_AUDIT_PASS` (4 REVISE passes, 74 direct strokes, 10 correction/retirement actions, 1 P5 reopen);
- regenerated with the canonical `finish()` default: `mode=every_n`, `every_n=4`, 89 logged actions → 24 GIF frames, final-frame/session hash match true;

## Visual result

The process improvements are real and observable: the P3 near-arm blocker was
recorded and corrected, the final near sleeve has an explicit inner contour, and
P5 reopen added stronger bob-hair handoff and rifle scope/stock topology breaks.

The final drawing is still not a high-fidelity likeness. Fresh whole-view inspection
finds remaining semantic gaps: the torso is too tubular/central for the subject's
back-three-quarter jacket, the face direction remains generic without a convincing
head/neck turn, and the rifle still reads more simply than the photographed prop.
The P3 numeric evidence is therefore useful provenance and width evidence, not proof
that the rendered drawing is artistically correct.

Conclusion: S01–S09 materially improve lifecycle integrity, region accountability,
and recovery behavior, but this dogfood does not yet demonstrate professional-level
subject likeness. The next improvement target is an earlier P2/P3 whole-view semantic
residual gate for torso turn, head identity, and prop topology.

Key artifacts:

- Final: [`croquis_run/final/drawing.png`](croquis_run/final/drawing.png)
- Subject comparison: [`croquis_run/compare/subject_vs_final.png`](croquis_run/compare/subject_vs_final.png)
- Timelapse: [`croquis_run/timelapse/timelapse.gif`](croquis_run/timelapse/timelapse.gif)
- P3 measurements: [`croquis_run/reviews/P3_primary_masses/pass_02/fidelity_evidence/region_measurements.json`](croquis_run/reviews/P3_primary_masses/pass_02/fidelity_evidence/region_measurements.json)
- Reopen record: [`croquis_run/reopens/reopen_01.json`](croquis_run/reopens/reopen_01.json)
