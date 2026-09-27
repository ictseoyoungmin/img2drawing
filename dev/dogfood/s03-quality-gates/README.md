# S03 fresh-worker visual-quality dogfood

Status: **PASS / USER_ACCEPTED**
Baseline: `main` after PR #49 (`c10e3f36a3347dad3195e450bd2bb3be89c3095f`)  
Renderer family under observation: `pillow-pencil-contact-v11 / 1`  
Package identity: unchanged from published `v1.0.3 / A14`

The current user-directed still-life campaign is defined in
[`SIMPLE_SUBJECT_CAMPAIGN.md`](SIMPLE_SUBJECT_CAMPAIGN.md). It supersedes both the original Gojo
rerun and the figure-based pilot; those outputs remain historical and do not count as class-level PASS evidence. The user accepted the dogfood release gate on 2026-09-27 in [`USER_ACCEPTANCE_2026-09-27.md`](USER_ACCEPTANCE_2026-09-27.md).

This directory owns S03 of `dev/planning/vnext/V11_QUALITY_CONTROL_SLICE_PLAN.md`.

S03 does not change renderer pixels. Its purpose is to determine whether the new instruction execution gates actually alter fresh-worker drawing behavior and to produce evidence precise enough for S04 to distinguish authoring/geometry failures from renderer/material failures.

## Fresh-worker rule

A valid S03 worker receives:

- the current skill and normal public runtime surface;
- the target reference needed for its class;
- the ordinary user request for the drawing task.

It must **not** receive prior solution strokes, a corrected session, hidden answer geometry, or the four failure outputs as a tracing/template source. Those failure outputs define the failure taxonomy only.

Fixed source references may be generated as raster or vector targets. The current references are original SVG compositions rendered to PNG because the image_gen service returned a usage-limit error. Image generation, SVG/canvas tracing, pixel paste, edge-trace paste, and raster repair remain prohibited for img2drawing drawing output.

## Required classes

| ID | Class | State |
| --- | --- | --- |
| S03.1 | apple still life | `NOT_RUN` |
| S03.2 | ceramic mug still life | `NOT_RUN` |
| S03.3 | closed umbrella still life | `NOT_RUN` |
| S03.4 | potted plant still life | `NOT_RUN` |

A class may become `PASS`, `BLOCKED`, or remain `NOT_RUN`. There is no averaged S03 score. One blocking class keeps S03 open.

The class README owns the state declaration. Once a class changes from `NOT_RUN` to `PASS` or `BLOCKED`, that class directory must also contain a completed `review.md` based on `REVIEW_TEMPLATE.md`. CI verifies artifact paths and SHA-256 values, residual ownership, retirement audit, and a verdict matching the README state. `PASS` additionally requires verified fresh-worker provenance. A `BLOCKED` review may truthfully record `no` or `unverified` freshness when provenance itself is part of the blocker; uncertain provenance can never be upgraded into PASS.

## Per-run evidence contract

Every executed class must preserve or identify all of the following:

1. reference identifier/source and enough information to recover the exact visual authority;
2. worker identity/configuration when available, plus confirmation that it was fresh with respect to solution strokes;
3. complete canonical `session.json` from action 0 through the latest accepted action;
4. final PNG rendered from that canonical session;
5. end-to-end GIF from action 0 through latest, normally `every_n=4`, using the same pencil renderer family as the PNG;
6. reference/final comparison board or equivalent inspectable comparison evidence;
7. top three remaining visible residuals, or an explicit statement that fewer than three remain;
8. for each residual: blocking yes/no, responsible owner, visible evidence, and accepted-limitation rationale when non-blocking;
9. KEEP / SOFTEN / RETIRE audit for surviving provisional/construction marks;
10. final verdict: `PASS` or `BLOCKED` with the exact reason.

If binary review artifacts are not committed, the review record must contain stable filenames plus SHA-256 values. Missing artifacts are not equivalent to PASS.

## Shared visual gates

Every class is reviewed at whole-drawing scale and at the relevant local crop against these questions:

- **whole read:** did the drawing become more subject-specific, or merely busier?
- **perspective:** does depth propagate through connected body/object chains rather than appearing in one local mass only?
- **ownership:** does each surviving final stroke belong to a continuous physical/semantic relation?
- **anti-symbol:** are visible-enough forms observed rather than replaced by circles, rails, capsules, wedges, icon features, or generic prop primitives?
- **silhouette/overlap/contact:** are near/far order and attachment relations coherent?
- **head/face/hair:** does head orientation control features and does hair read mass → clump → selected accent?
- **limbs/hands/feet:** do taper, joint insertion, rotation, foreshortening, and terminal orientation survive where visible?
- **props:** are object axis/thickness/contact/negative spaces solved with the body rather than beside it?
- **clothing:** do folds/hatches have observable force/contact/material causes rather than decorative repetition?
- **environment:** do context marks have visible plane/edge owners rather than generic perspective decoration?
- **hierarchy:** do primary, secondary, and tertiary marks actually read differently at final presentation scale?
- **retirement:** have replaced/contradicted search marks been retired rather than merely made faint?

## Geometry vs material boundary

S03 records symptoms; S04 assigns the owner.

A worker or reviewer must not call a renderer defect merely because a line looks ugly.

```text
path / proportion / ownership / overlap / contact can plausibly fix it
→ geometry/instruction candidate

geometry is held correct, but weight / taper / terminal / grain / deposition still fails
→ renderer/material candidate for S04 reproduction
```

No current-v11 pixel change is authorized from S03 evidence alone.

## Directory layout

```text
s03-quality-gates/
├─ README.md
├─ REVIEW_TEMPLATE.md
├─ strong-perspective-close/
│  ├─ README.md
│  └─ review.md               # required once executed
├─ fullbody-3q-prop/
│  ├─ README.md
│  └─ review.md               # required once executed
├─ frontal-fullbody/
│  ├─ README.md
│  └─ review.md               # required once executed
└─ head-hair-closeup/
   ├─ README.md
   └─ review.md               # required once executed
```

Each class README is an evidence ledger, not an answer template. Replace `NOT_RUN` only when a real run or a truthfully provenance-blocked dogfood package exists.

## Mechanical harness gate

`python dev/tools/verify_s03_quality_gate_harness.py` verifies the class/state surface. `NOT_RUN` is valid while no run exists. `PASS` or `BLOCKED` requires a concrete `review.md` with the review contract above; class PASS is stricter and requires verified freshness. Ordinary evidence closure requires all four classes PASS and `Status: **PASS / CLOSED**`. The separate `PASS / USER_ACCEPTED` gate requires the dated acceptance record and leaves unfinished class ledgers truthful.

## Closure

The ordinary evidence route closes S03 only when all four class ledgers contain reviewable real evidence and none has an unresolved blocking failure. The current release gate was accepted by the user with incomplete class evidence; this decision closes the gate for this release scope without a measured visual-quality claim. Any later class-level PASS still requires the full evidence contract.
