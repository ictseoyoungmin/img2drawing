# S04 residual ownership — S03.1 Gojo classification

Status: **ACTIVE / S03.1 CLASSIFIED / GLOBAL S04 OPEN**  
Date: 2026-09-15  
Input evidence: `dev/dogfood/s03-quality-gates/strong-perspective-close/review.md`  
Source merge: PR #51 / `0fb33287be165edd3326500caad7f44a8c2e266b`

This record owns the S04 classification for the first completed dogfood class. It does not close
S04 globally because S03.2–S03.4 have not yet produced evidence.

## Decision for this batch

```text
renderer-eligible blocking defects: 0
proven renderer-owned defects:       0
instruction/geometry blockers:       3
provenance/evidence blocker:         1 package-level case
```

No current-v11 pixel change is justified by this batch.

## Residual ledger

### R1 — supplied identity/style replaced by a remembered or alternate design

- symptom: the worker intentionally substituted identity/styling instead of preserving the supplied reference instance;
- visible evidence: the produced head/hair/garment language diverges from the supplied instance for reasons unrelated to observed geometry;
- responsible owner: **observation evidence / subject-specific geometry / completion decision**;
- parent premise: a familiar or named subject may be redrawn from memory when the worker considers another design more canonical or permissible;
- geometry correct: **no**;
- material/render behavior correct: **not relevant to cause**;
- renderer eligible: **no**;
- next disproof test: fresh rerun must treat the supplied instance as authority for visible identity-bearing geometry and must surface any external limitation instead of silently substituting a different design.

Routing consequence: reopen the instruction owner through `foundation/reference-authority.md`,
`figure/head-face-hair.md`, `review/visual-quality-gates.md`, and `review/completion.md`.

### R2 — visible projected hand normalized toward expected anatomy

- symptom: the worker judged the reference hand/chirality as implausible and changed the result toward expected anatomy;
- visible evidence: terminal orientation/grouping was corrected according to anatomical expectation rather than the readable projected silhouette/overlap;
- responsible owner: **observation evidence / construction-proportion-perspective / subject-specific geometry**;
- parent premise: anatomy plausibility may overrule a coherent visible projection;
- geometry correct: **no**;
- material/render behavior correct: **not relevant to cause**;
- renderer eligible: **no**;
- next disproof test: freeze the same reference crop, compare wrist entry, palm envelope, overlap, negative space, and terminal orientation, and require a fresh worker to preserve the coherent image-space projection even when it appears anatomically surprising.

Routing consequence: reopen `observation/visual-observation.md`,
`construction/foreshortening-and-depth.md`, `figure/hands-and-grip.md`, and the central visual gate.

### R3 — symbolic geometry and search construction survive finish

- symptom: one worker collapses hair into radial/starburst strokes, reduces body/hand forms toward generic primitives, and leaves scaffold/search marks visible at finish;
- visible evidence: category recognition survives while instance-specific mass/clump, perspective, terminal, and retirement decisions do not;
- responsible owner: **subject-specific geometry / mark-language selection / completion-retirement decision**;
- parent premise: recognizability plus local detail is sufficient to finish despite symbolic construction and unresolved search marks;
- geometry correct: **no**;
- material/render behavior correct: **uncertain but not eligible while geometry is wrong**;
- renderer eligible: **no**;
- next disproof test: fresh rerun must pass anti-symbol, hierarchy, and KEEP/SOFTEN/RETIRE gates before finish.

Routing consequence: current anti-symbol/retirement gates remain the owner. Do not escalate this
residual to renderer/material while authored geometry and finish decisions can explain it.

## Evidence-validity note — reconstructed Astra history

The visually strongest supplied result is useful qualitative evidence but its package states that
lost edit/deletion history was reconstructed from final visible coordinates. That is an evidence
validity problem, not a renderer defect and not proof that its visual geometry is wrong.

It remains ineligible to establish S03 PASS until a fresh canonical action-0→latest history exists.
Do not convert missing provenance into a visual residual or hide it as an accepted limitation.

## S04.2 geometry-first elimination result

All three visual blockers fail renderer eligibility because changing reference interpretation,
authored points, terminal orientation, semantic ownership, or retirement decisions can plausibly
repair them.

```text
R1 → authored identity/geometry changes are required      → not renderer-owned
R2 → authored projected hand geometry changes are required → not renderer-owned
R3 → authored geometry/retirement changes are required    → not renderer-owned
```

No minimal renderer reproduction is authorized from this evidence.

## Upstream reopen

The S03.1 dogfood disproves one assumption in the previously closed instruction slice: stating that
the subject is the geometry authority is not sufficient if a worker can still treat plausibility or
remembered identity as an implicit higher authority during correction.

The bounded reopen is therefore:

- explicit visible-projection-over-normalization rule in reference authority;
- plausibility-conflict observation procedure;
- hand and foreshortening anti-normalization rule;
- supplied-instance-over-remembered-identity rule for head/face/hair;
- central reference-fidelity gate;
- authority-drift rejection in residual correction and completion.

This reopen does **not** authorize a new runtime stage, renderer generation, package version, or
pixel change.

## S04 global state

S04 remains open until the remaining S03 classes are executed and their blocking/repeated residuals
are classified. For the current S03.1 batch the provisional decision is:

```text
A. no renderer-owned blocking defect in this batch
```

If S03.2–S03.4 later produce a geometry-correct material failure, that candidate must still satisfy
the separate real-drawing + minimal-controlled-reproduction rule before any S06 slice exists.
