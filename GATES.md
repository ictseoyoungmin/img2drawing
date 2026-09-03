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
- [x] package-root discovery now exposes only high-level session/declarative/construction facade names.
- [x] low-level history/action, schema, inspection, evidence, and advanced record capability remains in explicit owning namespaces.
- [x] pre-rc2 direct root imports remain available through deprecated lazy shims instead of becoming abrupt breakage.
- [x] `0.6.0rc2` + the A2-aligned contract snapshot mechanically freeze the narrowed root.

Evidence: `dev/planning/vnext/A2_PUBLIC_ROOT_API_AUDIT.md`, `dev/tests/test_vnext_package_contract.py`, and `dev/release/vnext/SUPPORT.md`.

## G3 — Runtime physical isolation matches the stage-free product model

- [ ] inventory stage-era/current-path packages (`stages`, exemplar/review-era modules, compatibility shims, and related exports).
- [ ] classify each as shared capability, explicit compatibility, current implementation, or retire/archive candidate.
- [ ] ensure normal canonical imports do not depend on stage lifecycle machinery.
- [ ] do not delete compatibility merely for cosmetic cleanliness; migration/support evidence governs removal.

## G4 — Instruction routing is operational, not only taxonomic

- [ ] make residual → responsible leaf → upstream escalation edges explicit for common failure classes.
- [ ] harden remaining high-value drawing gaps such as hands/grip and foreshortening when evidence supports a separate leaf.
- [ ] keep the graph progressive-disclosure: workers should not need to read the entire reference tree.

## G5 — Fresh integrated validation

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
