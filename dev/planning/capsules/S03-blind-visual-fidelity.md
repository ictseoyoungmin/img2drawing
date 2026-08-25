# Context capsule — S03 Blind Visual Fidelity + P3 Dual Gate

Status: `CLOSED`

Implementation commit: `26a222d` (`feat: add P3 blind fidelity dual gate`)

## Responsibility

Make P3 advancement depend on two independent closures: the existing mechanical
StageContract/process review and a fresh subject-fidelity review over all eight
required regions. S03 consumes S01's frozen observation digest and S02's region
evidence; it does not alter non-P3 stage progression.

## Public surface

- `RegionClosureEntry` records fresh subject/drawing findings, evidence refs,
  `closed/revise/accept-with-rationale`, blocker, and rationale basis.
- `RegionClosureManifest` enforces exactly `head_hair`, `torso_orientation`,
  `near_arm`, `far_arm`, `pelvis`, `leg_A`, `leg_B`, and `attached_object`.
- `build_blind_visual_packet()` exposes only the frozen observation projection,
  stage contract, current drawing artifact, subject path, and evidence refs.
- `VisualFidelityReviewRecord` binds evaluator decision to manifest digest,
  drawing state/artifact/cursor, lock digest, and blind packet digest.
- `DrawingRun.submit_region_closure_manifest()` and
  `DrawingRun.submit_visual_fidelity_review()` persist the visual path.
- `DrawingRun.submit_stage_review(..., decision="advance")` enforces the P3
  process ∧ visual barrier.

## Inputs and outputs

Inputs are a current prepared P3 drawing artifact, frozen observation lock, eight
region entries, and an evaluator-authored visual finding. Outputs are
`blind_visual_packet.json`, `region_closure_manifest.json`,
`visual_fidelity_review.json`, checkpoint v3 fields, and review manifest v9
fields.

## Invariants

- Blind packet has no worker rationale, previous advance claim, or exemplar
  verdict fields.
- Every required region has fresh subject and drawing findings plus evidence.
- Missing region, blocker, `revise`, stale artifact/state/cursor, or lock mismatch
  prevents visual/P3 advance.
- `accept-with-rationale` is valid only with uncertainty or occlusion basis.
- Visual and process artifacts use the same state/artifact/cursor/lock digest.
- Non-P3 stages retain their existing review-to-advance path.

## Budgets and dependencies

- No CV, network, or new inference dependency; review records are small JSON.
- Checkpoint schema is v3 and review manifest schema is v9 because visual
  records are authoritative lifecycle state.
- Canonical implementation is `src/img2drawing/review/fidelity.py`; schemas are
  `region_closure.schema.json`, `visual_fidelity_review.schema.json`, and
  `blind_visual_packet.schema.json`.

## Evidence

- `dev/evidence/p3-fidelity/S03-blind-visual-fidelity/closure_report.md`
- `skills/img2drawing/tests/test_fidelity.py` (`22 passed` overall suite)
- subject-only benchmark smoke (`SUBJECT_ONLY_BENCHMARK_PASS`)

## Limitations and next integration

S03 does not generate region geometry itself, infer anatomy, or make an artistic
quality score. It accepts agent-authored findings and S02 evidence refs. S04
should clean the exemplar mandatory path while preserving the blind/process
separation; later region-specific slices should enrich the eight entries.

## Reopen conditions

Reopen S03 if any P3 path bypasses the dual barrier, blind packet gains hidden
worker rationale/exemplar verdict, visual artifacts become stale or unbound to
the lock, or non-P3 progression regresses. Otherwise activate S04 only after
this capsule and closure evidence are reviewed.
