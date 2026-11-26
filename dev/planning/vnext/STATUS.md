# img2drawing current status

Updated: 2026-11-26

```text
PUBLISHED STABLE:   v1.2.1 · selected maintenance release (publication gated by main CI)
RELEASE TAG:        v1.2.1 · manifest-driven publish authority
CURRENT SOURCE:     1.2.1 · tonal authoring and provenance maintenance
CURRENT RENDERER:   img2drawing-pencil/11 default · exact v11 replay; v1.3 development opt-in 11-opacity-normalized-v1
RENDERER POLICY:    one engine · immutable per-session material contracts · no automatic migration or v12
ACTIVE BOTTLENECK:  v1.3.0 S01–S06 integrated; S00/S07 independent comparison remains open
S01 DESIGN:         CLOSED
S02 INSTRUCTIONS:   CLOSED · bounded anti-normalization reopen merged; further behavioral proof deferred by user acceptance
S03 CAMPAIGN:      PASS / USER_ACCEPTED · class runs remain NOT_RUN; no new visual-quality claim
S04 CLASSIFICATION: CLOSED / NO RENDERER CHANGE · no current material defect was proven
R1 REFACTOR:        CLOSED · vnext→session/authoring, one render package, one timelapse export; v11 golden identical
S05 REPLAY BOUNDARY: CLOSED by R1 · RenderProfile v2 persists contract digest; v9/v10 fail closed → img2drawing==1.0.3
GRAPH CLEANUP:      Slice A CLOSED · Slice B CLOSED · Slice C CLOSED · Slice D ownership cleanup CLOSED · Slice E structural QA CLOSED
PACKAGE VERSION:    1.2.1 tonal authoring/provenance maintenance
HISTORICAL REPLAY:  v1.0.3 package/tag remains immutable pixel authority
G01 GESTURE:        PASS/CLOSED
G02 BROAD PENCIL:   PASS/CLOSED
HISTORICAL V1.0.3 SOURCE: release/1.0.3-stable @ 0de885e6d3f2ed6ac857c46e60875cc8c5c9f727
STABLE WHEEL GATE:  CI 34749311565 · package tree 5758c5efa60d80a0d483bcb3573258e34d609055
MAIN RELEASE CI:    required green before manifest-driven publish
PUBLISH WORKFLOW:   .github/workflows/publish-release.yml
PUBLISH STATE:      GitHub Release v1.2.1 selected via main CI + publish manifest; v1.2.0 remains published until successful workflow
```

## Authority contract

This file is the **canonical point-in-time development status** for mutable `main` work.

Authority is intentionally split by purpose:

1. `STATUS.md` — current point-in-time state: what is ACTIVE, BLOCKED, READY, CLOSED, or NOT_RUN now;
2. `ROADMAP.md` — sequencing, slice definitions, dependencies, and closure criteria;
3. `INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md` — bounded execution plan for the current instruction-graph cleanup slices A–E;
4. release tags, freezes, manifests, and release notes — immutable historical release authority.

`ROADMAP.md` may explain why a state exists, but it must not silently override this file's current-state label. If the two diverge, update them in the same bounded documentation slice; do not create a second current-state truth.

## Current v1.3.0 development branch checkpoint

Scope: `dev/v1.3.0-constructive-drawing`, not the published v1.2.1 package/tag.

- S00 tooling merged (#79), independent six-class matched baseline NOT_RUN; remains open.
- S01 observation (#80, 69147b8): explicit landmarks/ratios/axes/sections/negative spaces/occlusion; 289 active tests passed. Real local 300-action landmark evidence; no visual PASS.
- S02 construction (#81, fb8babc): projected ellipses, explicit asymmetric sections and guide paths through existing ConstructionMark; 293 active tests passed. Local guide addition and retirement restored exact canonical pixels.
- S03 stroke authoring (#82, 1a2582f): Bezier, arc-length pressure and bounded deformation, atomic replacement/split/transform and exact prospective preview; 298 active tests passed. Real local 14-stroke group edit preview/commit exact pixel equality; split may change contact/compositing and is not pixel-equivalent by contract.
- S04 tonal inspection (#83, 4f0201a): shared runtime/CLI diagnosis, direction and centerline evidence, protected coverage and separation, explicit pressure proposals, verified cached canonical renders; 303 active tests passed, v11 golden and package boundary passed. Local 325-action portrait exploration retained geometry/material, lowered protected mean darkness modestly but coverage remained high; overall likeness/hair quality NOT PASS. Cached 3-area historical inspection took ~0.99 s locally with prior coverage reproduced exactly; full re-render timed out in the same local run. No general speed guarantee.
- S05 semantic groups (#84, a9f8067): explicit membership/dependency review, atomic transforms and guide retirement on existing history. 308 active tests passed. Non-blind real portrait copy: 5 groups / 124 members; 325→327 actions invalidated face/eye/nose-mouth/hair dependent reviews while unrelated sweater review stayed current; source checkpoint unchanged. No artistic PASS.
- S06 cleanup (#85, a2cb747): 310 active tests passed. Archived 253 unchanged retired artifacts (29,211,911 bytes) from checkout with immutable v1.2.1 blob recovery records, retaining required checkpoint. Tracked tree 161,993,315→132,951,388 bytes at S06; not a reduction of historical Git object size. API guide 22,720→20,502 bytes; CI enforces attention and repository-growth budgets.
- S07 tooling (#86, dea9557): isolated worker packets and submitted replay verification merged; PR CI 45702953436 PASS (312 active, 44 runtime tests and package/historical/archive gates). Fixed resume of submitted inspection artifacts. Local shared-path still-life diagnostic across pinned v1.2.0, v1.2.1 and S05 candidate: 33 actions, 29 surviving strokes, ten samples, independently rendered canonical PNG and decoded GIF endpoints pass; v1.2.1 and S05 candidate state/final pixels match. Not fresh-worker performance, intermediate-frame fidelity, or visual PASS. Five local reference candidates prepared, hand-object contact reference still needed; independent worker/model and equal-budget runs not sealed or executed.
- S07 public local erase/replay audit (#87, fe6ffde): 325 active tests, 44 runtime checks and package/historical/archive gates passed. Existing portrait copy 327 actions / 83 sampled frames passed strict regenerated sample and GIF tolerance audit; independent visual evaluation remains NOT_RUN.
- S07 tonal continuity follow-up: saved portrait PNGs show that matching average darkness can conceal abrupt invented value bands. Added optional explicitly corresponding tonal patches and read-only canonical cursor comparisons. External images are marked unverified; no renderer or history-schema change. Local focused tests passed on the available S07 source; final candidate CI is the integration gate. Interrupted portrait's latest checkpoint was not recovered, so no claim of resuming it.
- S07 renderer-owned follow-up: #89 investigation merged d11ec24 after portable-path correction and CI 45783806782 PASS. #90 optional normalized contact contract merged a91df5c; exact candidate 28e8eac push CI 45784089581 PASS (343 active, 44 runtime; v11 golden, archive and package gates). Legacy v11 default/digest retained. New sessions may explicitly choose RenderProfile.opacity_normalized; contract identity/digest and patch caches separated, unknown/foreign identity or digest fails closed. Local same-environment before/after v11 comparison: all 16 hashes equal (NumPy 2.3.5, Pillow 12.3.0); recorded golden fixture not rewritten. Separate local identical 32-action neck studies have equal action-log and state hashes; mean darkness across seven patches .788277 vs .279505, both Fast GIFs pass all nine sampled hashes and tolerance. These are controlled material diagnostics, not independent portrait acceptance. No private images, coordinates or large outputs committed. Combined-head CI remains a separate gate.
- S07 Library hand-object contact follow-up: developer-authored study of a privately selected 3D render crop, 723×412, 297 actions per profile (identical action-log and state digests); all 76 regenerated Fast replay sample hashes matched per profile, GIF max channel error 10 (v11) / 23 (normalized), maximum frame mean 3.22515 / 3.15843, no tolerance failures. Local patch means show v11 palm lower turn .592 and sleeve light .791 vs normalized .060/.035; normalized avoids severe dark saturation but the midtone transitions are too pale, and fret/string contrast and banded wood/fabric shading remain unresolved. No physical grip correctness or independent artistic PASS. Current runtime source matches all 112 skill blobs in integration da1e2bc; integrated documentation CI 45785071186 SUCCESS. Both complete checkpoints and full GIFs retained privately; no private images, coordinate paths or generated output committed. A hand-object reference candidate is now selected, but independent baseline budget/execution remains unsealed.
- S07 hand-object corrective follow-up (developer-authored, not independent): resumed normalized 297-action copy. Added optional per-stroke material overrides to the existing atomic StrokeEdit preview/apply. First 80 edits: preview 11.59 s, commit 5.27 s, exact prospective/committed state and pixels. Second 61-edit preview exposed false checkerboard fret relief; accepted 21 plane edits only (new preview equals commit), rejected 40; added 12 observed contact details, ending at 410 actions. Original session retained. Selected patch darkness palm lower .0603→.1089, light sleeve .0353→.1266, outer sleeve .0638→.3597; nine-patch sleeve adjacent variation .2816→.8878→.5697 (reference .2151), reversals 3→3→4 (reference 0). Midtone range and soft transitions improved relative to first retune, but continuity and metal highlights remain unresolved. Local focused 28 tests PASS (11 new cases plus existing contract suites); independent comparison remains NOT_RUN. No renderer/schema change and no private coordinates/images committed.
- S07 narrow-highlight and family rewrite follow-up (developer-authored, not independent): preserved 410-action hand-object checkpoint; rejected two previews (broad oval patches, excessive dark transverse hatching); accepted a calibrated 123-action mixed batch (6 edits, 40 retirements, 77 explicit new marks) in a copy, 533 total. Exact preview/commit pixels and state, resume PASS; eight manually selected fret-center contrasts averaged -.020 before and .458 after versus .340 reference (approximate cross-image measurements, no absolute quality score). Bright fret readability improved, but excessive contrast in some intervals, mechanical texture and bright string detail remain unresolved. Added existing preview/apply support for explicit retirements and new draw specs, and optional ordered action digest guard. Local 41 focused tests PASS (13 new); renderer and persisted schema unchanged. No private source geometry or outputs committed. Independent S00/S07 comparison still NOT_RUN.
- S07 continuous graphite and ordered-lift study: public normalized-profile path eraser reuses existing canonical material lifting; explicit additions/retirements/erasures use the same atomic preview/apply digest. Eraser carries normal stroke identity and reversible history; stable layer order, conservative full recomposition for edits with lifts, and raw legacy fallback. Original C 533-action session preserved; reviewed D 688 actions (93 retirements, 30 graphite additions, 32 path lifts), exact prospective/committed pixels/state and resume. Fret mean contrast .458→.290 vs reference .340, longitudinal board mean darkness .551→.718 vs photo .794; board continuity chain variation .274→.282 (not improved on that chain), reversals 3→2. Real string reflections now visible, but selected reference string-patch alignment is imprecise and no independent artistic acceptance. All 173 every-four sampled hashes and GIF tolerances passed (max channel 12, maximum frame mean 3.34241). 59 local focused tests including 18 new cases passed. Old renderer identity/digest and persisted schema unchanged. Private imagery/coordinates/results excluded. Independent S00/S07 still NOT_RUN.
- S01–S06 feature implementation and regression gates CLOSED (75% of weighted plan, six of nine slices). S00/S07 WIP; S08 OPEN. No private images, answer coordinates or large outputs committed.
- Next: complete S00 sealed baseline and S07 independent visual comparison, review independent visual residuals; real long-session erasure/replay audit has passed and optional opacity model is integrated. Then S08 release validation. No promotion to v1.3.0 stable.

## Current truth

- `v1.2.1` is the selected bounded maintenance release. Actual publication follows successful main CI and the manifest-driven workflow; v1.2.0 is immutable. Renderer v11 and the persisted history contract are unchanged. Synthetic high-resolution replay is measured; independent portrait-quality proof remains open.
- PR #48's additive `v12` experiment was abandoned without merge. Renderer generation numbers are not a feature counter.
- **S01 design closure is complete.** The quality failure taxonomy, reversible evidence-gate model, and renderer-family/replay policy agree on one architecture.
- **S02 instruction implementation is CLOSED again after the bounded S03.1 reopen.** The anti-normalization/reference-authority patch is merged. This does **not** mean the behavioral defect is proven closed: that proof was not completed; the user accepted the S03 release gate with this limit recorded.
- **S03 dogfood is PASS / USER_ACCEPTED for this release scope.** The user accepted the gate on 2026-09-27; the four prepared simple still-life classes remain NOT_RUN after Luna usage limits interrupted execution. This records an explicit decision, not measured drawing-quality proof. See `../../dogfood/s03-quality-gates/USER_ACCEPTANCE_2026-09-27.md`.
- **S04 is CLOSED / NO RENDERER CHANGE SELECTED.** Historical Gojo residuals were classified. The current campaign has no completed visual evidence from which to prove a renderer-owned defect, so S06 was skipped without a claim that no defects exist. S07 mechanical release validation and S08 release selection are both CLOSED; v1.1.0 is published.
- **Instruction-graph attention cleanup is CLOSED through Slice E.** Slice A synchronized planning authority, Slice B reduced `SKILL.md` to the root router, Slice C reduced `references/INDEX.md` to a direct map, Slice D restored canonical leaf ownership/runtime boundaries, and Slice E added structural CI for attention budgets, direct root fan-out, broken internal routes, canonical owner reachability, and deployable/control-plane separation. The cleaned baseline remains `SKILL.md` 9,066 bytes and `references/INDEX.md` 7,692 bytes, guarded by 12,000-byte / 10,000-byte ceilings and a 16-leaf direct-root-route ceiling.
- Slice E changed no drawing semantics, renderer/runtime behavior, package version, or dogfood verdict. Implementation CI run `34982967070` passed current docs/runtime, instruction graph, S03 harness, active suite, historical evidence, B17, and B18 before the final CLOSED transition.
- The redesign keeps `pillow-pencil-contact-v11 / 1` as the current renderer family. Exact pixel identity will move to a persisted renderer contract digest plus immutable package/tag boundary before intentional current-v11 pixel divergence.
- M03 maintenance: partial override merge and executed-state provenance, explicit tonal-area plans, and developer-only QA are implemented in PRs #76–#78. The maintainer approved promotion of the bounded maintenance/QA scope on 2026-11-26; this is not an independent visual-quality pass. Real portrait exploration found striped dark masses, excessive highlight coverage and likeness errors. Independent fresh-worker likeness, the original 511-action reproduction and real long-session segment erasure remain open for v1.3.0.
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
S07 mechanical release validation                         CLOSED
```

The attention graph A–E cleanup remains historical CLOSED. M03's evidence-backed toner/markmaking issue is a new bounded development slice, not a reopening of Slice E.

## Renderer/replay boundary (S05, closed by R1)

Persisted render identity now binds:

```text
renderer_id              img2drawing-pencil
renderer_version         11
renderer_contract_digest RenderProfile v2 field; exact pixel-behavior identity
```

Replay rule in current source:

- supported identity + matching contract digest → exact under the verified renderer environment;
- v1.0.3 `pillow-pencil-contact-v11 / 1` profiles (no digest) → accepted as legacy v11 only; the v11 golden proves pixel identity;
- v1.3 development opt-in `11-opacity-normalized-v1` → explicit new RenderProfile, distinct digest required; no legacy automatic migration;
- foreign digest, `v9`/`v10`, unknown identity, or retired `region.*` history → fail closed with a pointer to `img2drawing==1.0.3`;
- profile-less checkpoints resume and render only after an explicit `migrate_render_profile()`;
- published `v1.0.3` package/tag/freeze remains canonical authority for its original behavior.

S07 mechanical validation closed on main CI run `36327459040` after PR #68. S08 selected v1.1.0; final main CI `36328874580` and publish workflow `36329064232` passed.

Current `src` carries one renderer. Historical renderer implementations live in Git history and published releases, not in active source.

## R1 structural refactor (1.1.0)

R1 changed structure, not drawing semantics or pixels:

- `img2drawing.vnext` → `img2drawing.session` (DrawingSession + records) and `img2drawing.authoring` (markmaking, retune, curves, construction facade);
- nine generation-layered `render/pillow_*` modules + registry/dispatch/binding monkey-patches → `img2drawing.render` (`contract`, `paper`, `hand`, `grades`, `deposit`, `eraser`, `pencil`, `profile`, `artifact`);
- `provenance/timelapse.py` (legacy v9 exporter that fresh workers kept selecting) and `provenance/fast_timelapse/` → `img2drawing.timelapse` with one `export_timelapse()` behind `DrawingSession.export_timelapse()`;
- removed: `core/session.py`, `core/fill.py`, root compat shims, gesture/renderer runtime bindings, v9-calibrated `tone_scale`, orphan `line_weight`/`scale_guidance`;
- fixed: a v1.0.3 crash when a broad stroke's mask was empty (e.g. clipped by the canvas edge).

Persisted `img2drawing.vnext.*` schema strings and ids are unchanged data so earlier checkpoints and digests still resume. Current workers use the post-R1 public skill/runtime and fixed references in `../../dogfood/s03-quality-gates/SIMPLE_SUBJECT_CAMPAIGN.md`; Gojo and figure-pilot packets remain historical.

## M01 public-contract maintenance (1.1.1)

M01 closed post-v1.1.0 drift without changing renderer pixels or persisted drawing schemas:

- plugin manifests follow the package version and are checked against `img2drawing.__version__`;
- runtime discovery separates authoring operations from output operations while retaining the v1.1.0 mixed-list compatibility alias;
- correction provenance, semantic value-role authoring, and construction-mark serialization are aligned with their documented contracts;
- current documentation verification is release-generic;
- the current package verifier plus runtime-discovery/markmaking tests use semantic names instead of stale release labels; deliberately historical vNext compatibility/freeze tests retain their historical names;
- retired v1.0.3 branch-only artifact steps are absent from active CI.

The v11 renderer identity/digest and golden pixels are unchanged.

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

## Published v1.1.0 release authority

PR #69 promoted the structural release; PR #70 stabilized two observed hosted-runner fixture hashes and attached the contract freeze. Main CI `36328874580` passed all active, historical, package-install, and documentation checks. Publish workflow `36329064232` created GitHub Release `v1.1.0` from `c789296ab7767affdd51555a9f1730a8ed80a0b3`.

Published assets:

- `img2drawing-1.1.0-py3-none-any.whl` — SHA-256 `6cfba97ab176d32e897803ce64f550656cf01730e03073958d5bd06a011e3cb0`;
- `img2drawing-1.1.0.tar.gz` — SHA-256 `6fd6614060065490c2087a93697f4c780a4b4de98778c79114f6cf9ba3a2dea6`;
- `CONTRACT_FREEZE_V1_1_0.json` — SHA-256 `c25b3191d92d12ef326a96ea2a8562a95df5c0459fd51e40d39453028ec764bf`.

The S03 gate remains user-accepted; no class-level visual-quality PASS was measured.

## Selected v1.2.1 release authority

`docs/releases/v1.2.1.md`, `dev/release/vnext/CONTRACT_FREEZE_V1_2_1.json` and `dev/release/publish/v1.2.1.json` define the bounded promotion. PR #77 measured synthetic replay and swatch QA; PR #78 adds real-session diagnostics. The independent visual gate is deferred, not passed. v1.3.0 starts with a pinned evaluation protocol (S00), then observation, construction, stroke authoring, tonal inspection, semantic groups, cleanup, independent comparison and release validation. See `ROADMAP.md` and the Work OS parent WK-110.

## Published v1.2.0 release authority

v1.2.0 is described in `docs/releases/v1.2.0.md`, the additive freeze
`dev/release/vnext/CONTRACT_FREEZE_V1_2_0.json` and the manifest
`dev/release/publish/v1.2.0.json`. The main-CI-gated publish workflow creates the GitHub tag and release artifacts. The selected M02 scope preserves renderer v11; fresh portrait and large-GIF peak-RSS gates remain NOT_RUN.

## Published v1.1.1 release authority

The release is declared by `dev/release/publish/v1.1.1.json`, with human-facing notes in
`docs/releases/v1.1.1.md` and additive freeze
`dev/release/vnext/CONTRACT_FREEZE_V1_1_1.json`. The manifest-driven publish workflow requires
green main CI before creating the GitHub Release and building wheel/sdist assets.

## Historical B18 boundary

At the B18 implementation freeze, the product foundation was **frozen through B18** and the formal **D01–D06 not started** campaign was still future work. Those phrases are historical evidence only and do not describe current sequencing.

## Authority map

- current mutable state: **this file, `STATUS.md`**;
- product sequencing and closure criteria: `ROADMAP.md`;
- instruction-graph attention cleanup slices A–E: `INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md`;
- v11 quality execution plan: `V11_QUALITY_CONTROL_SLICE_PLAN.md`;
- v11 redesign rationale: `V11_QUALITY_CONTROL_REDESIGN.md`;
- selected stable: Git tag / GitHub Release `v1.2.1` (publication gated), `dev/release/publish/v1.2.1.json`, `docs/releases/v1.2.1.md`, and `dev/release/vnext/CONTRACT_FREEZE_V1_2_1.json`;
- previous published stable: v1.2.0 and v1.1.1 remain frozen at their existing tags, manifests and contract freezes;
- historical structural release: Git tag / GitHub Release `v1.1.0` + `dev/release/vnext/CONTRACT_FREEZE_V1_1_0.json`;
- historical published stable: Git tag / GitHub Release `v1.0.3` + `docs/releases/v1.0.3.md`;
- exact stable candidate: `dev/release/vnext/V1_0_3_STABLE_PROMOTION.json`;
- immutable v1.0.3 contract: `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- G01 evidence: `dev/dogfood/g01-gesture-rc2/README.md`;
- G02 evidence: `dev/dogfood/g02-broad-pencil-v11/README.md`;
- immutable v1.0.2 snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`.
