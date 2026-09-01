# img2drawing vNext post-freeze validation and release

Updated: 2026-09-01
Starts only after: **B18 CLOSED**

This document defines the first new full visual dogfood after the B09–B18 implementation
phase. Earlier dogfoods remain historical evidence, but no new unseen-subject/cross-agent
campaign is run before B18.

## Governing rule

```text
implementation completes first
→ system freeze
→ fresh dogfood tries to break it
→ responsible B-slice reopens
→ affected dogfood reruns
→ final regression
→ physical legacy retirement
→ release
```

Dogfood is validation, not a new architecture layer. A D-run never owns permanent runtime
code or a second workflow.

## Sealed input contract

Fresh workers may receive only what the product is supposed to provide:

- installed/current skill/package;
- fresh subject/reference when the mode requires one;
- user request;
- declared/inferred `DrawingIntent`;
- ordinary canonical runtime/output paths.

Do not provide:

- answer image / ideal-stroke reference;
- authored coordinate or landmark table;
- previous session/action ids;
- previous residual priorities;
- evaluator rationale/verdict;
- Pn/R23 worker packet;
- subject-specific helper script whose coordinates encode the solution.

Evaluator evidence may expose the subject/current drawing/canonical inspection outputs
needed to review quality, but must not leak a previous worker's solution into a new run.

## D01 — Difficult observed croquis

Intent baseline:

```text
observed · croquis · pose · pencil_loose
```

Primary proof:

- gesture / line of action;
- balance/support/stance;
- head/ribcage/pelvis masses and turn;
- limb chain and feet;
- silhouette / overlap / prop contact;
- line economy.

B07-R1 acceptance axes both apply:

1. **record cost** — canonical session must not regress to brute-force microstroke
   explosion; compare with preserved R23/vNext baselines using meaningful inventory
   units, not cosmetic JSON minification;
2. **representation quality** — with tone mentally/actually removed, major limb/torso/
   clothing volume and overlap still read.

Likely reopen mapping:

- observation boundary failure → B01-R1/B02+B03;
- construction/form failure → B05;
- correction/provenance failure → B06;
- evidence budget failure → B07;
- value/representation-cost failure → B07-R1/B16;
- finish policy failure → B09.

## D02 — Observed figure / subject recognition

Intent baseline:

```text
observed · figure_drawing · subject · graphite_academic
```

Requires D01 macro quality plus identity-bearing relations:

- eye spacing/direction and facial feature relations;
- cheek/jaw/hair occlusion;
- hair envelope/groups/termination direction;
- hand/foot parent-chain/contact/visibility;
- distinctive clothing mass/openings/seams;
- prop topology/contact/terminal mass.

Do not pass because “eyes”, “hair”, or “fingers” exist. Recognition must survive whole
image review and remain subordinate to correct macro form.

Likely reopen: B09, B10, or upstream B05/B01-R1 when finish exposed a construction or
observation premise error.

## D03 — Tonal study

Intent baseline:

```text
observed · tonal_study · form_light · graphite_tonal
```

Primary proof:

- large light/shadow families;
- calibrated broad value regions;
- edge hierarchy;
- form turning;
- focal value control;
- value revision through compact authored decisions.

Reject:

- arbitrary dark bands;
- hundreds of authored hatch micro-actions for one value premise;
- tone that manufactures missing form;
- line drawing plus renderer/post-filter presented as tonal study.

Likely reopen: B07-R1, B09, B11, B14, B15.

## D04 — Observed free-draw

Intent example:

```text
observed · free_draw · expressive · custom/preset
```

Primary proof:

- reference can inform subject truth without forcing croquis/figure grammar;
- composition, simplification, rhythm, focal hierarchy, and style are intentional;
- preserved reference constraints remain explicit;
- correction loop remains meaningful under looser grammar.

Likely reopen: B13–B16.

## D05 — Imaginative + hybrid

Run sequentially; do not combine them into one ambiguous claim.

### D05-A imaginative

No external subject is supplied.

Authority:

```text
declared subject/composition/gesture/rhythm/focal/shape-language intent
```

Prove that subjectless create/inspect/correct/finish/replay works without fake reference
or overlay authority.

### D05-B hybrid

Use a reference plus explicit transformation intent.

Separate in provenance:

```text
preserved constraints
transformed constraints
```

The worker must not silently sacrifice a preserved constraint because the chosen style
or expressive intent prefers something else.

Likely reopen: B13, B14, B15, B16, B10.

## D06 — Cross-agent reproducibility

Use at least two independent fresh workers on the same sealed input contract. Identical
strokes are not required.

Compare:

- observation quality;
- highest-impact residual prioritization;
- edit strategy;
- final visual quality;
- evidence/read cost;
- session/action cost;
- failure modes;
- degree of Pn/legacy leakage (must be none on canonical route).

Instruction changes are justified only by repeated divergence. If a minimal guidance fix
is made, reopen the responsible B-slice, recclose it, and rerun the affected case.

Do not claim statistical generality across all models/subjects from two workers.

## Evidence policy for D01–D06

Preserve enough evidence to reproduce and review the run, not every intermediate file.

Representative package:

- sealed input description;
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

Raw local workbench files need not all be committed.

## Reopen protocol

A failed D-case does not automatically invalidate the whole system.

```text
observe failure
→ identify earliest responsible product premise
→ REOPEN that B-slice only
→ minimal construction/implementation correction
→ run technical regressions
→ RECLOSE slice
→ rerun affected D-case from sealed input
```

Examples:

- D02 facial relation failure caused by B09 policy → B09 REOPEN;
- D02 hand repeatedly repaired because arm chain is absent → B05 REOPEN;
- D03 fill revision cannot bind to correction → B06/B07-R1 REOPEN;
- D05 subjectless inspect assumes a subject → B13 REOPEN;
- D06 workers interpret a style field as renderer state → B15 REOPEN;
- GIF final frame differs from PNG → B11 REOPEN.

Do not create D-specific runtime feature flags or parallel pipelines.

# Release hardening

Starts after D01–D06 are accepted.

## R01 — Consolidation

- absorb only repeated, evidence-backed dogfood fixes into canonical docs/API;
- remove dogfood-only workaround code/scripts;
- resolve temporary compatibility notes introduced during reopens;
- ensure no second workflow grew around a test subject.

## R02 — Final regression

Run a compact representative matrix covering:

```text
observed croquis
observed figure/subject
observed tonal
observed free-draw
imaginative
hybrid
checkpoint/resume
intent/style change
value-region revision
PNG/replay/GIF parity
clean install/package
```

Regression supports direct review; it does not replace it.

## R03 — Physical R23 retirement

Only now remove/archive remaining Pn/R23 current-path surface according to B12's support
matrix and the proven migration needs.

Inventory each item as:

```text
remove
retain as shared capability
retain as explicit time-bounded compatibility adapter
historical Git only
```

Candidates include stage runtime, stage review manifests, playbooks, Pn references,
stale exports/tests/examples, and obsolete package data. Do not delete the frozen Git
baseline or historical evidence.

After removal, verify:

- no canonical import/example/test depends on retired modules;
- supported legacy migration still works where promised;
- unsupported legacy inputs fail with actionable errors;
- shared stroke/history/renderer capability remains single-source;
- package/docs/link/dead-code audits pass.

## R04 — Release

Final exit requires package/docs/examples/CI/source tree to tell the same canonical truth
and D01–D06 + R02 evidence to support the product claims.

Release claims may include only what was actually demonstrated. Limitations and remaining
legacy compatibility windows are documented explicitly.
