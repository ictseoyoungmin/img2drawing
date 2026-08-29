# Autonomous worker packet — P2_primary_axes / pass 1

## Stage pass memory
- state: **cold_start**
- prior review count: 0
- previous decision: _none_
- carried concerns: _none_
- inter-pass correction actions: _none_

This is the first review pass for this stage. Start from the stage contract and references.

### Memory policy
- No prior stage review exists; begin from the stage contract and references.
- Runtime memory never invents artistic conclusions.
- Concern resolution must be stated by the Agent in a fresh review, not inferred by the runtime.

## Frozen stage representation contract
- contract: `full_body_croquis.P2.v3`
- representation: **skeletal_axes_and_measured_segments**
- tier: 2
- inherits from: `P1_gesture`

### This stage owns
- upper-arm and forearm axes with measured length
- thigh and shin axes with measured length
- foreshortening of each segment
- neck axis
- ribcage centre axis and its volume box
- pelvis axis and its volume box
- hand and foot placement blocks
- attached-object length and tilt relative to the body

### Must preserve from earlier stages
- P1 face, spine and pelvis centrelines
- P1 joint positions
- any P1 neck attachment cue as optional connection evidence only, not a measured axis
- P1 ground contact and whole-pose rhythm
- P1 limb-flow cues as pose and curvature evidence only, not measured axes or width

### Allowed representation
- limb segments as measured straight or lightly cylindrical axes
- ribcage and pelvis axis volumes
- the hip -> knee -> ankle -> foot chain stated as connected segments
- the shoulder -> elbow -> wrist -> hand chain stated as connected segments
- simple hand and foot placement blocks
- corrected joint positions when P1 flow proves a joint is misplaced
- attached-object length and tilt measured against the body
- retiring a superseded P1 placement cue with soft_lift or delete_stroke when a P2 axis or block takes over, while preserving P1 evidence and history

### Forbidden representation
- facial features
- hair
- clothing
- finished limb contour
- copying a P1 limb-flow path or optional cue spacing as measured thickness or mass
- surface or garment detail
- rendered shading

### Detail ceiling
- segment length and foreshortening
- the skeleton as a measurable mannequin
- prop length and tilt relative to the body
- no finished volume

### Next stage unlocks
- simple three-dimensional volumes wrapped around the P2 axes
- limb taper
- torso thickness and ribcage/pelvis rotation
- overlap and perspective cues

## Reference authority
- reference mode: **subject_only**
- comparison order: `subject_reference` (subject remains geometry and visible-edge truth)
- subject reference: `skills/img2drawing/examples/full_body_croquis/subject.png` — geometry truth
- task stage target: _not provided_

### Non-negotiable authority rule
- The stage contract decides representation scope; it does not decide pose correctness.
- The stage reference under `references/stages/` carries this stage's mark-making guidance, and some stages keep a rendered example beside it. Open one when you want it; never copy pose, coordinates, perspective or subject proportions from it.
- The subject reference remains geometry truth if references conflict about pose/proportion/perspective.

## Intent
Turn P1's flow into measured structure: segment lengths, foreshortening and the ribcage/pelvis volumes the mannequin needs. P1 said where the joints are; P2 says how long each bone is and how it is turned. P1 flow is curvature evidence, not a measured axis or width; P2's neck axis is measured independently from any optional P1 neck attachment cue.

## Observe
- the length of each limb segment against the subject
- foreshortening of each segment
- neck axis
- ribcage centre axis and how the ribcage box is turned
- pelvis axis and how the pelvis box is turned
- where the hands and feet sit as blocks
- any P1 joint that the measured chain proves was misplaced
- attached-object length and tilt relative to the body

## Draw
- limb segments as measured straight or lightly cylindrical axes
- ribcage and pelvis axis volumes
- the hip → knee → ankle → foot chain as connected segments
- the shoulder → elbow → wrist → hand chain as connected segments
- simple hand and foot placement blocks
- corrected joint positions where the measured chain disagrees with P1
- the attached object as a measuring axis against the body
- retiring a superseded P1 placement cue with soft_lift or delete_stroke when a P2 axis or block takes over, while preserving P1 evidence and history

## Avoid
- facial features
- hair
- clothing
- finished limb contour
- surface or garment detail
- copying a P1 flow path or optional cue spacing as measured thickness or mass

## Mandatory review questions
- Are the P1 centrelines — face, spine and pelvis — and the pose rhythm still readable underneath?
- Does each segment's length match the subject, or was it drawn to a comfortable proportion?
- Were the P2 axes measured independently from the subject rather than copied from P1 flow-line spacing?
- Does each segment read the subject's foreshortening? A limb coming toward the viewer is short.
- Are the ribcage and pelvis boxes turned the way the subject's are?
- Do the hand and foot blocks sit where the subject's hands and feet sit, including any in a pocket?
- If a joint moved from P1, was that because the subject says so — or to make the drawing easier?
- Is the attached object's length and tilt measured against the body rather than guessed?
- Did the worker stop before finished contour, clothing and hair?

## Advance only when
- Segment lengths and foreshortening agree with the subject.
- Ribcage and pelvis turn the way the subject's do.
- Hand and foot blocks are placed, including occluded ones.
- The P1 pose hypothesis survives; any joint correction is subject-driven.
- No major visible P2 mismatch remains after whole-view and relevant crop review.

## Suggested inspection intents
- neck+ribcage
- ribcage+pelvis boxes
- shoulder→elbow→wrist
- hip→knee→ankle
- hand blocks
- attached object against the torso

## Review artifacts
- schema: `img2drawing.reference_review_artifacts.v2`
- stage: `P2_primary_axes`
- subject_reference: `skills/img2drawing/examples/full_body_croquis/subject.png`
- subject_vs_drawing: `dev/evidence/fresh-worker/reviews/P2_primary_axes/pass_01/subject_vs_drawing.png`
- subject_split: `dev/evidence/fresh-worker/reviews/P2_primary_axes/pass_01/subject_split.png`
- subject_drawing_overlay: `dev/evidence/fresh-worker/reviews/P2_primary_axes/pass_01/subject_drawing_overlay.png`
- subject_drawing_absdiff: `dev/evidence/fresh-worker/reviews/P2_primary_axes/pass_01/subject_drawing_absdiff.png`
- overview: `dev/evidence/fresh-worker/reviews/P2_primary_axes/pass_01/reference_authority_overview.png`
- three_way: `dev/evidence/fresh-worker/reviews/P2_primary_axes/pass_01/reference_authority_overview.png`

## Canvas-scale pencil guidance
- canvas: `512 × 802`
- recommended width multiplier: **1.055×**
- minimum visible opacity for this stage: **0.6**
- minimum visible pressure for this stage: **0.48**
- Guidance only: do not silently rewrite explicit stroke intent.

## Checkpoint / resume
- checkpoint: `dev/evidence/fresh-worker/session/checkpoint.json`
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
