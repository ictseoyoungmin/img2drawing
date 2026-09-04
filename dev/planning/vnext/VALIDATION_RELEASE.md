# img2drawing vNext post-alignment validation and release

Updated: 2026-09-04
Starts only after: **B18 CLOSED + post-freeze alignment A1–A5 accepted**

This document owns the first fresh visual validation after implementation freeze and product-surface alignment. Earlier dogfoods remain historical evidence; they do not substitute for D01–D06.

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
- head/ribcage/pelvis mass and turn;
- limb chain and foot orientation;
- silhouette / overlap / prop contact;
- geometry-preserving line economy.

Reject a result that uses fewer lines by reducing the subject to symbolic head/limb/foot/fold shapes. Cost and fidelity are both first-class:

1. **record cost** — the session must not regress to brute-force microstroke explosion;
2. **representation quality** — major form, overlap, contact, and characteristic curvature must remain readable with sparse marks.

Likely reopen mapping:

- observation/boundary failure → B01-R1/B02+B03 or A4 guidance routing;
- construction/form failure → B05;
- correction/provenance failure → B06;
- evidence budget failure → B07;
- value/representation-cost failure → B07-R1/B16;
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

Do not pass because “eyes”, “hair”, “fingers”, or “folds” exist. Recognition must survive whole-image review and remain subordinate to correct macro form.

Likely reopen: B09/B10, upstream B05/B01-R1, or A4/A5 when the issue is guidance coverage/routing rather than runtime mechanics.

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

Reject arbitrary dark bands, dense authored hatch micro-actions for one value premise, tone that manufactures missing form, or a line drawing plus renderer/post-filter presented as tonal study.

Likely reopen: B07-R1, B09, B11, B14, B15.

## D04 — Observed free-draw

Intent example:

```text
observed · free_draw · expressive · custom/preset
```

Prove that reference truth can coexist with intentional composition, simplification, rhythm, focal hierarchy, and style without forcing figure/croquis grammar. Preserved reference constraints must remain explicit and the correction loop must remain meaningful under looser grammar.

Likely reopen: B13–B16.

## D05 — Imaginative + hybrid

Run separately.

### D05-A imaginative

No external subject. Authority is declared subject/composition/gesture/rhythm/focal/shape-language intent. Prove subjectless create/inspect/correct/finish/replay without fake reference or overlay authority.

### D05-B hybrid

Use a reference plus explicit transformation intent. Provenance must distinguish preserved from transformed constraints; style may not silently sacrifice preserved geometry.

Likely reopen: B13–B16 and B10.

## D06 — Cross-agent reproducibility

Use at least two independent fresh workers on the same sealed input contract. Identical strokes are not required.

Compare:

- observation quality;
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

Cover observed croquis, figure/subject, tonal, free-draw, imaginative, hybrid, checkpoint/resume, intent/style change, value revision, PNG/replay/GIF parity, and clean package installation. Regression supports direct review; it does not replace it.

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
