# img2drawing vNext post-alignment validation and release

Updated: 2026-09-05
Starts only after: **B18 CLOSED + post-freeze alignment A1–A8 accepted**

This document owns the first fresh visual validation after implementation freeze and product-surface alignment. Earlier dogfoods remain historical or exploratory evidence; they do not substitute for D01–D06.

## Governing rule

```text
implementation freeze
→ repository/API/instruction alignment
→ fresh dogfood tries to break the product
→ responsible premise reopens
→ affected dogfood reruns
→ final regression
→ physical legacy retirement decision
→ release
```

Dogfood is validation, not a new architecture layer. A D-run never owns permanent runtime code or a second workflow.

Across all observed/hybrid D-cases, apply the A7 inheritance rule: early construction may defer
secondary detail but may not genericize the structural relations that define the subject. Before a
later descriptive pass inherits existing construction, compare the whole drawing against its
authority again. If the parent relation is wrong, replace the responsible geometry before adding
local contour, detail, value, or accents.

Also apply the A8 occlusion rule whenever an important relation disappears behind another form:

- measurement and visible evidence stop at the occluder;
- the Agent may infer the minimum hidden continuation needed for continuity, pose, topology,
  contact, depth, or a downstream visible anchor;
- the inference remains provisional and lower-authority than visible anchors;
- exact hidden appearance is not fabricated from category knowledge;
- final visible contour normally stops at the foreground occluder and resumes only at observed
  reappearance;
- when only one side is visible, uncertainty increases and the exact hidden terminal remains
  unspecified unless additional evidence supports it.

D-cases should reject both **under-inference** (treating structural continuity as termination at the
occluder) and **over-inference** (rendering unsupported hidden contour/detail as observed).

## Sealed input contract

The frozen machine-readable vNext baseline is `dev/release/vnext/CONTRACT_FREEZE.json`.

Start each case from `dev/dogfood/vnext-template/` and the current schemas under `dev/schemas/`, bind the final input digest before dispatch, and do not edit a sealed input to accommodate a worker.

Fresh workers may receive only:

- installed/current skill and package;
- fresh subject/reference when the mode requires one;
- the user request;
- declared/inferred `DrawingIntent`;
- ordinary documented runtime/output paths.

Do not provide:

- answer image / ideal-stroke reference;
- authored coordinates or landmark tables;
- previous session/action IDs;
- previous residual priorities or evaluator verdicts;
- Pn/R23 worker packets;
- subject-specific helper scripts that encode the solution;
- uncurated examples as hidden answer templates.

The deployable skill currently contains no `examples/` directory by design.

## D01 — Difficult observed croquis

Intent baseline:

```text
observed · croquis · pose · pencil_loose
```

Primary proof:

- gesture / line of action;
- balance/support/stance;
- head/ribcage/pelvis placement, orientation, and relative twist;
- shoulder/pelvis counter-relation and near/far side read;
- major limb anchor chains and foot orientation;
- large negative spaces;
- silhouette / overlap / prop-body depth and contact;
- geometry-preserving line economy;
- early sparse construction remains structurally specific rather than symbolic;
- later description replaces disproven parent geometry instead of polishing around it;
- important occluded chains/parts/contacts retain plausible hidden continuity when needed without
  rendering unsupported hidden appearance.

D01 should be judged first from a line-dominant structural read. Broad value or dense regular
hatch must not be needed to make the pose convincing. If tone is used at all, mentally remove it
and verify that major mass turn, support, limb chains, negative spaces, and prop/body overlap still
read correctly.

For every material occlusion, inspect the visible entry/reappearance anchors when available. A
worker should not claim success merely because the final contour correctly stops at the occluder;
the visible downstream relation must also remain coherent with a plausible hidden continuation.
Conversely, a plausible hidden continuation does not justify drawing through the occluder.

Reject a result that uses fewer lines by reducing the subject to symbolic head/limb/foot/fold shapes, or that cleans local contours while making the whole pose more frontal, parallel, symmetric, or otherwise more generic than the reference. Also reject results that either sever important structural continuity at occluders or visibly complete unsupported hidden contour/detail. Cost and fidelity are both first-class:

1. **record cost** — the session must not regress to brute-force microstroke explosion;
2. **representation quality** — major form, orientation/twist, overlap, contact, characteristic curvature, structural specificity, and required occluded continuity must remain coherent with sparse marks.

Likely reopen mapping:

- observation/boundary failure → B01-R1/B02+B03 or A4/A6 guidance routing;
- whole-pose flattening / turn-twist failure → A6 first; B05 only if runtime construction capability is actually limiting;
- early generic-symbol construction or downstream inheritance of a disproven parent premise → A7 first;
- hidden relation treated as structural termination, or unsupported hidden appearance rendered as observed → A8 first;
- construction/form failure → B05;
- correction/provenance failure → B06;
- evidence budget failure → B07;
- value/representation-cost failure → B07-R1/B16, after confirming A6/A7/A8 structure-first policy was followed;
- finish policy failure → B09;
- public-surface friction → A2/B16.

## D02 — Observed figure / subject recognition

Intent baseline:

```text
observed · figure_drawing · subject · graphite_academic
```

Requires D01 macro quality plus identity-bearing relationships:

- cranial/jaw silhouette and face orientation;
- eye spacing/direction and facial feature relations;
- hair envelope/groups/termination direction without strand-noise filling;
- hand/foot parent-chain/contact/visibility;
- distinctive clothing mass/openings/seams/folds at observed locations;
- prop topology/contact/terminal mass.

Do not pass because “eyes”, “hair”, “fingers”, or “folds” exist. Recognition must survive whole-image review and remain subordinate to correct macro form and spatial orientation. Identity-bearing local detail may not become an excuse to preserve a wrong parent construction. When identity-bearing parts are occluded, infer only the structural relation needed for the visible result; do not complete exact hidden fingers, hair tips, seams, or prop details from memory.

Likely reopen: B09/B10, upstream B05/B01-R1, or A4/A5/A6/A7/A8 when the issue is guidance coverage/routing rather than runtime mechanics.

## D03 — Tonal study

Intent baseline:

```text
observed · tonal_study · form_light · graphite_tonal
```

Primary proof:

- large light/shadow families;
- calibrated broad value regions;
- edge hierarchy and form turning;
- focal value control;
- compact value revision.

Reject arbitrary dark bands, dense authored hatch micro-actions for one value premise, tone that manufactures missing form, or a line drawing plus renderer/post-filter presented as tonal study. A value pass must revalidate the parent structural premise before inheriting it. Value may describe a visible occlusion edge but may not be used to imply exact hidden geometry unsupported by the reference.

Likely reopen: B07-R1, B09, B11, B14, B15; A6 if value is compensating for weak orientation rather than describing a credible form; A7 if value is preserving an earlier generic or disproven construction; A8 if tone is concealing or fabricating an occluded relation.

## D04 — Observed free-draw

Intent example:

```text
observed · free_draw · expressive · custom/preset
```

Prove that reference truth can coexist with intentional composition, simplification, rhythm, focal hierarchy, and style without forcing figure/croquis grammar. Preserved reference constraints must remain explicit and the correction loop must remain meaningful under looser grammar. Simplification may reduce marks but may not silently replace structurally specific relationships with generic symbols. Stylization may omit hidden construction from the visible drawing while still reasoning through materially important occlusions.

Likely reopen: B13–B16, A7, or A8 when simplification/inheritance/occlusion policy is the actual failure.

## D05 — Imaginative + hybrid

Run separately.

### D05-A imaginative

No external subject. Authority is declared subject/composition/gesture/rhythm/focal/shape-language intent. Prove subjectless create/inspect/correct/finish/replay without fake reference or overlay authority. Construction remains provisional against declared intent just as observed construction remains provisional against a reference. Occluded structure may be authored as part of the declared design, but it must remain internally coherent with the chosen visible overlaps.

### D05-B hybrid

Use a reference plus explicit transformation intent. Provenance must distinguish preserved from transformed constraints; style may not silently sacrifice preserved geometry. Downstream description must revalidate both preserved reference constraints and transformed authored constraints before inheriting a parent premise. For preserved reference occlusions, A8 still separates observed evidence from inferred hidden structure.

Likely reopen: B13–B16, B10, A7, or A8 when the failure is construction inheritance/occlusion reasoning rather than runtime authority mechanics.

## D06 — Cross-agent reproducibility

Use at least two independent fresh workers on the same sealed input contract. Identical strokes are not required.

Compare:

- observation quality;
- whole-pose orientation/twist read;
- structural specificity of early sparse construction;
- whether downstream passes revalidate or blindly inherit parent geometry;
- whether important occlusions are under-inferred, appropriately inferred, or over-invented;
- whether hidden inference remains distinct from measured evidence and final visible contour;
- highest-impact residual prioritization;
- escalation to the correct instruction leaf/premise;
- edit strategy;
- final visual quality;
- evidence/read cost;
- session/action cost;
- failure modes;
- Pn/legacy leakage on the canonical route.

Instruction changes are justified only by repeated divergence. Do not claim statistical generality from two workers.

## Evidence policy for D01–D06

Preserve enough to reproduce and review the run, not every local workbench file:

- sealed input description/digest;
- intent/style/render profile;
- canonical session/checkpoint;
- initial whole drawing;
- prioritized major residual sequence;
- representative before/after inspections;
- at least one explicit parent-structure revalidation point before downstream description when applicable;
- for material occlusions, concise evidence of visible anchors and the chosen minimum hidden-continuity judgment when that relation affected the drawing;
- final PNG;
- end-to-end replay/GIF;
- concise decision log;
- independent whole-image review;
- cost inventory and known limitations.

## Reopen protocol

```text
observe failure
→ identify earliest responsible product/guidance premise
→ REOPEN narrowly
→ minimal correction
→ technical regressions
→ RECLOSE
→ rerun affected D-case from sealed input
```

Do not create D-specific runtime feature flags, task-specific pipelines, or solution-encoding helpers.

# Release hardening

Starts after D01–D06 are accepted.

## R01 — Consolidation

- absorb only repeated, evidence-backed fixes into canonical docs/API;
- remove dogfood-only workaround code/scripts;
- ensure no second workflow grew around a test subject.

## R02 — Final regression

Cover observed croquis, figure/subject, tonal, free-draw, imaginative, hybrid, checkpoint/resume, intent/style change, value revision, PNG/replay/GIF parity, clean package installation, structural-specificity preservation, parent-construction revalidation, and occlusion under/over-inference behavior. Regression supports direct review; it does not replace it.

## R03 — Physical R23 retirement

Start from `R03_RUNTIME_OWNERSHIP_INVENTORY.md`, which records the pre-D01 module-level
`canonical / shared / mixed / legacy-only / adapter` baseline and the compatibility seams that
must be split before deletion.

Inventory remaining stage/runtime/review/Pn-era surfaces as:

```text
remove
retain as shared capability
retain as explicit time-bounded compatibility adapter
historical Git only
```

Before deleting the old runtime, explicitly choose whether R23 support remains **full resume**,
becomes **migration-only**, or ends. The current migration implementation first resumes a
`DrawingRun`, so migration-only retirement requires a direct checkpoint-to-vNext adapter before
`run/stages/review/exemplar` can be removed.

Do not remove compatibility before support/migration evidence justifies it. After retirement, normal imports/package/docs must remain stage-free and supported legacy inputs must either migrate correctly or fail with actionable errors.

## R04 — Release

Final exit requires source tree, public API, package, deployable docs, support policy, CI, and demonstrated D01–D06/R02 evidence to tell the same canonical truth.

Representative examples are optional release assets, not a required package surface. Add an `examples/` tree only after examples are good enough to teach from without becoming accidental coordinate/style templates.

Release claims may include only what was actually demonstrated.
