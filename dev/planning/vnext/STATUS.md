# img2drawing current status

Updated: 2026-09-27

```text
PUBLISHED STABLE:   v1.0.3 · DrawingSession/1.0.3-vnext · A14
RELEASE TAG:        v1.0.3 → d6151ba8dfef8dc37ef5cddd24c2c6c974d53976
CURRENT SOURCE:     1.1.0 · R1 structural release
CURRENT RENDERER:   img2drawing-pencil/11 · pixel-identical to v1.0.3 pillow-pencil-contact-v11/1
RENDERER POLICY:    no additive v12 for this quality cycle
ACTIVE BOTTLENECK:  none · S07 mechanical validation CLOSED; S08 v1.1.0 release staged
S01 DESIGN:         CLOSED
S02 INSTRUCTIONS:   CLOSED · bounded anti-normalization reopen merged; further behavioral proof deferred by user acceptance
S03 CAMPAIGN:      PASS / USER_ACCEPTED · class runs remain NOT_RUN; no new visual-quality claim
S04 CLASSIFICATION: CLOSED / NO RENDERER CHANGE · no current material defect was proven
R1 REFACTOR:        CLOSED · vnext→session/authoring, one render package, one timelapse export; v11 golden identical
S05 REPLAY BOUNDARY: CLOSED by R1 · RenderProfile v2 persists contract digest; v9/v10 fail closed → img2drawing==1.0.3
GRAPH CLEANUP:      Slice A CLOSED · Slice B CLOSED · Slice C CLOSED · Slice D ownership cleanup CLOSED · Slice E structural QA CLOSED
PACKAGE VERSION:    1.1.0 selected after S07 mechanical validation
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

- `v1.0.3` remains an immutable published release. v1.1.0 is staged through `dev/release/publish/v1.1.0.json`; the GitHub Release workflow records publication after main CI.
- PR #48's additive `v12` experiment was abandoned without merge. Renderer generation numbers are not a feature counter.
- **S01 design closure is complete.** The quality failure taxonomy, reversible evidence-gate model, and renderer-family/replay policy agree on one architecture.
- **S02 instruction implementation is CLOSED again after the bounded S03.1 reopen.** The anti-normalization/reference-authority patch is merged. This does **not** mean the behavioral defect is proven closed: that proof was not completed; the user accepted the S03 release gate with this limit recorded.
- **S03 dogfood is PASS / USER_ACCEPTED for this release scope.** The user accepted the gate on 2026-09-27; the four prepared simple still-life classes remain NOT_RUN after Luna usage limits interrupted execution. This records an explicit decision, not measured drawing-quality proof. See `../../dogfood/s03-quality-gates/USER_ACCEPTANCE_2026-09-27.md`.
- **S04 is CLOSED / NO RENDERER CHANGE SELECTED.** Historical Gojo residuals were classified. The current campaign has no completed visual evidence from which to prove a renderer-owned defect, so S06 is skipped without a claim that no defects exist. S07 mechanical release validation is active.
- **Instruction-graph attention cleanup is CLOSED through Slice E.** Slice A synchronized planning authority, Slice B reduced `SKILL.md` to the root router, Slice C reduced `references/INDEX.md` to a direct map, Slice D restored canonical leaf ownership/runtime boundaries, and Slice E added structural CI for attention budgets, direct root fan-out, broken internal routes, canonical owner reachability, and deployable/control-plane separation. The cleaned baseline remains `SKILL.md` 9,066 bytes and `references/INDEX.md` 7,692 bytes, guarded by 12,000-byte / 10,000-byte ceilings and a 16-leaf direct-root-route ceiling.
- Slice E changed no drawing semantics, renderer/runtime behavior, package version, or dogfood verdict. Implementation CI run `34982967070` passed current docs/runtime, instruction graph, S03 harness, active suite, historical evidence, B17, and B18 before the final CLOSED transition.
- The redesign keeps `pillow-pencil-contact-v11 / 1` as the current renderer family. Exact pixel identity will move to a persisted renderer contract digest plus immutable package/tag boundary before intentional current-v11 pixel divergence.
- No next package version or release candidate is authorized yet. Version selection happens only after visual and mechanical validation close.
- The installable R23 runtime/legacy namespace remains physically retired from current `src`.

## S03 accepted scope and remaining evidence

Fresh workers receive the updated skill, the reference, and the normal public runtime surface without prior solution strokes or evaluator hints.

Required classes:

1. apple still life — NOT_RUN;
2. ceramic mug still life — NOT_RUN;
3. closed umbrella still life — NOT_RUN;
4. potted plant still life — NOT_RUN. The S03 release gate was accepted by the user; no class-level PASS is claimed.

Any future class-level PASS still requires canonical provenance, final PNG, action-0→latest GIF, comparison evidence, residual review, and a KEEP/SOFTEN/RETIRE audit. The user acceptance record is the current release decision.

S04 residual ownership uses this split:

```text
wrong path / proportion / ownership / overlap / contact / reference substitution
→ geometry / instruction owner

correct geometry but wrong weight / taper / terminal / grain / deposition
→ renderer-material candidate
```

A renderer candidate requires both real-drawing evidence and a minimal controlled reproduction.

## Instruction-graph cleanup state

The cleanup existed because the graph accumulated strong but duplicated guidance across `SKILL.md`, `references/INDEX.md`, and specialist leaves. It is now closed through the structural QA slice.

Current bounded sequence:

```text
Slice A authority synchronization                         CLOSED
Slice B SKILL.md router reduction + direct quality gate   CLOSED
Slice C INDEX.md map-only reduction                       CLOSED
Slice D leaf ownership / runtime-boundary cleanup         CLOSED
Slice E attention-architecture QA + structural CI         CLOSED
S03 dogfood user acceptance                              PASS / USER_ACCEPTED
S04 renderer decision                                     CLOSED / NO CHANGE
S07 mechanical release validation                         ACTIVE
```

The detailed scope and closure evidence live in `INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md`. New instruction accumulation is not authorized by Slice E closure; the next release target is S07 mechanical validation under the recorded dogfood acceptance.

## Renderer/replay boundary (S05, closed by R1)

Persisted render identity now binds:

```text
renderer_id              img2drawing-pencil
renderer_version         11
renderer_contract_digest RenderProfile v2 field; exact pixel-behavior identity
```

Replay rule in current source:

- identity + digest match → exact;
- v1.0.3 `pillow-pencil-contact-v11 / 1` profiles (no digest) → accepted as the current contract; the v11 golden proves pixel identity;
- foreign digest, `v9`/`v10`, unknown identity, or retired `region.*` history → fail closed with a pointer to `img2drawing==1.0.3`;
- profile-less checkpoints resume and render only after an explicit `migrate_render_profile()`;
- published `v1.0.3` package/tag/freeze remains canonical authority for its original behavior.

S07 mechanical validation closed on main CI run `36327459040` after PR #68; v1.1.0 is the selected S08 release version.

Current `src` carries one renderer. Historical renderer implementations live in Git history and published releases, not in active source.

## R1 structural refactor (1.1.0)

R1 changed structure, not drawing semantics or pixels:

- `img2drawing.vnext` → `img2drawing.session` (DrawingSession + records) and `img2drawing.authoring` (markmaking, retune, curves, construction facade);
- nine generation-layered `render/pillow_*` modules + registry/dispatch/binding monkey-patches → `img2drawing.render` (`contract`, `paper`, `hand`, `grades`, `deposit`, `eraser`, `pencil`, `profile`, `artifact`);
- `provenance/timelapse.py` (legacy v9 exporter that fresh workers kept selecting) and `provenance/fast_timelapse/` → `img2drawing.timelapse` with one `export_timelapse()` behind `DrawingSession.export_timelapse()`;
- removed: `core/session.py`, `core/fill.py`, root compat shims, gesture/renderer runtime bindings, v9-calibrated `tone_scale`, orphan `line_weight`/`scale_guidance`;
- fixed: a v1.0.3 crash when a broad stroke's mask was empty (e.g. clipped by the canvas edge).

Persisted `img2drawing.vnext.*` schema strings and ids are unchanged data so earlier checkpoints and digests still resume. Current workers use the post-R1 public skill/runtime and fixed references in `../../dogfood/s03-quality-gates/SIMPLE_SUBJECT_CAMPAIGN.md`; Gojo and figure-pilot packets remain historical.

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
- v1.1.0 release intent: `dev/release/publish/v1.1.0.json`, `docs/releases/v1.1.0.md`, and `dev/release/vnext/CONTRACT_FREEZE_V1_1_0.json`;
- historical published stable: Git tag / GitHub Release `v1.0.3` + `docs/releases/v1.0.3.md`;
- exact stable candidate: `dev/release/vnext/V1_0_3_STABLE_PROMOTION.json`;
- immutable v1.0.3 contract: `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- G01 evidence: `dev/dogfood/g01-gesture-rc2/README.md`;
- G02 evidence: `dev/dogfood/g02-broad-pencil-v11/README.md`;
- immutable v1.0.2 snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`.
