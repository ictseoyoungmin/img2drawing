# Autonomous worker packet — P4_structural_connections / pass 1

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
- contract: `full_body_croquis.P4.v2`
- representation: **real_form_connection**
- tier: 4
- inherits from: `P3_primary_masses`

### This stage owns
- hair mass seated on the skull
- garment structure over the body (shoulder → sleeve → elbow → wrist)
- waistline and garment openings
- hand and foot form
- footwear structure
- attached-object major structure and its contact with the body
- strap, sling, holster and pocket attachment

### Must preserve from earlier stages
- P3 volumes and proportion
- P2 joint positions
- P1 balance and ground contact

### Allowed representation
- how a garment hangs on the underlying volume
- hair as a large mass over the cranium, not strand by strand
- major prop structure: barrel direction, stock, receiver, magazine, sling
- contact and overlap points between object and body
- placement of facial features, kept minimal
- resolved hand, foot and footwear form

### Forbidden representation
- buttons, stitching and micro garment detail
- individual hair strands
- micro folds
- surface texture
- tonal rendering

### Detail ceiling
- how the real form connects to the body
- large structure of clothing, hair and equipment
- structure before decoration
- no rendering

### Next stage unlocks
- selecting which explored line is the final form
- subordinating superseded construction with soft_lift or fully retiring it with delete_stroke when the current contour replaces it, while preserving history
- explicit occlusion handoff where one mass passes behind another

## Reference authority
- reference mode: **subject_only**
- comparison order: `subject_reference` (subject remains geometry and visible-edge truth)
- subject reference: `dev/dogfood/croquis-sniper-girl/01_output/subject_reference.png` — geometry truth
- task stage target: _not provided_

### Non-negotiable authority rule
- The stage contract decides representation scope; it does not decide pose correctness.
- The stage reference under `references/stages/` carries this stage's mark-making guidance, and some stages keep a rendered example beside it. Open one when you want it; never copy pose, coordinates, perspective or subject proportions from it.
- The subject reference remains geometry truth if references conflict about pose/proportion/perspective.

## Intent
Connect the real subject's form to the body masses: how clothing, hair and equipment sit on the volumes underneath. Structure, not decoration.

## Observe
- how the hair mass sits on the skull
- how the garment hangs across shoulder → sleeve → elbow → wrist
- waistline and garment openings
- hand and foot form
- footwear structure
- the major structure of a large attached object
- where straps, slings, holsters and pockets attach and overlap

## Draw
- hair as a large mass over the cranium
- garment structure resolved over the underlying volume
- hand and foot form and footwear structure
- major prop structure: barrel direction, stock, receiver, magazine, sling
- contact and overlap points between object and body
- minimal placement of facial features

## Avoid
- buttons, stitching and micro garment detail
- individual hair strands
- micro folds
- surface texture
- tonal rendering

## Mandatory review questions
- Does the hair sit on the cranium as a mass, or was it drawn strand by strand?
- Does the garment hang on the arm chain rather than float beside it?
- Is the waistline placed on the pelvis volume from P3?
- Do the hands and feet grow out of their limbs instead of reading as detached blocks?
- Is the attached object's major structure connected to where it touches the body?
- Was structure solved before decoration — no buttons or stitching yet?
- Are the P3 volumes and proportion preserved underneath?

## Advance only when
- The drawing reads as this specific subject, not a generic mannequin.
- Clothing, hair and equipment are connected to the volumes beneath them.
- Hands, feet and footwear have form and stay attached to their limbs.
- The attached object's major structure and body contact are explicit.
- No major visible P4 mismatch remains after whole-view and relevant crop review.

## Suggested inspection intents
- head+hair
- shoulder→sleeve→wrist
- waist+garment opening
- hand
- foot+footwear
- object↔body contact

## Review artifacts
- schema: `img2drawing.reference_review_artifacts.v2`
- stage: `P4_structural_connections`
- subject_reference: `dev/dogfood/croquis-sniper-girl/01_output/subject_reference.png`
- subject_vs_drawing: `dev/evidence/material-integration/s10-quality-run/reviews/P4_structural_connections/pass_01/subject_vs_drawing.png`
- subject_split: `dev/evidence/material-integration/s10-quality-run/reviews/P4_structural_connections/pass_01/subject_split.png`
- subject_drawing_overlay: `dev/evidence/material-integration/s10-quality-run/reviews/P4_structural_connections/pass_01/subject_drawing_overlay.png`
- subject_drawing_absdiff: `dev/evidence/material-integration/s10-quality-run/reviews/P4_structural_connections/pass_01/subject_drawing_absdiff.png`
- overview: `dev/evidence/material-integration/s10-quality-run/reviews/P4_structural_connections/pass_01/reference_authority_overview.png`
- three_way: `dev/evidence/material-integration/s10-quality-run/reviews/P4_structural_connections/pass_01/reference_authority_overview.png`

## Canvas-scale pencil guidance
- canvas: `512 × 768`
- recommended width multiplier: **1.033×**
- minimum visible opacity for this stage: **0.58**
- minimum visible pressure for this stage: **0.48**
- Guidance only: do not silently rewrite explicit stroke intent.

## Checkpoint / resume
- checkpoint: `dev/evidence/material-integration/s10-quality-run/session/checkpoint.json`
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
