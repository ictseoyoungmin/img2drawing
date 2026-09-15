# img2drawing current status

Updated: 2026-09-15

```text
PUBLISHED STABLE:   v1.0.3 · DrawingSession/1.0.3-vnext · A14
RELEASE TAG:        v1.0.3 → d6151ba8dfef8dc37ef5cddd24c2c6c974d53976
CURRENT RENDERER:   pillow-pencil-contact-v11/1
RENDERER POLICY:    no additive v12 for this quality cycle
ACTIVE BOTTLENECK:  S03 · fresh-worker visual dogfood
S01 DESIGN:         CLOSED
S02 INSTRUCTIONS:   CLOSED · bounded anti-normalization reopen merged; behavioral proof remains in S03.1
S03.1 RERUN:        READY / NOT_RUN · initial batch remains BLOCKED until clean fresh-worker rerun
S04 CLASSIFICATION: ACTIVE / PARTIAL · S03.1 classified; renderer-owned blocker count = 0
GRAPH CLEANUP:      Slice A CLOSED · Slice B SKILL router reduction CLOSED · Slice C INDEX reduction READY
PACKAGE VERSION:    no new RC/version authorized before integrated validation
HISTORICAL REPLAY:  v1.0.3 package/tag remains immutable pixel authority
G01 GESTURE:        PASS/CLOSED
G02 BROAD PENCIL:   PASS/CLOSED
STABLE SOURCE:      release/1.0.3-stable @ 0de885e6d3f2ed6ac857c46e60875cc8c5c9f727
STABLE WHEEL GATE:  CI 34749311565 · package tree 5758c5efa60d80a0d483bcb3573258e34d609055
MAIN RELEASE CI:    34749869989 · PASS
PUBLISH WORKFLOW:   34749920471 · PASS
PUBLISH STATE:      GitHub Release v1.0.3 published
```

## Authority contract

This file is the **canonical point-in-time development status** for mutable `main` work.

Authority is intentionally split by purpose:

1. `STATUS.md` — current point-in-time state: what is ACTIVE, BLOCKED, READY, CLOSED, or NOT_RUN now;
2. `ROADMAP.md` — sequencing, slice definitions, dependencies, and closure criteria;
3. `INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md` — bounded execution plan for the current instruction-graph cleanup slices A–E;
4. release tags, freezes, manifests, and release notes — immutable historical release authority.

`ROADMAP.md` may explain why a state exists, but it must not silently override this file's current-state label. If the two diverge, update them in the same bounded documentation slice; do not create a second current-state truth.

## Current truth

- `v1.0.3` remains the latest published stable release and its tag, artifacts, freeze, and historical dogfood are immutable.
- PR #48's additive `v12` experiment was abandoned without merge. Renderer generation numbers are not a feature counter.
- **S01 design closure is complete.** The quality failure taxonomy, reversible evidence-gate model, and renderer-family/replay policy agree on one architecture.
- **S02 instruction implementation is CLOSED again after the bounded S03.1 reopen.** The anti-normalization/reference-authority patch is merged. This does **not** mean the behavioral defect is proven closed: that proof belongs to the clean S03.1 fresh-worker rerun.
- **S03 fresh-worker visual dogfood remains the active product bottleneck.** S03.1's initial batch is BLOCKED; its clean rerun is READY / NOT_RUN. S03.2–S03.4 remain pending.
- **S04 is ACTIVE / PARTIAL.** S03.1 residuals are classified as reference-authority / authored-geometry / anti-symbol-retirement failures. No renderer-owned blocking defect is proven in that batch.
- **Instruction-graph attention cleanup remains bounded maintenance around S03.** Slice A synchronized planning authority. Slice B is now CLOSED: `SKILL.md` is reduced to mission, seven root invariants, conditional routing, the canonical correction loop, and completion/output routing; observed finished/substantially-resolved work now routes directly to `review/visual-quality-gates.md`. Slice C is READY and owns only the `references/INDEX.md` map reduction.
- Slice B changed no specialist leaf semantics, renderer/runtime behavior, package version, or dogfood verdict. PR CI run `34968493328` passed current docs/runtime, instruction graph, S03 harness, active suite, historical evidence, B17, and B18 before the final CLOSED transition.
- The redesign keeps `pillow-pencil-contact-v11 / 1` as the current renderer family. Exact pixel identity will move to a persisted renderer contract digest plus immutable package/tag boundary before intentional current-v11 pixel divergence.
- No `1.0.4rc1` or other package-version bump is authorized yet. Version selection happens only after visual and mechanical validation close.
- The installable R23 runtime/legacy namespace remains physically retired from current `src`.

## Active S03 evidence loop

Fresh workers receive the updated skill, the reference, and the normal public runtime surface without prior solution strokes or evaluator hints.

Required classes:

1. strong-perspective close figure — **initial batch BLOCKED; clean rerun READY / NOT_RUN**;
2. full-body 3/4 figure with attached or held prop — NOT_RUN;
3. frontal or near-frontal full body — NOT_RUN;
4. head/hair close-up — NOT_RUN.

Each run must preserve canonical provenance and provide a final PNG, action-0→latest GIF, comparison evidence, top remaining residuals, and a KEEP/SOFTEN/RETIRE audit. A blocking failure in any class stays open; results are not averaged into one score.

S04 residual ownership uses this split:

```text
wrong path / proportion / ownership / overlap / contact / reference substitution
→ geometry / instruction owner

correct geometry but wrong weight / taper / terminal / grain / deposition
→ renderer-material candidate
```

A renderer candidate requires both real-drawing evidence and a minimal controlled reproduction.

## Instruction-graph cleanup state

The current cleanup exists because the graph accumulated strong but duplicated guidance across `SKILL.md`, `references/INDEX.md`, and specialist leaves.

Current bounded sequence:

```text
Slice A authority synchronization                         CLOSED
Slice B SKILL.md router reduction + direct quality gate   CLOSED
Slice C INDEX.md map-only reduction                       READY
Slice D leaf ownership / runtime-boundary cleanup         BLOCKED by C
Slice E attention-architecture QA + structural CI         BLOCKED by D
clean S03.1 rerun                                         follows the cleaned graph
```

The detailed scope and closure rules live in `INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md`. Do not broaden Slice C into leaf ownership cleanup before its own closure criteria pass.

## Renderer/replay direction

Before current-v11 pixel behavior is intentionally changed, persisted render identity must become capable of binding:

```text
renderer_id
renderer_version
renderer_contract_digest
```

Target replay rule:

- family/version/digest match → exact replay eligible;
- same family/version with digest mismatch → fail closed or require explicit migration;
- a legacy session without a digest remains loadable under an explicitly non-exact current-source policy;
- published `v1.0.3` package/tag/freeze remains canonical authority for its original v11 behavior.

Historical implementation accumulation in active `src` is not the long-term replay strategy.

## Stable release authority

Before publication, the selected package was rebuilt from `release/1.0.3-stable` commit `0de885e6d3f2ed6ac857c46e60875cc8c5c9f727` and verified by CI run `34749311565`.

- root tree: `996836ef4c2188ad39e621550575e0d9780d288f`
- package tree: `5758c5efa60d80a0d483bcb3573258e34d609055`
- workflow artifact: `10315122558`
- candidate artifact ZIP SHA-256: `2c7650e252b2b2f253630724bd35a30c348bd3114eebf034e45ec4f2cbdfe04a`
- candidate wheel: `img2drawing-1.0.3-py3-none-any.whl`
- candidate wheel SHA-256: `eaecfeb08100640211d3de73ea6dcfd1557d097c85318c814e217a3eb4265567`

`dev/release/vnext/V1_0_3_STABLE_PROMOTION.json` remains exact pre-publication authority. Current development must not rewrite it.

## Published release authority

Post-merge main CI run `34749869989` passed all current runtime, instruction-graph, active-suite, historical, B17, and B18 gates. Publish workflow run `34749920471` created GitHub Release `v1.0.3` from main commit `d6151ba8dfef8dc37ef5cddd24c2c6c974d53976`.

Published assets:

- `img2drawing-1.0.3-py3-none-any.whl` — SHA-256 `89061b74984e1ffbb78b48fa1de81aacd64c9d4bfb2ec6baadc41b703bc240f7`
- `img2drawing-1.0.3.tar.gz` — SHA-256 `08067b1aec8384a94dc323d6ea511be84ffe006069f5180ff3c44c9d9a1dd4c4`

## Historical B18 boundary

At the B18 implementation freeze, the product foundation was **frozen through B18** and the formal **D01–D06 not started** campaign was still future work. Those phrases are historical evidence only and do not describe current sequencing.

## Authority map

- current mutable state: **this file, `STATUS.md`**;
- product sequencing and closure criteria: `ROADMAP.md`;
- instruction-graph attention cleanup slices A–E: `INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md`;
- v11 quality execution plan: `V11_QUALITY_CONTROL_SLICE_PLAN.md`;
- v11 redesign rationale: `V11_QUALITY_CONTROL_REDESIGN.md`;
- current published stable: Git tag / GitHub Release `v1.0.3` + `docs/releases/v1.0.3.md`;
- exact stable candidate: `dev/release/vnext/V1_0_3_STABLE_PROMOTION.json`;
- immutable v1.0.3 contract: `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- G01 evidence: `dev/dogfood/g01-gesture-rc2/README.md`;
- G02 evidence: `dev/dogfood/g02-broad-pencil-v11/README.md`;
- immutable v1.0.2 snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`.
