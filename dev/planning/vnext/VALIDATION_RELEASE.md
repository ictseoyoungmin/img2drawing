# img2drawing validation and release hardening

Updated: 2026-09-13

This document is the current validation matrix for work **after the published v1.0.3 baseline**. It does not own historical R23 retirement or the already-closed v1.0.3 release cycle. Historical D01–D06/R01–R04 plans remain visible in Git history and closed planning records but are not current sequencing authority.

## Governing rule

```text
fresh evidence
→ identify highest-impact reusable defect
→ reopen the responsible premise narrowly
→ correct
→ rerun affected validation
→ full regression
→ choose version / create new freeze only when needed
→ publish only through an explicit manifest
```

Dogfood validates the existing product; it must not create subject-specific runtime branches,
worker-specific answer paths, or a second drawing workflow.

## Sealed-input assets

When a reproducible sealed run is useful, reuse `dev/dogfood/vnext-template/` and the current
schemas rather than inventing a task-local protocol.

Release comparison authority is versioned:

- `dev/release/vnext/CONTRACT_FREEZE.json` — immutable v1.0.2/A10 snapshot;
- `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json` — immutable v1.0.3/A14 snapshot.

Current validation compares future `main` changes against the relevant released baseline and the
current `STATUS.md` / `CHANGELOG.md` state; it does not rewrite old freezes.

## V01 — Gesture mode behavior — CLOSED for v1.0.3

The v1.0.3 cycle exercised two fresh-worker cases:

1. **pure gesture** — explicitly quick/pure/line-of-action request;
2. **constructive gesture** — unqualified `gesture drawing` request.

The cycle found and closed runtime-mode, primitive-shape, anti-blob, and semantic-mark/tool-adapter
integration gaps. Evidence is `dev/dogfood/g01-gesture-rc2/README.md`.

The durable contract remains:

- pure gesture may be sparse but must communicate the whole pose: head direction, torso/pelvis relation, major visible limb chains, support, and decisive negative spaces;
- constructive gesture adds occupied masses, orientation, joint anchors, width/overlap/contact, and must not stop at an isolated construction scaffold;
- if a request says to start with gesture and continue to a fuller drawing, gesture is only an intermediate pass and the larger requested mode owns completion.

## V02 — Render-input parity — CLOSED for v1.0.3

The strict inspection/final seed-parity gap was closed during the v1.0.3 RC cycle while preserving historical replay semantics.

Current regression authority verifies:

- `inspect()` and `render_final()` parity for identical authored state/profile where required;
- canonical replay final == final PNG;
- eligible fast timelapse final == canonical final;
- custom persisted `RenderProfile` values remain authoritative;
- output-scale handling does not corrupt canvas-space inspection geometry;
- explicit v9/v10 replay remains available after v11 becomes current.

The correction normalized shared render input rather than patching only one output path.

## V03 — Fresh observed subject — AVAILABLE, NOT ACTIVE

A fresh difficult observed drawing without prior answer geometry is the next reusable validation
slice **if it is explicitly selected as the highest-impact bottleneck**. It is not automatically
authorized merely because v1.0.3 is closed.

If selected, review whole-subject structure before local description and verify cause-based residual
routing, observation-id correction provenance, stroke retirement, finish evidence-read requirements,
and end-to-end replay.

A lower-quality result is not automatically a skill defect. Separate worker visual-reasoning limits
from reusable instruction/runtime friction before changing the product.

## V04 — Optional broader matrix

Run only when broader claims are needed:

- observed figure / subject recognition;
- tonal study;
- observed free-draw;
- imaginative and hybrid authority;
- cross-agent comparison.

These are evidence expansions, not mandatory prerequisites for every patch release unless the
release claims depend on them.

## Evidence policy

Preserve enough to reproduce and review a meaningful run:

- sealed input/reference and user request;
- intent and render profile;
- canonical session/checkpoint;
- representative inspections and residual/correction decisions;
- final PNG;
- end-to-end replay/timelapse;
- accepted limitations and cost/action summary.

Do not pass hidden answer images, authored coordinate tables, previous sessions, evaluator
rationales, or task-specific solution scripts to a fresh worker.

## Release hardening for future versions

After a future targeted defect or capability slice is selected and closed:

1. review compatibility impact relative to the latest published stable;
2. select a new version only when release-worthy changes exist; never mutate or republish an existing immutable tag;
3. create a new immutable contract freeze instead of modifying v1.0.2/A10 or v1.0.3/A14;
4. run active tests, current-runtime isolation, dynamic instruction-graph reachability, package/wheel/sdist/clean-install verification, replay/timelapse exactness, and historical release evidence checks;
5. ensure README, changelog, package metadata, release notes, manifest, planning state, and CI describe the same version and compatibility boundary;
6. publish only from an explicit new release manifest.

Release claims may include only behavior actually demonstrated by the corresponding evidence.
