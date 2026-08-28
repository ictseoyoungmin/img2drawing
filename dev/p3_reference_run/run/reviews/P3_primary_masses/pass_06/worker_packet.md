# Autonomous worker packet — P3_primary_masses / pass 6

## Stage pass memory
- state: **revision_continuation**
- prior review count: 5
- parent review digest: `efe7d26811091d41a46575b2b631e94e624e05d17d3daadf8e33416ef4d6d134`
- previous decision: **revise**

### Previous remaining concerns
- one final blind residual sweep is required before P3 closure

### Previous reported corrections
- Rechecked shoulder counter-tilt and the lower torso bridge without adding garment seams.

### Inter-pass actions since the previous review
- `P3R-P6-HEAD-L` replace_stroke / head_mass_left — Final blind sweep keeps the head mass close to the locked crown/chin while preserving turn.
- `P3R-P6-LEG-A-KNEE` replace_stroke / leg_A_knee_cross — Final blind sweep aligns the support knee cross-contour to the measured outer and inner edges.
- `P3R-P6-LEG-B-KNEE` replace_stroke / leg_B_knee_cross — Final blind sweep aligns the counterbalance knee cross-contour to its measured station.

### Carried concerns for this pass
- one final blind residual sweep is required before P3 closure

### Memory policy
- Start the next pass by re-checking carried_concerns against fresh artifacts.
- inter_pass_actions are mechanical action provenance, not proof that a concern was solved.
- Do not infer resolved concerns by set subtraction or scores; the Agent must make a fresh visual judgement.
- Use correction history to avoid repeating an ineffective edit without changing observation strategy.

## Frozen stage representation contract
- contract: `full_body_croquis.P3.v2`
- representation: **three_dimensional_masses**
- tier: 3
- inherits from: `P2_primary_axes`

### This stage owns
- head volume
- ribcage volume
- pelvis volume
- shoulder volume
- upper-arm and forearm volumes
- thigh and calf volumes
- simple hand and foot volumes
- ribcage and pelvis rotation
- front/back relationships and overlap
- whole-figure proportion
- attached-object volume

### Must preserve from earlier stages
- P1 balance and whole-body pose rhythm
- P1 face, spine and pelvis centrelines
- P2 segment lengths and foreshortening

### Allowed representation
- simple three-dimensional volumes wrapped around the P2 axes
- cross-contours that state the direction a volume points
- limb taper
- torso thickness and ribcage/pelvis rotation
- overlap and perspective cues
- a few garment or gear marks where they change the occupied volume

### Forbidden representation
- facial features
- individual hair strands
- clothing folds and seams
- finished garment silhouette
- hand and foot detail
- rendered shading

### Detail ceiling
- what volume the body occupies
- limb thickness and taper
- rotation, overlap and perspective
- no real-form surface yet

### Next stage unlocks
- hair as a large mass over the cranium, not strand by strand
- how a garment hangs on the underlying volume
- major prop structure: barrel direction, stock, receiver, magazine, sling
- resolved hand, foot and footwear form

## Reference authority
- reference mode: **subject_only**
- comparison order: `subject_reference` (subject remains geometry and visible-edge truth)
- subject reference: `../../../../../../skills/img2drawing/examples/full_body_croquis/subject.png` — geometry truth
- task stage target: _not provided_

### Non-negotiable authority rule
- The stage contract decides representation scope; it does not decide pose correctness.
- The stage reference under `references/stages/` carries this stage's mark-making guidance, and some stages keep a rendered example beside it. Open one when you want it; never copy pose, coordinates, perspective or subject proportions from it.
- The subject reference remains geometry truth if references conflict about pose/proportion/perspective.

## Intent
Turn the stick figure into a body with volume: wrap simple three-dimensional masses around the P2 axes.

## Observe
- how thick the torso is
- ribcage and pelvis rotation
- limb thickness and taper
- which parts are in front of which
- overlap
- perspective
- whole-figure proportion
- the volume a large attached object occupies

## Draw
- simple three-dimensional volumes around head, ribcage, pelvis, shoulders, upper arms, forearms, thighs, calves, hands and feet
- cross-contours that state which way a volume points
- limb taper
- torso thickness and ribcage/pelvis rotation
- overlap and perspective cues
- a few garment or gear marks where they materially change the occupied volume

## Avoid
- facial features
- individual hair strands
- clothing folds and seams
- finished garment silhouette
- hand and foot detail

## Mandatory review questions
- Does each limb read as a volume pointing somewhere, not two parallel outlines?
- Do the ribcage and pelvis show their rotation?
- Is the torso thickness credible against the subject?
- Are front/back and overlap relationships explicit?
- Does whole-figure proportion hold up at mass level?
- Are the P2 joint positions and directions preserved underneath?
- Did the worker keep garment detail and face out, adding only marks that change the occupied volume?

## Advance only when
- The figure reads as a body with volume rather than a stick figure.
- Ribcage and pelvis rotation match the subject.
- Limb thickness, taper and overlap match the subject.
- Whole-figure proportion holds at mass level.
- No major visible P3 mismatch remains after whole-view and relevant crop review.

## Suggested inspection intents
- head+ribcage
- ribcage+pelvis
- one full arm
- one full leg
- attached object volume

## Review artifacts
- schema: `img2drawing.reference_review_artifacts.v2`
- stage: `P3_primary_masses`
- subject_reference: `../../../../../../skills/img2drawing/examples/full_body_croquis/subject.png`
- subject_vs_drawing: `../../../../../../dev/p3_reference_run/run/reviews/P3_primary_masses/pass_06/subject_vs_drawing.png`
- subject_split: `../../../../../../dev/p3_reference_run/run/reviews/P3_primary_masses/pass_06/subject_split.png`
- subject_drawing_overlay: `../../../../../../dev/p3_reference_run/run/reviews/P3_primary_masses/pass_06/subject_drawing_overlay.png`
- subject_drawing_absdiff: `../../../../../../dev/p3_reference_run/run/reviews/P3_primary_masses/pass_06/subject_drawing_absdiff.png`
- overview: `../../../../../../dev/p3_reference_run/run/reviews/P3_primary_masses/pass_06/reference_authority_overview.png`
- three_way: `../../../../../../dev/p3_reference_run/run/reviews/P3_primary_masses/pass_06/reference_authority_overview.png`

## Canvas-scale pencil guidance
- canvas: `512 × 802`
- recommended width multiplier: **1.055×**
- minimum visible opacity for this stage: **0.66**
- minimum visible pressure for this stage: **0.54**
- Guidance only: do not silently rewrite explicit stroke intent.

## Checkpoint / resume
- checkpoint: `../../../../../../dev/p3_reference_run/run/session/checkpoint.json`
- `submit_stage_review()` writes a resumable checkpoint automatically.
- Resume with `DrawingRun.resume(output_dir)` after process loss; prepare a fresh review before judging new edits.

## Local Review API
Use this when the whole-view comparison leaves a concrete question unresolved.

```python
local = run.prepare_local_review(
    label="head_face",
    intent="Check face-direction curve and head envelope",
    subject_box=(left, top, right, bottom),
    drawing_box=(left, top, right, bottom),
)
```

- ROI selection authority: **Agent explicit boxes**.
- Automatic anatomy/landmark detection: **not used**.
- Runtime validates/crops/binds only.
- Each local review also writes a crop-registered subject/drawing overlay and raw absolute-difference view. These are evidence, never a score.

## Autonomous loop
1. Read pass memory first. If state is reopen_restart, treat archived target/downstream reviews as invalidated evidence and rebuild from the restored branch.
2. If carried concerns exist, re-check them before inventing new work.
3. Read the frozen stage contract before deciding what belongs in this stage.
4. Observe the subject at whole-body scale first; choose a local ROI only to answer a concrete uncertainty.
5. SUBJECT-ONLY MODE: no same-subject stage target exists. Construct the current stage from the subject geometry, frozen StageContract, and verified prior drawing state.
6. Before drawing, reject vocabulary listed in forbidden_representation.
7. Draw a bounded set of explicit strokes that serve the current stage ownership.
8. Render the exact current artifact with prepare_stage_review().
9. If a whole-view question remains unresolved, choose explicit ROI boxes and call prepare_local_review().
10. Compare fresh evidence against carried concerns and the inter-pass correction actions recorded in pass memory.
11. Write contract_findings separately from reference/artifact findings and cite useful local_review_ids.
12. If any important drawing mismatch remains, choose the highest-impact 1–3 issues and revise locally.
13. After every drawing mutation, prepare fresh stage/local reviews; never reuse stale judgement.
14. After carried concerns appear cleared, perform one fresh residual-mismatch sweep that is NOT limited to the prior concern list; inspect the whole view and a high-risk ROI before setting remaining_concerns=[] .
15. Advance only when both the carried-concern recheck and the fresh residual sweep find no important mismatch at the current stage purpose.
16. If a later stage exposes an earlier foundational error, reopen the earliest responsible stage.

## Autonomy policy
- Do not stop after a pass merely to ask the user whether to continue.
- Do not ask the user to approve routine stage transitions; the worker owns the self-review loop.
- Use pass memory to continue unresolved work rather than resetting the stage mentally each pass.
- Do not treat inter-pass action provenance as proof that a concern was solved.
- Do not let the prior concern list become the review boundary; new defects found in the residual sweep can keep the stage at REVISE.
- Never use CV/evidence maps or crop automation as semantic authority.

## Escalation policy
- Ask the user only when the source reference is missing/unreadable, the requested goal is internally contradictory, or a choice genuinely changes the intended artistic target.
- Repeated visual failure is not itself a reason to ask the user; change observation strategy, crop, stroke plan, or reopen the responsible stage first.

## Bound modular grammar cards
- _none bound for this condition_
