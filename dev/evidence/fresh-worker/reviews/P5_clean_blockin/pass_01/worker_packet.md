# Autonomous worker packet — P5_clean_blockin / pass 1

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
- contract: `full_body_croquis.P5.v2`
- representation: **clean_block_in**
- tier: 5
- inherits from: `P4_structural_connections`

### This stage owns
- decisive outer silhouette
- resolved face form
- resolved hair silhouette
- decided garment contour
- tidied hands and footwear
- settled equipment form
- construction-line retirement
- silhouette-owner handoff between overlapping masses

### Must preserve from earlier stages
- P4 real-form structure
- P3 volume and proportion
- P1 balance and ground contact

### Allowed representation
- selecting which explored line is the final form
- subordinating superseded construction with soft_lift or fully retiring it with delete_stroke when the current contour replaces it, while preserving history
- resolved face and hair silhouette
- major internal contour breaks
- explicit occlusion handoff where one mass passes behind another

### Forbidden representation
- tonal shading and filled black areas
- surface texture
- excessive garment folds
- fine skin rendering
- accidental contour welding between independent masses

### Detail ceiling
- which lines survive
- readable silhouette and tidy internal line
- an under-drawing solid enough that detail will not collapse it
- no tonal finish

### Next stage unlocks
- _none; final stage in this contract_

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
Decide which lines are the final form. Clean means selection, not heavier strokes, and this is an under-drawing, not a finished illustration.

## Observe
- which explored line is the real contour
- the face form
- the hair silhouette
- the garment contour
- hands and footwear
- equipment form
- where overlapping lines need a break rather than a weld

## Draw
- the decided contour drawn first
- superseded construction subordinated with soft_lift or fully retired with delete_stroke when the current contour replaces it, while keeping history
- resolved face and hair silhouette
- major internal contour breaks
- an explicit occlusion handoff where one mass passes behind another

## Avoid
- tonal shading and filled black areas
- surface texture
- excessive garment folds
- fine skin rendering
- welding two independent masses into one continuous contour

## Mandatory review questions
- Was the final line selected, or were the existing lines merely darkened?
- Is the face form clear without becoming rendered detail?
- Is the hair a resolved silhouette rather than strands?
- Are the garment contours decided?
- Are hands, footwear and equipment tidy?
- Where two masses overlap, does the contour hand off with a visible break instead of welding?
- Is this an under-drawing solid enough that detail would not collapse it?
- Did the worker avoid shading, texture and micro folds?

## Advance only when
- The silhouette is readable and the surviving internal lines are chosen, not accumulated.
- Face, hair, garment, hands, footwear and equipment forms are decided.
- Contour ownership is explicit wherever masses overlap.
- Where a structural error surfaced, the earliest responsible stage was reopened rather than repainted over.
- No major visible P5 mismatch remains after whole-view and relevant crop review.

## Suggested inspection intents
- head+face
- hair silhouette
- garment contour
- hands
- footwear
- overlap handoff regions

## Review artifacts
- schema: `img2drawing.reference_review_artifacts.v2`
- stage: `P5_clean_blockin`
- subject_reference: `skills/img2drawing/examples/full_body_croquis/subject.png`
- subject_vs_drawing: `dev/evidence/fresh-worker/reviews/P5_clean_blockin/pass_01/subject_vs_drawing.png`
- subject_split: `dev/evidence/fresh-worker/reviews/P5_clean_blockin/pass_01/subject_split.png`
- subject_drawing_overlay: `dev/evidence/fresh-worker/reviews/P5_clean_blockin/pass_01/subject_drawing_overlay.png`
- subject_drawing_absdiff: `dev/evidence/fresh-worker/reviews/P5_clean_blockin/pass_01/subject_drawing_absdiff.png`
- overview: `dev/evidence/fresh-worker/reviews/P5_clean_blockin/pass_01/reference_authority_overview.png`
- three_way: `dev/evidence/fresh-worker/reviews/P5_clean_blockin/pass_01/reference_authority_overview.png`

## Canvas-scale pencil guidance
- canvas: `512 × 802`
- recommended width multiplier: **1.055×**
- minimum visible opacity for this stage: **0.62**
- minimum visible pressure for this stage: **0.52**
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
