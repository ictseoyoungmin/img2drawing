# Autonomous worker packet — P5_clean_blockin / pass 1

## Stage pass memory
- state: **reopen_restart**
- prior review count: 0
- previous decision: _archived / invalidated by reopen_
- carried concerns: _read reopen context below_

### REOPEN CONTEXT
- reopen id: `reopen_02`
- role: **invalidated_downstream**
- target stage: `P3_primary_masses`
- discovered in: `P5_clean_blockin`
- reason: P5 cleanup preflight proves the verified left outer silhouette cannot be stated without contradicting the inherited P3 prop and torso-left envelopes. The prop axis and extent are credible, so the underfilled P3 envelope, not P2 or P1, is the earliest responsible stage.

#### Findings that caused the reopen
- Measured left outer edge: canvas x=136 at y=140, 145 at y=190, 149 at y=220, 152 at y=270, 150 at y=300, 160 at y=340, 163 at y=396.
- Inherited P3 rifle mass sits up to 16px right of that edge through the middle of the prop.
- Inherited P3 torso-left contour underfills the observed occupied volume by about 12px over the same range.
- Silhouette ownership handoff from prop to garment occurs near canvas y=205.

Do not reuse archived downstream judgements as current evidence. Rebuild from the restored authoritative history.

### Memory policy
- This active review epoch was restarted by an upstream/downstream reopen; read reopen_context before drawing.
- Rebuild from the restored authoritative history, not from archived invalidated artifacts.
- The reopen reason is Agent-authored evidence; runtime does not invent the correction.
- Concern resolution must be stated by the Agent in a fresh review, not inferred by the runtime.

## Frozen stage representation contract
- contract: `full_body_croquis.P5.v1`
- representation: **clean_blockin_contour**
- tier: 5
- inherits from: `P4_structural_connections`

### This stage owns
- decisive outer silhouette
- major clothing silhouette
- major internal contour breaks
- construction-line retirement
- silhouette-owner handoff
- clean attached-object silhouette

### Must preserve from earlier stages
- P1 gesture and weight
- P2 directional axes
- P3 masses/negative spaces
- P4 joint/attachment logic

### Allowed representation
- head/hair mass
- major clothing silhouette
- decisive outer contour
- major internal contour breaks
- overlap contour between adjacent masses
- silhouette-owner handoff with a visible break or occlusion
- joint/attachment-informed contour
- hand/foot silhouette
- clean attached-object silhouette
- construction-line retirement

### Forbidden representation
- rendered tonal shading
- micro texture
- micro clothing folds
- accidental contour welding between independent semantic masses
- beautification that changes verified structure

### Detail ceiling
- clean block-in
- readable silhouette
- major internal structure only
- no tonal finish

### Next stage unlocks
- _none; final stage in this contract_

### Grammar exemplar contract
**must show**
- readable whole silhouette
- clean major clothing/body contour
- major internal contour breaks
- subordinated construction
**may show**
- major pockets/accessory shapes
- simple hair grouping
- clean prop silhouette
**must not show**
- rendered shading
- micro texture
- micro fold rendering

## Reference authority
- reference mode: **subject_only**
- authority order: `subject_reference > grammar_exemplar`
- subject reference: `dev/dogfood/croquis-sniper-girl/01_output/subject_reference.png` — geometry truth
- task stage target: _not provided_
- grammar exemplar: `skills/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p5_clean_blockin.png` — representation only
- grammar exemplar audit: **FAIL**

### KNOWN GRAMMAR EXEMPLAR DEFECT
The bundled exemplar failed the frozen stage contract audit. Do not widen or distort the stage to imitate it.
- The exemplar contains extensive tonal hatching/shading across hair, clothing and trousers, exceeding clean block-in scope.
- Numerous micro folds and texture marks appear in sleeves, trousers and shoes.
- Facial and hair rendering are developed enough to read as a finished sketch rather than a clean structural block-in.
- audit note: P5 currently demonstrates a finished pencil illustration, not the frozen clean-block-in stage.

### Non-negotiable authority rule
- The stage contract decides representation scope; it does not decide pose correctness.
- Never copy pose, coordinates, perspective, or subject proportions from a grammar exemplar.
- The subject reference remains geometry truth if references conflict about pose/proportion/perspective.

## Intent
State a readable silhouette from verified structure while keeping construction subordinate.

## Observe
- whole silhouette
- head/body proportion
- torso-pelvis relation
- stance
- negative space
- prop alignment
- line hierarchy

## Draw
- decisive outer contour
- major internal breaks
- major attached-object subpart topology
- explicit silhouette-owner handoffs
- overlap contours
- only necessary surviving construction

## Avoid
- tone rendering
- micro-detail
- accidental contour welding between independent masses
- beautification that hides structural error
- cleaning a wrong structure instead of reopening it

## Mandatory review questions
- Does the final block-in preserve the verified P1-P4 structure?
- Is the main silhouette readable without construction noise?
- Are head/body/leg/prop proportions credible against the subject?
- Has rejected construction receded through replayable retirement rather than accumulating as dead lines?
- At hair/garment/limb/attached-object handoffs, does each visible contour keep one semantic owner instead of visually welding two masses together?
- If a large attached object changes the silhouette, are its major width changes/subparts readable without micro-detail?

## Advance only when
- The figure and attached objects are immediately readable from silhouette and major internal breaks.
- Construction is subordinate and no major structural error is being hidden by cleanup.
- No major block-in mismatch remains, and P5 did not draw outside P3/P4 merely to hide an upstream error.

## Suggested inspection intents
- whole silhouette
- head+torso
- pelvis+legs
- prop integration

## Review artifacts
- schema: `img2drawing.reference_review_artifacts.v2`
- stage: `P5_clean_blockin`
- subject_reference: `dev/dogfood/croquis-sniper-girl/01_output/subject_reference.png`
- grammar_exemplar: `skills/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p5_clean_blockin.png`
- stage_exemplar: `skills/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p5_clean_blockin.png`
- subject_vs_drawing: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P5_clean_blockin/pass_01/subject_vs_drawing.png`
- subject_split: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P5_clean_blockin/pass_01/subject_split.png`
- subject_drawing_overlay: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P5_clean_blockin/pass_01/subject_drawing_overlay.png`
- subject_drawing_absdiff: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P5_clean_blockin/pass_01/subject_drawing_absdiff.png`
- grammar_vs_drawing: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P5_clean_blockin/pass_01/grammar_vs_drawing.png`
- exemplar_vs_drawing: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P5_clean_blockin/pass_01/grammar_vs_drawing.png`
- overview: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P5_clean_blockin/pass_01/reference_authority_overview.png`
- three_way: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P5_clean_blockin/pass_01/reference_authority_overview.png`

## Canvas-scale pencil guidance
- canvas: `512 × 768`
- recommended width multiplier: **1.033×**
- minimum visible opacity for this stage: **0.48**
- minimum visible pressure for this stage: **0.42**
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
