# Autonomous worker packet — P1_gesture / pass 2

## Stage pass memory
- state: **revision_continuation**
- prior review count: 1
- parent review digest: `f5009e65791c772eaf24415e593ef2bd774b9405dfa014864c58551be93b8287`
- previous decision: **revise**

### Previous remaining concerns
- cranium outline is a borrowed ellipse, not this head's measured width
- eye line and facial centreline therefore sit inside the face instead of across the head

### Previous reported corrections
- _none_

### Inter-pass actions since the previous review
- `EX-P1-R1` replace_stroke / head_outline — Pass 1 stood a borrowed narrow ellipse in for the cranium, which the P1 contract forbids. Replaced with the head outline measured on the subject: wider, centred right of where the ellipse sat, and asymmetric.

### Carried concerns for this pass
- cranium outline is a borrowed ellipse, not this head's measured width
- eye line and facial centreline therefore sit inside the face instead of across the head

### Memory policy
- Start the next pass by re-checking carried_concerns against fresh artifacts.
- inter_pass_actions are mechanical action provenance, not proof that a concern was solved.
- Do not infer resolved concerns by set subtraction or scores; the Agent must make a fresh visual judgement.
- Use correction history to avoid repeating an ineffective edit without changing observation strategy.

## Frozen stage representation contract
- contract: `full_body_croquis.P1.v3`
- representation: **gesture_and_construction_centrelines**
- tier: 1
- inherits from: _none_

### This stage owns
- the head's observed outline, with its facial centreline and eye line
- face direction and head tilt
- spine centreline as an S-curve from the back of the neck
- pelvis centreline and its tilt
- shoulder line and its tilt
- line of action, distinct from the spine
- joint positions: shoulder, elbow, wrist, hip, knee, ankle
- arm and leg flow lines, including occluded segments
- loose torso mass
- foot direction and ground contact
- overall silhouette envelope
- major attached-object axis

### Must preserve from earlier stages
- subject-derived standing direction
- subject-derived weight side
- whole-body energy

### Allowed representation
- the head outline read from the subject: its width, its jaw, and how much cranium the head's tilt exposes
- a curved facial centreline passing crown -> nose -> chin
- an eye line drawn through both eyes, taking its tilt from where those two eyes actually sit
- spine centreline starting behind the neck and running as an S-curve through mid-back, waist and sacrum
- pelvis centreline stating its tilt
- shoulder line stating its tilt
- one line of action that enters above the head, cuts across the body and lands ahead of the weight-bearing foot
- joint markers as small circles
- flowing limb lines from shoulder to wrist and from hip to ankle
- an inferred flow line through an occluded limb, ending where the hidden hand or foot must be
- a loose flowing torso mass
- each foot's observed shape, linked to its ankle, stating which way it points and how much it is foreshortened
- ground contact marks under the feet
- major attached-object axis

### Forbidden representation
- facial features other than the centreline and eye-line
- the hair silhouette used as the cranial outline
- a generic ellipse standing in for an observed head or foot
- the facial centreline collapsed into a plain vertical centre line
- a facial centreline that misses the nose, which turns the face the wrong way
- an eye line that does not connect both eyes
- face and spine centrelines merged into one stroke
- straight landmark-to-landmark joins that flatten limb curvature
- omitting an occluded limb because it is not visible
- hair
- garment structure
- footwear detail beyond a direction oval
- muscle definition
- cross-contours or closed volume
- attached-object detail
- rendered shading

### Detail ceiling
- a whole-body pose hypothesis at minimum information
- the centrelines that carry direction: face, spine, pelvis
- accurate joint centres and observed limb curvature
- loose mass, never resolved volume

### Next stage unlocks
- limb segments as measured straight or lightly cylindrical axes
- ribcage and pelvis axis volumes
- simple hand and foot placement blocks
- attached-object length and tilt measured against the body

## Reference authority
- reference mode: **subject_only**
- authority order: `subject_reference`
- subject reference: `/mnt/f/NowWorking/skill-forge/img2drawing/project/skills/img2drawing/examples/full_body_croquis/subject.png` — geometry truth
- task stage target: _not provided_

### Non-negotiable authority rule
- The stage contract decides representation scope; it does not decide pose correctness.
- The stage reference under `references/stages/` carries this stage's mark-making guidance, and some stages keep a rendered example beside it. Open one when you want it; never copy pose, coordinates, perspective or subject proportions from it.
- The subject reference remains geometry truth if references conflict about pose/proportion/perspective.

## Intent
Build a whole-body pose hypothesis. P1 is not a few simple lines: head, spine, shoulder and pelvis rhythm, both arms, both legs, foot direction and any large prop must all be readable at minimum information.

## Observe
- crown position, and the curvature of the facial centreline through nose and chin
- head tilt from the eye-line cross
- the spine's S-curve, starting behind the neck
- pelvis centreline and its tilt
- shoulder line and its tilt
- the line of action, which is not the spine
- shoulder, elbow, wrist, hip, knee and ankle centres
- the curvature of each limb between those joints
- any limb hidden behind clothing or a prop
- where the feet meet the ground and which way each foot points
- the overall silhouette envelope
- the major axis of a large attached object

## Draw
- the head outline read from the subject, a facial centreline through crown → between the eyes → nose → mouth → chin, and an eye line through both eyes
- a separate spine centreline: an S-curve from behind the neck through mid-back, waist and sacrum
- pelvis and shoulder lines stating their tilt
- one line of action entering above the head, cutting across the body and landing ahead of the weight-bearing foot
- joint markers as small circles
- flowing limb lines that follow observed curvature, not straight joins
- an inferred flow line through an occluded limb, ending where the hidden hand or foot must be
- a loose flowing torso mass
- each foot's observed shape linked to its ankle, stating the direction it points
- ground contact marks under each foot
- the major axis of a large attached object

## Avoid
- reading the hair silhouette as the cranial outline
- dropping a generic ellipse in for the head or a foot instead of observing its shape
- drawing the facial centreline as a plain vertical centre line
- running the facial centreline beside the nose instead of through it
- drawing the eye line without checking it meets both eyes
- merging the face and spine centrelines into one stroke
- joining joints with straight lines
- dropping an occluded limb because it cannot be seen
- copying joint positions from an example drawing instead of the subject
- moving a line to satisfy a filter or evidence map
- footwear detail — state the foot's direction and shape, not its laces and panels
- facial features, hair, garment structure, muscle or closed volume

## Mandatory review questions
- Overlay P1 on the subject: does the crown sit where the subject's crown sits, and is the head outline the subject's shape rather than a generic ellipse?
- Does the eye line say what the subject's head tilt says — level, up, or down — rather than whatever the ellipse happened to give?
- Does the facial centreline actually pass through the nose? A centreline beside the nose turns the face the wrong way, however good the outline is.
- Does the eye line pass through both eyes, and does its tilt come from where those two eyes sit rather than from a guess?
- Is the spine an S-curve that starts behind the neck, not at the chin, and is it a separate stroke from the facial centreline?
- Do shoulder and pelvis state the subject's rotation, not just a tilt?
- Are both arms present, including any hidden behind a prop or in a pocket?
- Is every joint centre on the subject's joint, or are several drifting the same way?
- Does each limb follow the subject's observed curvature, or was it joined straight?
- Do the feet land where the subject's land, and does each foot oval point the way that foot points?
- Do the foot directions agree with the body direction the rest of the drawing states?
- Is any part merely 'roughly around here'?
- With the subject hidden, does this read as this specific person in this specific pose — not just as a person?

## Advance only when
- Overlaid on the subject, head direction, spine curvature, shoulder and pelvis rotation, both arms, both legs' joint centres and both foot directions all register.
- No part of the drawing is 'roughly around here'.
- With the subject hidden, the drawing reads as this specific person in this specific pose.
- Any occluded limb has a stated hypothesis rather than being absent.
- No joint drift, no straight landmark joins, no merged face/spine stroke.

## Suggested inspection intents
- crown+face centreline
- neck+upper spine
- shoulder rhythm
- pelvis+hips
- each arm including occluded ones
- each leg
- ankles, foot direction and ground contact

## Review artifacts
- schema: `img2drawing.reference_review_artifacts.v2`
- stage: `P1_gesture`
- subject_reference: `/mnt/f/NowWorking/skill-forge/img2drawing/project/skills/img2drawing/examples/full_body_croquis/subject.png`
- subject_vs_drawing: `/mnt/f/NowWorking/skill-forge/img2drawing/project/dev/p1_reference_run/run/reviews/P1_gesture/pass_02/subject_vs_drawing.png`
- subject_split: `/mnt/f/NowWorking/skill-forge/img2drawing/project/dev/p1_reference_run/run/reviews/P1_gesture/pass_02/subject_split.png`
- subject_drawing_overlay: `/mnt/f/NowWorking/skill-forge/img2drawing/project/dev/p1_reference_run/run/reviews/P1_gesture/pass_02/subject_drawing_overlay.png`
- subject_drawing_absdiff: `/mnt/f/NowWorking/skill-forge/img2drawing/project/dev/p1_reference_run/run/reviews/P1_gesture/pass_02/subject_drawing_absdiff.png`
- overview: `/mnt/f/NowWorking/skill-forge/img2drawing/project/dev/p1_reference_run/run/reviews/P1_gesture/pass_02/reference_authority_overview.png`
- three_way: `/mnt/f/NowWorking/skill-forge/img2drawing/project/dev/p1_reference_run/run/reviews/P1_gesture/pass_02/reference_authority_overview.png`

## Canvas-scale pencil guidance
- canvas: `512 × 802`
- recommended width multiplier: **1.055×**
- minimum visible opacity for this stage: **0.55**
- minimum visible pressure for this stage: **0.45**
- Guidance only: do not silently rewrite explicit stroke intent.

## Checkpoint / resume
- checkpoint: `/mnt/f/NowWorking/skill-forge/img2drawing/project/dev/p1_reference_run/run/session/checkpoint.json`
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
