# Gates: img2drawing current program

This file tracks **current** project gates only. Historical R21/R23 gate evidence remains in
`dev/release/`, `dev/evidence/`, `dev/planning/`, and Git history; it must not be mistaken for
the current control plane.

## G0 — Repository truth is singular

- [x] `HANDOFF.md`, `STATUS.md`, `ROADMAP.md`, `VALIDATION_RELEASE.md`, package notes, and the changelog describe the same current route.
- [x] deployable skill guidance starts at `skills/img2drawing/SKILL.md`.
- [x] `skills/img2drawing/examples/` is absent until a genuinely representative example exists.
- [x] frozen vNext contract is referenced at `dev/release/vnext/CONTRACT_FREEZE.json`, not from the deployable skill root.

## G1 — Deployable instruction surface is clean

- [x] `SKILL.md` is an instruction router, not a development log.
- [x] references use the stage-free graph: foundation → modes → observation → construction → description → subject leaves → review/output/API.
- [x] croquis guidance preserves observed geometry while economizing marks.
- [x] drawing guidance does not require private/internal runtime implementation knowledge.

Mechanical verification is owned by `dev/tests/test_skill_surface_boundary.py` and the B17/B18 verifiers.

## G2 — Public API mental model is narrow

- [x] root exports are audited against the intended normal-user route centered on `DrawingSession`.
- [x] package-root discovery exposes only high-level session/declarative/construction facade names.
- [x] low-level history/action, schema, inspection, evidence, and advanced record capability remains in explicit owning namespaces.
- [x] pre-rc2 direct root imports remain available through deprecated lazy shims instead of abrupt breakage.
- [x] `0.6.0rc2` + the A2-aligned contract snapshot freeze the narrowed root.

Evidence: `dev/planning/vnext/A2_PUBLIC_ROOT_API_AUDIT.md`, `dev/tests/test_vnext_package_contract.py`, and `dev/release/vnext/SUPPORT.md`.

## G3 — Runtime physical isolation matches the stage-free product model

- [x] inventory/classification covers historical `run`, `stages`, `exemplar`, `review`, and `registration` plus current `vnext/core/inspection/render` ownership.
- [x] canonical `DrawingSession` import/resolution does not activate the historical R23 orchestration cluster.
- [x] `img2drawing.inspection` owns current stage-free registration/measurement; historical `img2drawing.registration` is compatibility implementation.
- [x] instruction-graph `review` is distinguished from the historical Python `img2drawing.review` package.
- [x] `img2drawing.legacy.r23` remains lazy until a caller explicitly requests historical orchestration.
- [x] physical rename/deletion is deferred to R03 as a compatibility-window decision.

Evidence: `dev/planning/vnext/A3_RUNTIME_PHYSICAL_ISOLATION_AUDIT.md` and `dev/tests/test_runtime_physical_isolation.py`.

## G4 — Instruction routing and high-value guidance are operational

- [x] common residuals route explicitly to the smallest responsible leaf and upstream construction/observation/contact/environment premises when the local part is only a symptom.
- [x] local hands/grip have focused guidance that preserves hand envelope, thumb/finger grouping, visible terminations, and real contact without mitten completion or invented hidden digits.
- [x] foreshortening/depth has a construction owner for projected spacing, near/far order, overlap, hidden length, and terminal orientation without anatomical unfolding.
- [x] the graph remains progressive-disclosure: `INDEX.md` stays compact and delegates conditional diagnostics to `review/residual-routing.md`.

Evidence: `dev/planning/vnext/A4_RESIDUAL_ROUTING_HARDENING.md`, `dev/planning/vnext/A5_DRAWING_LEAF_GAP_HARDENING.md`, and `dev/tests/test_skill_surface_boundary.py`.

## G5 — Fresh integrated validation — NEXT

- [ ] D01 difficult observed croquis.
- [ ] D02 observed figure / subject recognition.
- [ ] D03 tonal study.
- [ ] D04 observed free-draw.
- [ ] D05 imaginative + hybrid.
- [ ] D06 cross-agent reproducibility.

`dev/planning/vnext/VALIDATION_RELEASE.md` owns these contracts. No D-case is considered passed by mechanical CI alone.

## G6 — Release hardening

- [ ] R01 consolidate repeated evidence-backed fixes.
- [ ] R02 final representative regression.
- [ ] R03 physical R23 retirement / bounded compatibility decision.
- [ ] R04 release with claims limited to demonstrated evidence.

## Current stopping rule

Work on the highest-impact open gate in order unless new evidence disproves an earlier closed premise. Reopen the responsible gate narrowly instead of adding a workaround or a second workflow.
