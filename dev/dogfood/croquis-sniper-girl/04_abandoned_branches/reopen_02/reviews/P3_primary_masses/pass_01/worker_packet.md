# Autonomous worker packet — P3_primary_masses / pass 1

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
- contract: `full_body_croquis.P3.v1`
- representation: **connected_primary_masses**
- tier: 3
- inherits from: `P2_primary_axes`

### This stage owns
- head/hair mass
- ribcage mass
- pelvis mass
- torso bridge
- tapered limb masses
- attached-object mass
- major negative spaces

### Must preserve from earlier stages
- P1 gesture and weight path
- P2 head/shoulder/pelvis axes
- P2 limb directions
- P2 attached-object axes

### Allowed representation
- dominant crown→face→neck→spine→pelvis→support gesture
- head cross-axis
- shoulder axis
- pelvis axis
- major limb axes
- attached-object extent/breadth axis
- head/hair mass
- ribcage mass contour
- pelvis mass contour
- torso bridge
- tapered limb masses
- attached-object mass

### Forbidden representation
- detailed shoulder insertion
- elbow joint plane construction
- knee joint plane construction
- ankle articulation
- hand/finger detail
- boot detail
- clothing folds
- final cleaned silhouette
- rendered shading

### Detail ceiling
- organic connected volumes
- limb taper
- major overlap
- major negative space
- no articulated joint detail

### Next stage unlocks
- shoulder insertion
- elbow transition
- wrist transition
- hip-to-thigh insertion
- knee transition
- ankle-to-foot transition
- hand/foot block
- strap/holster/prop attachment

### Grammar exemplar contract
**must show**
- connected ribcage and pelvis masses
- torso bridge
- tapered limb masses
- preserved underlying axes
**may show**
- head/hair mass
- attached-object mass
- simple hand/foot endpoints
**must not show**
- articulated elbow anatomy
- articulated knee anatomy
- detailed hand block
- detailed boot block
- clothing folds
- clean final contour

## Reference authority
- reference mode: **subject_only**
- authority order: `subject_reference > grammar_exemplar`
- subject reference: `/home/claude/work/subject.png` — geometry truth
- task stage target: _not provided_
- grammar exemplar: `/tmp/skill/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p3_masses.png` — representation only
- grammar exemplar audit: **PASS**

### Non-negotiable authority rule
- The stage contract decides representation scope; it does not decide pose correctness.
- Never copy pose, coordinates, perspective, or subject proportions from a grammar exemplar.
- The subject reference remains geometry truth if references conflict about pose/proportion/perspective.

## Intent
Turn verified axes into connected organic masses while preserving the P1/P2 rhythm.

## Observe
- ribcage volume
- pelvis wedge
- torso bridge
- limb taper
- overlap
- head/hair mass
- attached-object mass

## Draw
- head mass
- ribcage mass
- pelvis mass
- torso bridge
- tapered limb masses
- attached-object mass

## Avoid
- joint dots as substitutes for structure
- box assembly that breaks spinal flow
- clothing folds
- rendered facial features

## Mandatory review questions
- Do ribcage and pelvis read as connected organic masses rather than boxes?
- Does the torso bridge preserve spinal rhythm and twist?
- Do limbs taper and emerge from the pelvis/shoulder masses naturally?
- Does the attached object read as an integrated long mass rather than a floating object?

## Advance only when
- The figure is readable as connected masses at a glance.
- The subject silhouette and major negative spaces are credible at mass level.
- No major mass/connection mismatch remains.

## Suggested inspection intents
- torso+pelvis
- shoulder+arm
- pelvis+thighs
- prop overlap

## Review artifacts
- schema: `img2drawing.reference_review_artifacts.v2`
- stage: `P3_primary_masses`
- subject_reference: `/home/claude/work/subject.png`
- grammar_exemplar: `/tmp/skill/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p3_masses.png`
- stage_exemplar: `/tmp/skill/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p3_masses.png`
- subject_vs_drawing: `/home/claude/work/croquis/out/reviews/P3_primary_masses/pass_01/subject_vs_drawing.png`
- subject_split: `/home/claude/work/croquis/out/reviews/P3_primary_masses/pass_01/subject_split.png`
- subject_drawing_overlay: `/home/claude/work/croquis/out/reviews/P3_primary_masses/pass_01/subject_drawing_overlay.png`
- subject_drawing_absdiff: `/home/claude/work/croquis/out/reviews/P3_primary_masses/pass_01/subject_drawing_absdiff.png`
- grammar_vs_drawing: `/home/claude/work/croquis/out/reviews/P3_primary_masses/pass_01/grammar_vs_drawing.png`
- exemplar_vs_drawing: `/home/claude/work/croquis/out/reviews/P3_primary_masses/pass_01/grammar_vs_drawing.png`
- overview: `/home/claude/work/croquis/out/reviews/P3_primary_masses/pass_01/reference_authority_overview.png`
- three_way: `/home/claude/work/croquis/out/reviews/P3_primary_masses/pass_01/reference_authority_overview.png`

## Canvas-scale pencil guidance
- canvas: `512 × 768`
- recommended width multiplier: **1.033×**
- minimum visible opacity for this stage: **0.34**
- minimum visible pressure for this stage: **0.3**
- Guidance only: do not silently rewrite explicit stroke intent.

## Checkpoint / resume
- checkpoint: `/home/claude/work/croquis/out/session/checkpoint.json`
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
