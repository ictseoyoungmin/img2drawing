# Autonomous worker packet — P6_identity_finish / pass 1

## Stage pass memory
- state: **reopen_restart**
- prior review count: 0
- previous decision: _archived / invalidated by reopen_
- carried concerns: _read reopen context below_

### REOPEN CONTEXT
- reopen id: `reopen_04`
- role: **invalidated_downstream**
- target stage: `P5_clean_blockin`
- discovered in: `P6_identity_finish`
- reason: P6 preflight found that the P5 hair silhouette owns the face opening.

#### Findings that caused the reopen
- hair/face ownership is an upstream structural mismatch; P6 cannot repair it

Do not reuse archived downstream judgements as current evidence. Rebuild from the restored authoritative history.

### Memory policy
- This active review epoch was restarted by an upstream/downstream reopen; read reopen_context before drawing.
- Rebuild from the restored authoritative history, not from archived invalidated artifacts.
- The reopen reason is Agent-authored evidence; runtime does not invent the correction.
- Concern resolution must be stated by the Agent in a fresh review, not inferred by the runtime.

## Frozen stage representation contract
- contract: `full_body_croquis.P6.v1`
- representation: **optional_identity_finish**
- tier: 6
- inherits from: `P5_clean_blockin`

### This stage owns
- head-turn-preserving eye, nose, mouth and chin relationship
- grouped hair locks and face occlusion
- identity-defining garment and prop marks
- selective pressure, taper and accent expression

### Must preserve from earlier stages
- P5 contour ownership and clean block-in
- P3 volume and proportion
- P1/P2 head turn, balance and ground contact

### Allowed representation
- proportional facial features bound to the observed head turn
- grouped hair locks and representative tips
- sparse structural garment folds
- selective restatement with per-point pressure and taper

### Forbidden representation
- pixel tracing
- upstream structural correction
- blanket confirmation
- broad value bands
- unlimited micro texture

### Detail ceiling
- identity-defining relationships only
- no rendering claim
- bounded line-expression budget

### Next stage unlocks
- _none; final stage in this contract_

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
Only after P1–P5 are visually closed, add a bounded set of identity-defining feature, hair, garment and line-expression marks.

## Observe
- the frozen head turn, eye line, jaw and feature intervals
- hair parting, grouped locks and face occlusion
- identity-defining garment breaks, sparse folds and prop contacts
- the selected pressure/taper calibration on the actual canvas

## Draw
- proportional eye/nose/mouth relationship bound to the observed head turn
- outer hair mass plus a small number of grouped internal locks
- sparse form-following folds at anchors, tension and compression events
- selective contour accent and restatement with explicit pressure samples

## Avoid
- upstream pose, volume, view or contour-ownership correction
- pixel-by-pixel edge tracing
- blanket confirmation or whole-contour darkening
- broad charcoal/value bands and unlimited micro-detail

## Mandatory review questions
- Does the eye line and facial centreline still state the locked head turn?
- Are the eyes, nose, mouth and chin in a proportional relationship rather than arbitrary marks?
- Does hair remain grouped into a seated mass with only representative locks?
- Do sparse folds explain anchor, tension or compression rather than texture?
- Is accent limited to the selected high-information 15–25% of marks?
- Did no P1–P5 blocker get hidden under identity detail?

## Advance only when
- P1–P5 preflight is clear of structural blockers.
- Feature, hair, garment and line-expression marks stay inside their declared budgets.
- A fresh whole-view and applicable close-crop review finds no unresolved identity mismatch owned by P6.

## Suggested inspection intents
- face relation
- hair grouping
- garment anchor/fold
- hands/footwear/prop contact

## Review artifacts
- schema: `img2drawing.reference_review_artifacts.v2`
- stage: `P6_identity_finish`
- subject_reference: `dev/dogfood/croquis-sniper-girl/01_output/subject_reference.png`
- subject_vs_drawing: `dev/evidence/material-integration/s10-quality-run/reviews/P6_identity_finish/pass_01/subject_vs_drawing.png`
- subject_split: `dev/evidence/material-integration/s10-quality-run/reviews/P6_identity_finish/pass_01/subject_split.png`
- subject_drawing_overlay: `dev/evidence/material-integration/s10-quality-run/reviews/P6_identity_finish/pass_01/subject_drawing_overlay.png`
- subject_drawing_absdiff: `dev/evidence/material-integration/s10-quality-run/reviews/P6_identity_finish/pass_01/subject_drawing_absdiff.png`
- overview: `dev/evidence/material-integration/s10-quality-run/reviews/P6_identity_finish/pass_01/reference_authority_overview.png`
- three_way: `dev/evidence/material-integration/s10-quality-run/reviews/P6_identity_finish/pass_01/reference_authority_overview.png`

## Canvas-scale pencil guidance
- canvas: `512 × 768`
- recommended width multiplier: **1.033×**
- minimum visible opacity for this stage: **0.55**
- minimum visible pressure for this stage: **0.45**
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
