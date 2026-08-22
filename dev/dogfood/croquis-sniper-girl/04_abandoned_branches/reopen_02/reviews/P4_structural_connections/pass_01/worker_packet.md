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
- contract: `full_body_croquis.P4.v1`
- representation: **mannequin_connections**
- tier: 4
- inherits from: `P3_primary_masses`

### This stage owns
- shoulder insertion
- elbow/wrist transitions
- hip-to-thigh insertion
- knee/ankle transitions
- hand/foot blocks
- prop/strap/holster attachment and overlap

### Must preserve from earlier stages
- P1 gesture and weight
- P2 axes
- P3 connected masses
- P3 negative spaces

### Allowed representation
- head/hair mass
- ribcage mass contour
- pelvis mass contour
- torso bridge
- tapered limb masses
- attached-object mass
- shoulder insertion
- elbow transition
- wrist transition
- hip-to-thigh insertion
- knee transition
- ankle-to-foot transition
- hand/foot block
- strap/holster/prop attachment

### Forbidden representation
- final polished clothing silhouette
- micro clothing folds
- surface texture
- tonal rendering
- micro facial detail

### Detail ceiling
- functional mannequin articulation
- attachment/overlap
- simple hands/feet
- no polish rendering

### Next stage unlocks
- decisive outer contour
- major clothing silhouette
- major internal contour breaks
- construction-line retirement

### Grammar exemplar contract
**must show**
- connected mannequin limb chains
- joint transitions
- hand/foot blocks
- major prop attachments/overlaps
**may show**
- simple clothing envelope where needed for attachment
- major accessory block
**must not show**
- polished clothing contour
- micro folds
- surface texture
- tonal shading

## Reference authority
- reference mode: **subject_only**
- authority order: `subject_reference > grammar_exemplar`
- subject reference: `/home/claude/work/subject.png` — geometry truth
- task stage target: _not provided_
- grammar exemplar: `/tmp/skill/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p4_structure.png` — representation only
- grammar exemplar audit: **FAIL**

### KNOWN GRAMMAR EXEMPLAR DEFECT
The bundled exemplar failed the frozen stage contract audit. Do not widen or distort the stage to imitate it.
- Elbows, knees and several other joints are represented primarily as dots on line chains rather than as directional structural transitions between connected masses.
- Hip-to-thigh and shoulder insertion relationships are only weakly explained; the exemplar relies on markers more than insertion geometry.
- audit note: The exemplar demonstrates joint locations but not the structural transition grammar required by the P4 contract.

### Non-negotiable authority rule
- The stage contract decides representation scope; it does not decide pose correctness.
- Never copy pose, coordinates, perspective, or subject proportions from a grammar exemplar.
- The subject reference remains geometry truth if references conflict about pose/proportion/perspective.

## Intent
Clarify functional joint transitions and how masses connect through the limb chains.

## Observe
- shoulder insertion
- elbow turn
- wrist direction
- hip-to-thigh
- knee plane
- ankle-to-foot
- prop overlap and attachment

## Draw
- limb chains
- partial directional joint planes
- joint transitions
- hands/feet blocks
- overlap corrections
- attachment relationships

## Avoid
- joint dots without form transition
- full-width elbow/knee bands that read as clothing stripes
- faceted detached hand/foot polygons
- final shading
- texture
- decorative detail

## Mandatory review questions
- Can each arm be followed shoulder→elbow→wrist as a connected chain?
- Can each leg be followed pelvis→knee→ankle as a connected chain?
- Do joints explain directional change with local transitions rather than dots or full-width decorative bands?
- If loose clothing hides a joint, is the functional transition readable without drawing a naked joint or a decorative full-width stripe?
- Do simple hand blocks attach to the wrist and respect occlusion instead of floating beside the sleeve?
- Are feet/boots smoothly connected to the ankle, directionally credible and grounded?
- Are holsters/straps/props physically attached rather than floating?

## Advance only when
- Major joint transitions are structurally readable without becoming dots, bands or final clothing detail.
- Limb chains, hand/foot blocks and attachments remain consistent from whole view and local crops.
- A fresh residual-mismatch sweep finds no major connection-level mismatch or upstream mass error.

## Suggested inspection intents
- shoulder+elbow
- pelvis+knee
- ankle+foot
- prop/strap attachment

## Review artifacts
- schema: `img2drawing.reference_review_artifacts.v2`
- stage: `P4_structural_connections`
- subject_reference: `/home/claude/work/subject.png`
- grammar_exemplar: `/tmp/skill/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p4_structure.png`
- stage_exemplar: `/tmp/skill/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/p4_structure.png`
- subject_vs_drawing: `/home/claude/work/croquis/out/reviews/P4_structural_connections/pass_01/subject_vs_drawing.png`
- subject_split: `/home/claude/work/croquis/out/reviews/P4_structural_connections/pass_01/subject_split.png`
- subject_drawing_overlay: `/home/claude/work/croquis/out/reviews/P4_structural_connections/pass_01/subject_drawing_overlay.png`
- subject_drawing_absdiff: `/home/claude/work/croquis/out/reviews/P4_structural_connections/pass_01/subject_drawing_absdiff.png`
- grammar_vs_drawing: `/home/claude/work/croquis/out/reviews/P4_structural_connections/pass_01/grammar_vs_drawing.png`
- exemplar_vs_drawing: `/home/claude/work/croquis/out/reviews/P4_structural_connections/pass_01/grammar_vs_drawing.png`
- overview: `/home/claude/work/croquis/out/reviews/P4_structural_connections/pass_01/reference_authority_overview.png`
- three_way: `/home/claude/work/croquis/out/reviews/P4_structural_connections/pass_01/reference_authority_overview.png`

## Canvas-scale pencil guidance
- canvas: `512 × 768`
- recommended width multiplier: **1.033×**
- minimum visible opacity for this stage: **0.38**
- minimum visible pressure for this stage: **0.34**
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
