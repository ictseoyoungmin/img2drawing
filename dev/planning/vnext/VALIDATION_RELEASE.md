# img2drawing validation and release hardening

Updated: 2026-09-11

This document is the current validation matrix for unreleased post-v1.0.2 main. It no longer owns
R23 retirement; that work is already complete in current `src`. Historical D01–D06/R01–R04 plans
remain visible in Git history and closed planning records but are not current sequencing authority.

## Governing rule

```text
fresh evidence
→ identify highest-impact reusable defect
→ reopen the responsible premise narrowly
→ correct
→ rerun affected validation
→ full regression
→ choose version / create new freeze
→ publish
```

Dogfood validates the existing product; it must not create subject-specific runtime branches,
worker-specific answer paths, or a second drawing workflow.

## V01 — Gesture mode behavior

Run two fresh-worker cases with the current installed skill:

1. **pure gesture** — explicitly quick/pure/line-of-action request;
2. **constructive gesture** — unqualified `gesture drawing` request.

Pure gesture may be sparse but must still communicate the whole pose: head direction,
torso/pelvis relation, major visible limb chains, support, and decisive negative spaces.
Constructive gesture adds occupied masses, orientation, joint anchors, width/overlap/contact, and
must not stop at an isolated construction scaffold.

If the request says to start with gesture and continue to a fuller drawing, gesture is only an
intermediate pass and the larger requested mode owns completion.

## V02 — Render-input parity

Close the strict inspection/final parity xfail while preserving canonical replay and fast replay
exactness. Validate:

- `inspect()` and `render_final()` pixel parity for identical authored state/profile;
- canonical replay final == final PNG;
- fast timelapse final == canonical final for eligible histories;
- custom persisted `RenderProfile` values remain authoritative;
- output-scale handling does not corrupt canvas-space inspection geometry.

The correction must normalize the shared render input rather than alter only one output path.

## V03 — Fresh observed subject

After V01/V02, run at least one fresh difficult observed drawing without prior answer geometry.
Review whole-subject structure before local description and verify cause-based residual routing,
observation-id correction provenance, stroke retirement, finish evidence-read requirements, and
end-to-end replay.

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

## Release hardening

After the targeted open defects are closed:

1. review compatibility impact of all post-v1.0.2 changes;
2. select a new version; never republish the mutable main state as v1.0.2;
3. create a new immutable contract freeze instead of modifying `v1.0.2-A10`;
4. run active tests, current-runtime isolation, dynamic instruction-graph reachability,
   package/wheel/sdist/clean-install verification, replay/timelapse exactness, and historical
   release evidence checks;
5. ensure README, changelog, support/migration policy, package metadata, release notes, manifest,
   and CI all describe the same version and compatibility boundary;
6. publish only from an explicit new release manifest.

Release claims may include only behavior actually demonstrated by the corresponding evidence.
