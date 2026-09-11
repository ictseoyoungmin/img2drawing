# img2drawing current status

Updated: 2026-09-11

```text
RELEASED STABLE:  v1.0.2 · DrawingSession/1.0.2-vnext · A10
MAIN:             post-v1.0.2 unreleased hardening; package version intentionally still 1.0.2
RUNTIME:          stage-free DrawingSession; R23 runtime/legacy namespace physically retired
INSTRUCTION GRAPH: path-consistent, dynamically reachability-verified, gesture mode split into pure/constructive
KNOWN OPEN DEFECT: inspect() ↔ final/replay pixel parity strict xfail
NEXT VALIDATION:  fresh-worker gesture dogfood, then render-input parity closure
NEXT RELEASE:     assign a new version only after post-v1.0.2 breaking changes are reviewed
```

## Current truth

- `v1.0.2` is the latest published immutable release.
- Current `main` contains unreleased changes after v1.0.2. Do not republish or mutate the v1.0.2 tag/freeze.
- The installable R23 compatibility namespace and the remaining R23 orchestration/runtime cluster have been removed from current `src`.
- Historical R23 evidence remains recoverable from Git history and the records under `dev/legacy/` and `dev/release/r23/`.
- New work uses one stage-free `DrawingSession` orchestration route.
- The deployable drawing authority is `skills/img2drawing/SKILL.md` plus `skills/img2drawing/references/`.
- `SKILL.md` routes with skill-root-relative `references/...` paths; `references/INDEX.md` routes with references-root-relative paths.
- `dev/tools/verify_instruction_graph.py` derives the graph from the actual `references/**/*.md` tree and rejects broken, orphaned, or bare routed Markdown paths.
- Gesture drawing has two explicit finish modes: pure gesture and constructive gesture. An unqualified gesture request defaults to constructive gesture.
- `finish()` requires a non-blank current drawing and a fresh inspection that the Agent explicitly recorded as read; accepted limitations cannot bypass an open residual.
- Residual correction provenance requires the repairing mutation to carry the residual observation id when the residual is resolved against that observation.
- Mechanical CI verifies repository/runtime/package/provenance contracts. It does not issue an artistic-quality verdict.

## Current source surface

The installable top-level implementation is intentionally narrow:

```text
img2drawing/
├── core/
├── data/
├── inspection/
├── observation/      # palette only
├── provenance/
├── render/
├── vnext/
├── __init__.py
└── _version.py
```

Retired from current `src`: `legacy/`, `run.py`, `stages/`, `exemplar/`, `review/`, historical `registration/`, `canvas/`, historical `reference/`, and non-palette R23 observation modules.

## Open work

1. **Fresh-worker gesture dogfood** — verify that `gesture drawing` now reaches constructive gesture completion rather than stopping at a construction scaffold; separately verify explicit pure gesture.
2. **Render-input parity** — close the strict xfail where `inspect()` and final/replay differ by a few luminance levels because stage compatibility metadata affects hand-dynamics seeding.
3. **Release/version closure** — after the two items above, decide the next version for the compatibility-breaking post-v1.0.2 main state and create a new freeze instead of editing the v1.0.2 freeze.
4. **Root compatibility shims** — deprecated pre-0.6.0rc2 root aliases remain intentionally supported for now; remove them only in a separately versioned compatibility cleanup.

## Historical boundaries

The following are history/evidence, not current planning authority:

- `docs/releases/v1.0.0.md`, `v1.0.1.md`, `v1.0.2.md`;
- closed A/B slice, capsule, baseline, and audit documents under this planning tree;
- benchmark reports tied to earlier versions;
- `dev/release/vnext/CONTRACT_FREEZE.json`, which is the immutable v1.0.2/A10 release snapshot even though current main has moved on.

## Authority map

- current repository truth: actual `main` + this file;
- deployable drawing behavior: `skills/img2drawing/SKILL.md` + `skills/img2drawing/references/`;
- released stable notes: `docs/releases/v1.0.2.md`;
- unreleased public changes and known issues: `CHANGELOG.md`;
- current near-term sequence: `ROADMAP.md`;
- immutable v1.0.2 contract snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`;
- R23 retirement audit: `dev/release/vnext/SRC_LEGACY_AUDIT_2026-09-09.md`.
