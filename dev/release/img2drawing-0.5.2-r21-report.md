# img2drawing 0.5.2 — R21 Fresh-worker Defect Closure + Subject-only Default

## Closure state

- R20 fresh-worker autonomy / P1→P5 E2E: **CLOSED**
- R20 runtime/package defects: **CLOSED by R21**
- R21: **CLOSED**

## Important finding about the R20 dogfood

The R20 fresh-worker run already used the ordinary **subject-only** path.

Its checkpoint records:
- `task_stage_targets = {}`
- every P1→P5 review has `task_stage_target = null`
- authority order at every stage is:
  `subject_reference > grammar_exemplar`

Therefore the stage images visible to the worker were **not same-subject answer
drawings**. They were generic grammar exemplars plus the worker's own rendered review
artifacts.

The fresh worker still produced:
- P1: REVISE → ADVANCE
- P2: ADVANCE
- P3: REVISE → ADVANCE
- P4: REVISE → ADVANCE
- P5: REVISE → REVISE → ADVANCE

Mechanical fresh-worker audit: PASS.

## Subject-only default architecture

Same-subject P1/P2/P3/P4/P5 target images are not required.

At each stage the worker constructs a contract-constrained visual hypothesis from:

`subject geometry truth + StageContract + generic grammar + verified prior stage`

The grammar exemplar controls only representation vocabulary, stroke economy, line
hierarchy and detail ceiling. It must not provide current-subject pose, coordinates,
proportions or perspective.

The subject-only review evidence remains strong:
- subject vs current drawing;
- split comparison;
- registered overlay and raw difference;
- Agent-selected local crops;
- current StageContract;
- prior-stage structural state;
- generic grammar-vs-drawing representation review.

If a caller explicitly supplies a same-subject stage target, the stage changes to
`task_stage_target_augmented` mode. This remains optional evidence rather than a
dependency.

## R20 defects closed in R21

### 1. Version / provenance authority
Added one `_version.py` source of truth. Runtime checkpoint, review/session metadata,
public API ID and release slice now derive from current R21 constants. Stale
`dev13`, `DrawingRun/0.5.2-r13`, and R13 slice strings were removed from operational
runtime code.

### 2. Interruption durability
R21 atomically checkpoints after successful:
- stage start;
- `draw`;
- `draw_many`;
- `prepare_stage_review`;
- submitted review.

Checkpoints are fsynced to a temporary sibling and atomically replaced. The exact R20
failure mode — correction after a prepared review followed by resume — has a regression
test and now preserves the correction.

### 3. Scalar review finding serialization
Review findings now normalize a scalar string to one item. A string can no longer be
serialized as a list of individual characters.

### 4. Current documentation / benchmark
- QUICKSTART updated to R21.
- canonical subject-only benchmark renamed to
  `full_body_croquis_subject_only`.
- benchmark explicitly covers P1→P5.
- benchmark contains only `subject.png`, metadata and smoke runner — no same-subject
  stage target drawings.
- added `playbooks/subject-only-stage-derivation.md`.

### 5. Skill-only package boundary
Fresh-worker audit tooling now lives inside the canonical skill folder:
`img2drawing/tools/audit_fresh_worker.py`.

The R21 distribution ZIP contains only the `img2drawing/` skill folder.

## Validation

- `R21_DEFECT_CLOSURE_PASS 0.5.2.dev21`
- `FRESH_WORKER_READINESS_PASS 0.5.2.dev21 R21`
- R19 silhouette-separation regression: PASS
- subject-only benchmark smoke: PASS
- R20 returned fresh-worker mechanical audit: PASS
- full unit suite: **29 passed**
- wheel build: PASS
- clean wheel install/import: PASS
- clean installed subject-only/create/checkpoint smoke: PASS
- skill-only ZIP integrity: PASS

The full historical integration matrix was not re-run.

## Verdict

**R21 CLOSED.**

img2drawing no longer relies on same-subject intermediate target drawings. The ordinary
mode is explicitly subject-only, while optional same-subject stage targets remain an
augmentation when a user actually has them.
