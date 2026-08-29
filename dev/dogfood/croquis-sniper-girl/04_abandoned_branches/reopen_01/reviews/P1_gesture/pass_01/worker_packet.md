# Autonomous worker packet — P1_gesture / pass 1

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
- contract: `full_body_croquis.P1.v1`
- representation: **gesture_and_weight_path**
- tier: 1
- inherits from: _none_

### This stage owns
- craniofacial centre gesture
- whole-body line of action
- pelvis weight transfer
- support vs counterbalance role
- major attached-object axis when silhouette/balance requires it

### Must preserve from earlier stages
- subject-derived head direction
- subject-derived support side
- whole-body energy

### Allowed representation
- dominant crown→face→neck→spine→pelvis→support gesture
- open head-envelope arcs, including segmented crown/temporal/jaw arcs
- shoulder rhythm
- pelvis rhythm
- counterbalance-leg flow
- major attached-object axis
- minimal landing/ground cue

### Forbidden representation
- anatomical joint construction
- ribcage/pelvis mass contour
- full limb thickness
- clothing contour
- facial features
- rendered shading

### Detail ceiling
- global gesture
- face-direction cue
- weight relationship
- major prop direction only

### Next stage unlocks
- head cross-axis
- shoulder axis
- pelvis axis
- major limb axes
- attached-object extent/breadth axis

### Grammar exemplar contract
**must show**
- dominant whole-body gesture
- head direction construction
- support/counterbalance relationship
**may show**
- shoulder rhythm
- pelvis rhythm
- minimal ground cue
- major attached-object axis
**must not show**
- ribcage mass contour
- pelvis mass contour
- full limb thickness
- joint anatomy
- clothing silhouette
- facial features

## Reference authority
- reference mode: **subject_only**
- authority order: `subject_reference > grammar_exemplar`
- subject reference: `dev/dogfood/croquis-sniper-girl/01_output/subject_reference.png` — geometry truth
- task stage target: _not provided_
- grammar exemplar: `skills/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p1_gesture.png` — representation only
- grammar exemplar audit: **FAIL**

### KNOWN GRAMMAR EXEMPLAR DEFECT
The bundled exemplar failed the frozen stage contract audit. Do not widen or distort the stage to imitate it.
- The exemplar shows only one long lower-body path and does not establish a distinct counterbalance-leg flow, so support versus counterbalance is not readable.
- The visually dominant body gesture begins at the chin/neck instead of being carried from the crown through a curved facial centre into the neck, so the craniofacial centre gesture is not demonstrated by the exemplar.
- The head reads as a nearly closed oval construction; it does not clearly teach two subordinate open envelope arcs around an asymmetric facial centre.
- audit note: R03 audit finds the bundled P1 grammar exemplar insufficient for the 0.5.2 P1 contract. Do not copy its neck-origin gesture.

### Non-negotiable authority rule
- The stage contract decides representation scope; it does not decide pose correctness.
- Never copy pose, coordinates, perspective, or subject proportions from a grammar exemplar.
- The subject reference remains geometry truth if references conflict about pose/proportion/perspective.

## Intent
Capture the full craniofacial-to-ground gesture: face direction, spinal rhythm, pelvis transfer, support leg and counterbalance before anatomy.

## Observe
- crown and top of cranium
- curved facial centre line and unequal left/right head halves
- chin-to-neck exit
- neck-to-spine flow
- pelvis centre and tilt
- support-side hip and weight-bearing leg
- counterbalance leg
- shoulder rhythm
- major attached-object axis when it changes the global envelope

## Draw
- one dominant continuous stroke from crown through curved facial centre, chin, neck, spine, pelvis and support leg to the weight landing point
- open cranial/jaw envelope arcs; use a separate short crown arc when needed so the head does not collapse into one closed egg
- subordinate shoulder rhythm
- subordinate pelvis rhythm
- secondary counterbalance-leg flow
- restrained attached-object major axis when relevant
- minimal ground/weight cue only if needed

## Avoid
- starting the main gesture at the neck instead of the crown
- straight geometric face centre that carries no face-direction information
- closed polygon/circle head symbol that overwhelms the face-axis relationship
- independent torso and leg sticks that break the neck→spine→pelvis→support path
- joint anatomy
- clothing detail
- final contour
- facial features

## Mandatory review questions
- Does the dominant gesture start at the crown, not at the neck?
- Inside the head, does the centre line curve asymmetrically and do the open crown/temporal/jaw arcs avoid reconstructing a closed badge?
- Does that same dominant intention continue through chin→neck→spine→pelvis→support leg without a conceptual break?
- Does the pelvis visibly transfer weight into one support leg instead of feeding two equivalent sticks?
- Does the opposite leg read as counterbalance?
- Are head width/height, shoulder span and pelvis breadth derived from the subject rather than copied from the exemplar?
- Is the dominant gesture materially/visually stronger than secondary construction?
- Did the worker avoid P2/P3 anatomy, clothing and contour detail?
- If a large attached object changes balance or silhouette, is its major axis already present but subordinate?

## Advance only when
- A viewer can infer the subject's head/face direction from the curved craniofacial centre line and head-envelope relationship.
- The full dominant weight path is readable from crown to the support landing point.
- Support and counterbalance roles are unambiguous.
- Large subject proportions (head/shoulder/pelvis/leg spread) are credible at P1 abstraction.
- Secondary construction supports the dominant gesture instead of competing with it.
- No major visible P1 mismatch remains after whole-view and relevant crop review.

## Suggested inspection intents
- head/face
- torso+pelvis
- pelvis+both legs
- attached object + shoulder when present

## Review artifacts
- schema: `img2drawing.reference_review_artifacts.v2`
- stage: `P1_gesture`
- subject_reference: `dev/dogfood/croquis-sniper-girl/01_output/subject_reference.png`
- grammar_exemplar: `skills/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p1_gesture.png`
- stage_exemplar: `skills/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p1_gesture.png`
- subject_vs_drawing: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P1_gesture/pass_01/subject_vs_drawing.png`
- subject_split: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P1_gesture/pass_01/subject_split.png`
- subject_drawing_overlay: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P1_gesture/pass_01/subject_drawing_overlay.png`
- subject_drawing_absdiff: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P1_gesture/pass_01/subject_drawing_absdiff.png`
- grammar_vs_drawing: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P1_gesture/pass_01/grammar_vs_drawing.png`
- exemplar_vs_drawing: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P1_gesture/pass_01/grammar_vs_drawing.png`
- overview: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P1_gesture/pass_01/reference_authority_overview.png`
- three_way: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P1_gesture/pass_01/reference_authority_overview.png`

## Canvas-scale pencil guidance
- canvas: `512 × 768`
- recommended width multiplier: **1.033×**
- minimum visible opacity for this stage: **0.18**
- minimum visible pressure for this stage: **0.18**
- Guidance only: do not silently rewrite explicit stroke intent.

## Checkpoint / resume
- checkpoint: `dev/dogfood/croquis-sniper-girl/02_run_record/checkpoint.json`
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
    grammar_box=(left, top, right, bottom),
)
```

- ROI selection authority: **Agent explicit boxes**.
- Automatic anatomy/landmark detection: **not used**.
- Runtime validates/crops/binds only.
- Each local review also writes a crop-registered subject/drawing overlay and raw absolute-difference view. These are evidence, never a score.

## Autonomous loop
1. Read pass memory first. If state is reopen_restart, treat archived target/downstream reviews as invalidated evidence and rebuild from the restored branch.
2. If carried concerns exist, re-check them before inventing new work.
3. Read the frozen stage contract before interpreting the exemplar.
4. Observe the subject at whole-body scale first; choose a local ROI only to answer a concrete uncertainty.
5. SUBJECT-ONLY MODE: no same-subject stage target exists. Construct the current stage from the subject geometry, frozen StageContract, and verified prior drawing state; do not treat the grammar exemplar as an answer image.
6. Use the grammar exemplar only for representation vocabulary allowed by the frozen stage contract.
7. Before drawing, reject vocabulary listed in forbidden_representation.
8. Draw a bounded set of explicit strokes that serve the current stage ownership.
9. Render the exact current artifact with prepare_stage_review().
10. If a whole-view question remains unresolved, choose explicit ROI boxes and call prepare_local_review().
11. Compare fresh evidence against carried concerns and the inter-pass correction actions recorded in pass memory.
12. Write contract_findings separately from reference/artifact findings and cite useful local_review_ids.
13. If any important drawing mismatch remains, choose the highest-impact 1–3 issues and revise locally.
14. After every drawing mutation, prepare fresh stage/local reviews; never reuse stale judgement.
15. After carried concerns appear cleared, perform one fresh residual-mismatch sweep that is NOT limited to the prior concern list; inspect the whole view and a high-risk ROI before setting remaining_concerns=[] .
16. Advance only when both the carried-concern recheck and the fresh residual sweep find no important mismatch at the current stage purpose.
17. If a later stage exposes an earlier foundational error, reopen the earliest responsible stage.

## Autonomy policy
- Do not stop after a pass merely to ask the user whether to continue.
- Do not ask the user to approve routine stage transitions; the worker owns the self-review loop.
- Use pass memory to continue unresolved work rather than resetting the stage mentally each pass.
- Do not treat inter-pass action provenance as proof that a concern was solved.
- Do not let the prior concern list become the review boundary; new defects found in the residual sweep can keep the stage at REVISE.
- Never use a grammar exemplar as pose/coordinate truth.
- Never use CV/evidence maps or crop automation as semantic authority.

## Escalation policy
- Ask the user only when the source reference is missing/unreadable, the requested goal is internally contradictory, or a choice genuinely changes the intended artistic target.
- Repeated visual failure is not itself a reason to ask the user; change observation strategy, crop, stroke plan, or reopen the responsible stage first.
