# Autonomous worker packet — P2_primary_axes / pass 1

## Stage pass memory
- state: **reopen_restart**
- prior review count: 0
- previous decision: _archived / invalidated by reopen_
- carried concerns: _read reopen context below_

### REOPEN CONTEXT
- reopen id: `reopen_01`
- role: **invalidated_downstream**
- target stage: `P1_gesture`
- discovered in: `P2_primary_axes`
- reason: P2 evidence proves the inherited P1 counterbalance flow disagrees with the subject's braced thigh centre through the upper thigh, and correcting it downstream would harden a compensating P2 axis. Reopening the earliest responsible stage.

#### Findings that caused the reopen
- Subject braced-thigh centre measured at canvas x~258-264 for y 415-460.
- P1 counterbalance stroke sits at x~267-273 over the same range.
- Result at P2 is a two-line pant-leg rail down the thigh.

Do not reuse archived downstream judgements as current evidence. Rebuild from the restored authoritative history.

### Memory policy
- This active review epoch was restarted by an upstream/downstream reopen; read reopen_context before drawing.
- Rebuild from the restored authoritative history, not from archived invalidated artifacts.
- The reopen reason is Agent-authored evidence; runtime does not invent the correction.
- Concern resolution must be stated by the Agent in a fresh review, not inferred by the runtime.

## Frozen stage representation contract
- contract: `full_body_croquis.P2.v1`
- representation: **primary_axes**
- tier: 2
- inherits from: `P1_gesture`

### This stage owns
- head cross-axis
- shoulder axis
- pelvis axis
- major arm direction chains
- major leg direction chains
- attached-object extent/breadth axis

### Must preserve from earlier stages
- P1 crown-to-support gesture
- P1 face direction
- P1 support/counterbalance roles
- P1 weight landing

### Allowed representation
- dominant crown→face→neck→spine→pelvis→support gesture
- open head-envelope arcs
- shoulder rhythm
- pelvis rhythm
- counterbalance-leg flow
- major attached-object axis
- minimal landing/ground cue
- head cross-axis
- shoulder axis
- pelvis axis
- major limb axes
- attached-object extent/breadth axis

### Forbidden representation
- ribcage side contour
- ribcage mass contour
- pelvis side contour
- pelvis mass contour
- full arm thickness
- full thigh/shin thickness
- constructed hand block
- constructed foot/boot block
- joint anatomy
- clothing block-in
- final silhouette
- rendered shading

### Detail ceiling
- axis relationships
- tilt and twist direction
- foreshortening direction
- prop extent/breadth
- no volume closure

### Next stage unlocks
- head/hair mass
- ribcage mass contour
- pelvis mass contour
- torso bridge
- tapered limb masses
- attached-object mass

### Grammar exemplar contract
**must show**
- head direction axis
- shoulder axis
- pelvis axis
- major arm and leg axes
- preserved P1 gesture
**may show**
- open head envelope
- minimal pelvis/shoulder rhythms from P1
- attached-object extent/breadth axis
- tiny endpoint ticks
**must not show**
- ribcage side contour
- closed torso mass
- closed pelvis mass
- full limb thickness
- hand block
- foot/boot block
- joint anatomy
- clothing silhouette

## Reference authority
- reference mode: **subject_only**
- authority order: `subject_reference > grammar_exemplar`
- subject reference: `dev/dogfood/croquis-sniper-girl/01_output/subject_reference.png` — geometry truth
- task stage target: _not provided_
- grammar exemplar: `skills/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p2_axes.png` — representation only
- grammar exemplar audit: **PASS**

### Non-negotiable authority rule
- The stage contract decides representation scope; it does not decide pose correctness.
- Never copy pose, coordinates, perspective, or subject proportions from a grammar exemplar.
- The subject reference remains geometry truth if references conflict about pose/proportion/perspective.

## Intent
Translate the closed P1 gesture into directional axes without losing its energy or support relationship.

## Observe
- head direction
- shoulder tilt
- pelvis tilt
- limb directions
- prop direction and breadth
- foreshortening cues

## Draw
- head axis
- shoulder axis
- pelvis axis
- major limb axes
- attached-object extent

## Avoid
- surface detail
- folds
- final contour
- small anatomy
- redrawing P1 as a new unrelated scaffold

## Mandatory review questions
- Do head/shoulder/pelvis axes explain the same pose already established in P1?
- Do shoulder and pelvis tilts communicate twist rather than behave as unrelated bars?
- Do limb axes originate from the correct body masses rather than float independently?
- Does the attached-object breadth/axis agree with the subject and with the P1 global envelope?

## Advance only when
- Axes clarify the P1 pose without changing its dominant gesture.
- Torso twist, pelvis relation, support leg and limb directions are readable.
- No major axis-level mismatch remains in subject-vs-drawing review.

## Suggested inspection intents
- head+shoulders
- torso+pelvis
- pelvis+legs
- prop overlap

## Review artifacts
- schema: `img2drawing.reference_review_artifacts.v2`
- stage: `P2_primary_axes`
- subject_reference: `dev/dogfood/croquis-sniper-girl/01_output/subject_reference.png`
- grammar_exemplar: `skills/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p2_axes.png`
- stage_exemplar: `skills/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p2_axes.png`
- subject_vs_drawing: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P2_primary_axes/pass_01/subject_vs_drawing.png`
- subject_split: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P2_primary_axes/pass_01/subject_split.png`
- subject_drawing_overlay: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P2_primary_axes/pass_01/subject_drawing_overlay.png`
- subject_drawing_absdiff: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P2_primary_axes/pass_01/subject_drawing_absdiff.png`
- grammar_vs_drawing: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P2_primary_axes/pass_01/grammar_vs_drawing.png`
- exemplar_vs_drawing: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P2_primary_axes/pass_01/grammar_vs_drawing.png`
- overview: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P2_primary_axes/pass_01/reference_authority_overview.png`
- three_way: `dev/dogfood/croquis-sniper-girl/03_stage_reviews/P2_primary_axes/pass_01/reference_authority_overview.png`

## Canvas-scale pencil guidance
- canvas: `512 × 768`
- recommended width multiplier: **1.033×**
- minimum visible opacity for this stage: **0.23**
- minimum visible pressure for this stage: **0.22**
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
