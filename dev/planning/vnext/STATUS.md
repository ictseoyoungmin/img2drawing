# img2drawing current status

Updated: 2026-11-28

```text
PUBLISHED STABLE:   v1.5.0 · actual tag and four uploaded assets observed
SELECTED RELEASE:   v1.5.0 · published; earlier release records remain immutable
RELEASE TAG:        v1.5.0 · 94770798cee2838d4378fe9eb77f96f18085fa72
CURRENT SOURCE:     1.5.0 · optional layered editing and exchange
CURRENT RENDERER:   img2drawing-pencil/11 default · normalized graphite v1/v2/v3 and opt-in mixed-media v1/v2/v3
RENDERER POLICY:    one engine · immutable per-session material contracts · no automatic migration or v12
CURRENT WORK:      v1.5.0 S01–S07 CLOSED · practical evidence and actual publication recorded
S01 DESIGN:         CLOSED · historical v11 quality-control design
S02 INSTRUCTIONS:   CLOSED · historical anti-normalization implementation; further proof was user-accepted
S03 CAMPAIGN:      PASS / USER_ACCEPTED · class runs remain NOT_RUN; historical gate, not v1.4 comparison
S04 CLASSIFICATION: CLOSED / NO RENDERER CHANGE · historical v11 campaign
R1 REFACTOR:        CLOSED · one session/render/timelapse architecture; v11 golden preserved
S05 REPLAY BOUNDARY: CLOSED by R1 · historical v9/v10 exact authority: img2drawing==1.0.3
GRAPH CLEANUP:      Slice A–E CLOSED; conditional mixed-media leaves are governed by the same graph checks
PACKAGE VERSION:    1.5.0
HISTORICAL REPLAY:  existing release tags/freezes remain immutable pixel authority
MAIN RELEASE CI:    SUCCESS · run 46061608993 at the tagged main SHA
PUBLISH WORKFLOW:   .github/workflows/publish-release.yml
PUBLISH STATE:      PUBLISHED · workflow 46061846831 SUCCESS · four assets uploaded
```

## Authority contract

This file is the **canonical point-in-time development status** for mutable `main` work.

Authority is intentionally split by purpose:

1. `STATUS.md` — current point-in-time state: what is ACTIVE, BLOCKED, READY, CLOSED, or NOT_RUN now;
2. `ROADMAP.md` — sequencing, slice definitions, dependencies, and closure criteria;
3. `INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md` — bounded execution plan for the current instruction-graph cleanup slices A–E;
4. release tags, freezes, manifests, and release notes — immutable historical release authority.

`ROADMAP.md` may explain why a state exists, but it must not silently override this file's current-state label. If the two diverge, update them in the same bounded documentation slice; do not create a second current-state truth.

## Published v1.5.0 release checkpoint

- User selected optional layered editing for casual line art, hand-drawn studies and professional
  revision/exchange on 2026-11-28. [Design](V15_LAYERED_EDITING_PLAN.md) ·
  [Work OS](https://app.notion.com/p/425c6a3b5bf181c5a45dd7d037572ebb).
- [PR #124](https://github.com/ictseoyoungmin/img2drawing/pull/124) integrated the implementation
  into `dev/v1.5.0-layered-editing` as `b1ca145` from published main `a3921fb`.
  [Integration CI](https://github.com/ictseoyoungmin/img2drawing/actions/runs/46051134484) passed
  **844 active**, **49 runtime** and **45 Pillow 13 replay** checks, plus package, installed API,
  documentation, instruction graph and historical/repository gates. These runs overlap.
- S01–S05 are CLOSED: native layer actions, isolated composition with exact neutral conversion,
  guarded mixed transforms and PNG/ORA exchange. Real retained 859-action graphite and 654-action
  ink-only mixed-profile drawings preserve RGBA pixels across released 1.4.0, unlayered candidate
  and neutral conversion. The independent small-geometry installed worker verified optional
  editing/export and native resumption without the old output folder.
- [PR #125](https://github.com/ictseoyoungmin/img2drawing/pull/125) merged at `3bdce30` after
  [exact-head CI](https://github.com/ictseoyoungmin/img2drawing/actions/runs/46058543138) passed
  851 active, 49 runtime and 45 Pillow 13 replay checks plus package/repository gates. Sparse
  occupied-alpha composition preserves exact old-path pixels with unchanged limits; the original
  27-node page uses 230,710,832 rather than 348,340,985 working-pixel operations.
- S06 is CLOSED with stated limits. The installed manga workflow finished at cursor 1178 with
  27 native nodes, 921 ink/area/tone elements, seven retained inspections and three resolved
  material corrections. Independent visual review accepted the specified correction scope;
  hair, hand, cloth, ruin and tone simplification remain artistic limits.
- Both PNG and ORA native handoffs resume and reproduce exact final RGBA with original-path
  reads blocked. Full-span replay covers 0→1178 every 16 actions: all 75 staged and decoded GIF
  frames match, as do eight independent pixel/state rerenders. These are sampled frames.
- Actual Krita 5.2.9 document-engine opening/editing verifies all 23 raw paint layers and
  non-opacity structure. Baseline/edited KRA reopen exactly; fractional opacity import and
  ORA re-save quantization are measured. Native→Krita differs at 351,807 pixels, max 79,
  mean RGBA8 0.98724270, including mild broad tone brightening. This is not pixel-exact external
  interchange or GUI verification. [Release notes](../../../docs/releases/v1.5.0.md) give the
  complete scoped comparison and working-file guidance.
- S07 is CLOSED. Stable selection [PR #126](https://github.com/ictseoyoungmin/img2drawing/pull/126)
  and main promotion [PR #127](https://github.com/ictseoyoungmin/img2drawing/pull/127) passed
  exact-head CI. Main `94770798cee2838d4378fe9eb77f96f18085fa72` passed
  [push CI 46061608993](https://github.com/ictseoyoungmin/img2drawing/actions/runs/46061608993),
  including 851 active, 49 runtime and 45 Pillow 13 replay checks and package/repository gates.
  [Publisher 46061846831](https://github.com/ictseoyoungmin/img2drawing/actions/runs/46061846831)
  succeeded. The actual [v1.5.0 Release](https://github.com/ictseoyoungmin/img2drawing/releases/tag/v1.5.0)
  is neither draft nor prerelease; its tag targets that tested SHA, and wheel, sdist, standalone
  skill ZIP and contract freeze are all uploaded. Publication was observed at 2026-11-28
  05:11:23 Asia/Seoul. The uploaded freeze digest matches the selected source file.
- Normal is the initial blend mode. Additional modes need separate P1 verification; PSD and a
  visual editor remain P2. Raster edits do not become native strokes. Existing simple drawing,
  material contracts, development metadata and historical release records remain available.
- Layer PNG reflattening can differ from the exact merged image; manifests measure the runtime
  difference. History cursor undo/redo retains observations and rejects branches that would
  orphan audit evidence. Layered timelapse uses canonical rendering.

## Published v1.4.0 release checkpoint

- Selected scope: Multi-Medium Drawing, developed from v1.3.1 maintenance main `820c88c` on `dev/v1.4.0-multi-medium-drawing`. [Design contract](V14_MULTI_MEDIUM_DRAWING_PLAN.md) · [Work OS](https://app.notion.com/p/424c6a3b5bf1814ca9abe1ba2e3b60b1) · [release notes](../../../docs/releases/v1.4.0.md).
- S01–S04 are CLOSED (70% weight): shared mixed contract, G-pen/fineliner, brush/solid contours/white ink, and editable dot screentone. Default graphite v11 and older opt-in contracts retain their pixel semantics.
- S06 final integration includes S06e [PR #121](https://github.com/ictseoyoungmin/img2drawing/pull/121), which fixes observed Pillow 13 Fast parity failures for both ink and graphite using canonical-dimension downsampling on Pillow 13+ or unknown versions, while retaining the verified guarded crop path before 13. Incremental composition/cache and dirty delta output remain. merged as `5f91bbe6ff47609e6457618081e368b019a14d99`; exact-head [PR CI 46017430613](https://github.com/ictseoyoungmin/img2drawing/actions/runs/46017430613) and push CI 46017419474 passed **679 active + 49 runtime checks**, with **45** additional Pillow 13 replay tests. [Stress 46017430538](https://github.com/ictseoyoungmin/img2drawing/actions/runs/46017430538) passed all 680 lossless frame checks, eight independent canonical sample cursors, final/GIF checks, and exact official-v1.3.0/candidate graphite comparison across all 680 frame hashes with identical GIF bytes. Mixed actual 654-action/165-sample replay is canonical RGB/state exact with original final preserved; graphite **216/216** decoded RGB and independent state matches against the official v1.3.0 installed canonical export, with original checkpoint/final unchanged. The separate parent canonical export completed all 216 samples after the worker budget. Earlier #118 and private 904/563-action measurements below remain historical evidence, not timings of the final resampling implementation.
- S05 is CLOSED (10% weight): fresh mixed worker completed 654 actions, 13 observations, 8 inspections, 3 corrections, current finish, resume PNG equality and all 165 canonical GIF samples within its recorded budget. Parent independently checked installed wheel bytes, retained evidence, resume/final, sample hashes and GIF.
- S07 comparison and release review are complete: mixed candidate received qualified acceptance and overall preference; the official v1.3.0 graphite drawing was rejected for uneven value development. Pose/hair tie and a modest local graphite face advantage are retained. Geometry/material/uncertain residuals remain explicit in the [review ledger](../../benchmarks/s07_worker_protocol/REVIEW_2026_11_27.md). Graphite completed 859-action drawing/finish/resume within budget, but its GIF required post-budget parent verification after the runtime failure; this is not worker-budget GIF success. Token usage is unmetered. Final release closure is established by successful main CI and the actual four-asset GitHub Release, not this source declaration alone.
- S07 material comparison is measured: eight authored paths / 328 points retained exact geometry; novel area/tone operations assessed separately. Independent blinded material review accepted the bounded demonstration without an overall preference. This does not certify likeness, figure construction or general artistic improvement.
- #119 sealed-input preparation merged `1e34ecb`; #120 hardened installable wheel names, provenance/no-overwrite behavior and mixed freeze validation, and added the material probe. #120 merged `6617b6189a9e2ef224f78ab96341184d4931522d`; exact-head PR/push CI `46008369576` / `46008361133` passed 672 active + 44 runtime checks and package/docs/graph/history gates.
- Reproducibility boundary: the local Pillow 13 / NumPy 2.3 environment showed five historical golden differences. The unchanged code and fixtures passed 46 focused golden/release/packet checks under Pillow 12.3 / NumPy 2.2.6, with hosted Python 3.10 CI passing in the verified environment. Do not extend exact hash claims to untested library versions.
- Maintainer authorization on 2026-11-27 covers completion and release, without a research waiver. The v1.4.0 manifest selects publication after green main push CI; the actual [GitHub Release](https://github.com/ictseoyoungmin/img2drawing/releases/tag/v1.4.0), tag, target SHA and uploaded wheel/sdist/skill ZIP/freeze are publication authority. Development CI and metadata preparation alone do not establish that publication occurred.
- Existing releases/freezes remain untouched. Private references, authored coordinates, sessions and large outputs remain outside Git. Release closure binds the measured comparison and S06e replay correction to the new version; no second drawing runtime or automatic geometry generation is introduced.

## Historical v1.4.0 implementation checkpoints

The following dated implementation observations retain their original measurements and provisional labels. The release checkpoint above owns current S05–S07 state.

- Target: v1.4.0 Multi-Medium Drawing; branch `dev/v1.4.0-multi-medium-drawing` original design from stable `fdaf6b1`; synchronized to v1.3.1 maintenance main `820c88c`.
- [Design contract](V14_MULTI_MEDIUM_DRAWING_PLAN.md) · [Work OS](https://app.notion.com/p/424c6a3b5bf1814ca9abe1ba2e3b60b1).
- S01 CLOSED: #107, #108, #109 merged; integration head 4663a14, CI 45976885593 SUCCESS (517 active + 44 runtime tests in final PR CI). Typed ink geometry, mixed history/profile, canonical composition, preview/apply/resume, selective graphite lifts and canonical GIF vertical path verified. S02–S04 CLOSED; S05 REVIEW; S06 WIP; S07 OPEN. Weighted closed gates 70% (4/7); implemented/mechanically verified S01–S05 80%.
- v1.3.0 final main CI 473 active + 44 runtime passed, release workflow succeeded, 4/4 assets. All nine v1.3 tasks CLOSED: S01–S06/S08 evidence-based (80% weight), S00/S07 USER_ACCEPTED (20%, independent comparison/high-resolution performance NOT_RUN/uncertified). This does not reopen them.
- S02 CLOSED: #110 and #111 merged; latest integration 684ca8a, PR CI 45979974212 and merge CI 45980250961 SUCCESS (554 active + 44 runtime on #111). G-pen/fineliner, adaptive recipes and explicit miter/bevel, butt/square, point tapers. Mixed-media-v2 defaults for new mixed sessions; v1 and legacy exact contracts preserved.
- S03 CLOSED: #112 merged 77e8ca0, PR CI 45983056787 and merge CI 45983382282 SUCCESS (572 active + 44 runtime). Wet brush, explicit cubic/solid contour, white paint and guarded ink transforms. Existing profile pixels preserved.
- S04 CLOSED: #113 merged 1e178b1; PR CI 45984215468 and merge CI 45984670001 SUCCESS (606 active + 44 runtime). Typed calibrated dot screen, page-fixed phase and gradient, bounded tile evaluation, mixed-media-v3. Older contracts unchanged.
- S05 #114 merged 46180ad; PR CI 45986027734 and merge CI 45986307849 SUCCESS (611 active + 44 runtime), installed guide example PASS. A maintainer-supplied independent Agent session contains 563 explicit ink additions (287 areas, 213 paths, 63 screens), 30,704 geometry samples, no inspection, correction or finish record. Private diagnostic rerender matched its final RGBA hash; no GIF provided or full installed resume verified in that review. Partial independent-use evidence, S05 REVIEW remains (not complete worker loop or artistic PASS). No private source/session assets retained in Git.
- S06a #115 merged 68f9b8f; PR CI 45992266141 SUCCESS (616 active + 44 runtime). Validated incremental prefix, sealed rollback references and serialization reuse; exact 64 decode calls for 64 append actions tested. Private 563-action single-commit model predicts 317,532 -> 563 decode calls, not an elapsed-time claim.
- S06b #116 merged 05ce36b, PR CI 45992848433 and merge CI 45993275822 SUCCESS (626 active + 44 runtime). Conservative edge sweep, diagnostic indices, explicit Registration.fit, sealed scalar validation. Private pair-test evidence unchanged: 2,409,247 -> 752 predicate calls, 2.0344s -> 0.01636s; not whole-runtime speed.
- S06c #117 merged b34b63c, PR CI 45994768035 and merge CI 45995137892 SUCCESS (637 active + 44 runtime). Exact incremental opaque ink-only replay, independent final PNG, state/RGB frame hashes. Mixed graphite/eraser and transparent histories retain canonical fallback.
- S06d local evidence from the supplied development ZIP: a 904-action authored portrait, 2048² SS2, 227 frames, 6 inspections, 2 corrections, current finish and resume parity; synthetic 1358 actions/680 frames each for ink and graphite-v3 control, same environment. Ink vs graphite: author 1.175/18.532s, full Fast export 53.284/48.116s, whole measured execution 63.943/113.730s, peak RSS 446784/481668 KiB. The graphite control uses explicit area outlines, not equal appearance or separately installed v1.3.0. These are local measurements, not universal speed guarantees. Private old 563-action session restored with actual development runtime: 142/142 lossless delta hashes, final original RGBA digest and GIF tolerance passed. No private coordinates/assets committed.
- S06d candidate: packed one-bit native alpha patch cache (32 MiB retained payload, 2048 entries), allocation-free bounds preflight and mark-major dirty recomposition. All renderer/profile/session digests unchanged; preserve exact pixels and existing resource gates. Private candidate parity: actual 904-action/227-frame and 563-action/142-frame full runtime replays, every RGB/state hash and encoded GIF SHA-256 equal before/after; final RGBA hashes unchanged. Portrait export 46.281 -> 35.925s, patch misses 6416 -> 772, evictions 6403 -> 0, retained cache peak 33553976 -> 18815792 bytes, parent peak RSS 334788 -> 338668 KiB (not a universal RSS reduction). Old 563 export 11.320 -> 11.100s, misses 571 -> 563, evictions 463 -> 0. Local source-runtime measurements only. Reproducible public synthetic stress harness and pinned v1.3.0 wheel comparison added; run outcomes and candidate CI pending.

## Historical v1.3.1 maintenance checkpoint

- v1.3.0 was published from `fdaf6b1`; main CI `45870744957` passed 473 active + 44 runtime tests, publish `45871125462` succeeded with 4/4 release assets.
- Maintainer closed all 9 v1.3.0 slices: S01–S06/S08 verified (80% weight); S00/S07 USER_ACCEPTED (20%, independent six-class comparison and extended high-resolution performance NOT_RUN/uncertified). No remaining mandatory v1.3.0 research gate.
- PR #98 closed without merge; normalized-v4 is NOT shipped. Existing v11/default and normalized v1/v2/v3, contact-width, selective lift and overlap diagnostics remain. The one-off portrait handoff branch is not a product feature; its pinned runtime is already in main. See [branch disposition](../../docs/v131-branch-disposition.md).
- v1.3.1 only synchronizes release authority, strengthens freeze validation and retains manual tonal QA. No runtime change besides version. Main promotion remains CI-gated.
- At this maintenance checkpoint v1.4.0 was still a future design. Current implementation and release evidence are recorded in the v1.4.0 checkpoint above.

## v1.3.0 development checkpoint (historical)

Scope: development evidence before the v1.3.0 promotion; not the v1.2.1 release.

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
- #93 ordered lift integrated (3cceb01), final PR/push CI PASS (385 active + 44 runtime checks). Pre-integration research: curved-hair study with a new explicitly authored 184-action cropped portrait base (same state/pixels in normalized v1 and experimental v2), constant hard/soft proposals rejected, 17 profiled lifts accepted in separate 201-action v2 session. Matched 15 hair paths, 5×5 start/crest/end mean lightening .3759/.3868/.3543 constant vs .0019/.1805/.0019 profiled; endpoints taper, crest weaker; not a likeness or natural hair quality PASS. Existing v11/v1 identities/default remain unchanged; new contract/digest, explicit pressure and bounded sample count; older runtime refuses v2. Local focused 69 tests PASS including 10 new cases. 52/52 sampled Fast replay hashes exact, max decoded channel 10, max frame mean 2.98203, zero tolerance violations, resume and preview/commit exact. Private source/reference/output not committed. Long-session footprint performance, independent comparison and artistic residuals remain open. This study alone does not justify stable release promotion.
- Maintainer-authorized development integration: #94 merged `1a2c3f9` (head `92633c1`, CI `45807705710` SUCCESS), optional pressure-shaped lift contract with bounded slab scratch and exact footprint regressions, synthetic 1920×1080 output / 3840×2160 working raster wide lift, edit/resume, every-cursor Fast/Canonical parity and GIF export. #95 merged `547dc95` (head `80c4ce2`, CI `45806841684` SUCCESS), form-first clump value guidance and blinded comparison rubric. Both features verified present in the combined branch. Combined-head push CI `45809282626` was in progress at integration verification. Legacy v11/v1 defaults and identities preserved. This is development integration, not release or independent visual acceptance. At integration, new portrait render and independent comparison were NOT_RUN; long-session high-resolution RSS/throughput remained unmeasured.
- Developer-authored form-first portrait follow-up: attached skill ZIP verified to contain #94/#95 implementation and guidance; actual fresh 420×476 crop study uses the normalized v1 profile (SS3) to isolate authoring. 160→454 actions (389 adds, 52 deletes, 13 soft lifts); final 58-mark preview/apply state and pixel digests exact. All 115 every-four regenerated Fast sample hashes match, all decoded samples within existing GIF tolerance (max channel 10, max frame mean 3.024), nine selected Fast/Canonical comparisons exact. Export wall 15.49 s, measured Python peak RSS 230860 KiB; relocated compact package resumes and reproduces final pixels exactly. Approximate selected crown patch-chain darkness .271→.549, adjacent variation .333→.573 (reference .370); neck adjacent variation .165→.361 (reference .073). Better directional read, but continuity, likeness and clump overlaps remain unresolved. Not independent visual PASS; original full-resolution source not recovered, pressure-shaped lift not exercised in this v1 study, high-resolution long-session RSS remains open. No private reference, coordinates, session, or outputs committed. Combined development documentation head `e1b20a0` CI `45809363939` SUCCESS.
- Developer continuity follow-up: current public observation/construction/authoring/tonal implementation audited against original design. S01 geometry measurements and S03 stroke operations are implemented; S02 exposes explicit projected ellipses, asymmetric sections and linear envelope guides, but high-level volume/attachment ergonomics and genuine 3D projection are not implemented. Curve control points are sampled into explicit strokes, not persisted as editable parametric objects. Group transform preserves material widths/pressure; tonal inspection is diagnostic, not automatic geometry or tone solving. These limits do not reopen the already accepted bounded implementation gate, but remain candidates for future refinement. Actual 454→472 action normalized-v1 portrait correction: 7 retired strokes, 5 edited strokes and 6 new authored strokes across two preview/apply batches, exact state/pixel verification. Canonical patch-chain adjacent variation crown .573→.315 (reference .370), neck .361→.053 (reference .073); neck coverage 76.3→81.3%, crown saturation 37.3→32.0%. Mean neck tone remains pale, hair protected area remains dark, and approximately 14.2% of added neck interval darkness lies outside the plan; not an artistic PASS. 119 frames action-0→472 every-four export, final match, 13.77 s, Python peak RSS 228184 KiB. All saved delta-pack frame hashes and GIF tolerance checked (119/119; max channel 10, max frame mean 3.028), but separate checkpoint re-render audit timed out. No private coordinates, source images or outputs committed. S00/S07 independent evaluation and v2 high-resolution long-session evidence remain open.
- Developer-authored PR #96 candidate dogfood on pinned `3f76525`: new full-body reference study (480×1105 crop, SS2, normalized-v2) uses eight explicitly authored ProjectedVolumes, 32 guides added then retired, 325→517 actions, 16 recovered and edited face CurveDefinitions, one pressure-shaped lift, four preview/apply pixel/state exact checks. Two first tonal proposals rejected; replacement and later edits reduce selected across-trouser adjacent variation .438627→.171426 (reference .143547) but knit variation .367150→.351856 (ref .221974), reversals 1→3; likeness, garment bands and weak fine details remain. All 131 every-four sample hashes regenerated from checkpoint and match; nine selected Canonical comparisons exact, decoded max channel error 14, max sample mean 2.920186, zero tolerance failures; export 14.55 s, Python process peak RSS 198872 KiB. Non-human pot crop (102×116 enlarged 4×, 408×464) uses explicit orthographic camera ellipse and projected rim/body attachment, center gap 6.403124→0 px, 7 guides, 3 guide edits, 72 actions, exact preview/apply, 19/19 regenerated sample hashes, four selected Canonical comparisons exact, decoded max channel 25, max sample mean 2.627085, zero tolerance failures, export 1.79 s. Both relocated checkpoints reproduce exact final PNG. Four runtime file blob hashes match the pinned candidate. This is actual developer dogfood, not independent comparison, automatic 3D reconstruction or artistic PASS. No private images/geometry/sessions/large artifacts committed. #96 remains Draft; S00/S07 WIP, S08 OPEN, 6/9 (75%).
- Maintainer-approved #96 integrated `af875b2`; merge CI `45820861728` SUCCESS. Follow-up #97 integrated `5c3a4ac` (head `d2563dc`; PR `45821842233` and push `45821833592` SUCCESS). Opt-in normalized-v3 `ContactWidthProfile` scales resolved graphite diameter by explicit normalized arc knots; authored geometry/pressure independent, width metadata preserved through retune and reparameterized on split, ordinary/default v11 and v1/v2 contracts unchanged. `TonalBandProbe` reuses matched strip-chain/preview/cache diagnostics, no automated artistic decision. Local 24 focused tests (15 new + 9 prior), all 18 changed blobs equal tested local source. Actual previous v2 517-action session independently re-rendered under updated runtime and RGBA digest EXACT; cached canonical strip analysis detects remaining knit and trouser bands. Separate real knit crop 290×339 v3 SS2: 54-action base, 14 edits, 68 total; width-only rejected (across variation .26919→.38950). Combined widened overlap and shaped widths accepted as a limited diagnostic (across variation .23213, mean darkness .10839→.17590; reference variation .18753). Matched widened constant vs width-shaped candidate: outside added darkness fraction .142394→.055795, protected mean .13407→.11466; actual target mean .16096→.15045. Rails, weak values and material realism still unresolved; no width-only or artistic PASS. Preview/apply exact, resume/relocated package PNG exact; all 18 samples Fast/Canonical/RGB hash exact, max GIF channel 10 and frame mean 3.42615, zero tolerance failures; export 3.57 s. Original checkpoint not migrated; no private references, paths, sessions or large outputs committed. S00/S07 remain WIP, S08 OPEN; high-resolution long-session v3 performance and independent visual comparisons NOT_RUN.
- Research #98 head `85b12ed` (Draft, not integrated): explicit side-of-pencil contact recipe on a separate normalized-v4 opt-in contract. Tangent-aligned compact optical sweep and smooth transverse shoulder replace the narrow dark core only for marked broad strokes; unmarked v3 render and older contracts/digests/cache keys retained. Local 35 focused tests (11 new + 24 existing) PASS; all 15 changed Git blobs match tested local files. Controlled spacing 18px relative strip variation .077→.167 (worse); 24px .149→.028 (better). Reused PR #97 manually authored knit paths (not fresh worker), radial v4 unmarked candidate PNG exactly equals old v3 PNG. Three fixed-material side shoulders and three explicitly calibrated width/opacity candidates; selected .85 shoulder, +12% width and +18% opacity on five front paths, 54→68 actions, exact preview/apply and relocated resume. Across-strip mean .175904→.178978, total adjacent variation .232127→.279405 (worse), mean absolute second difference .016591→.014063; along second difference .004646→.003191; outside added darkness .055795→.061704 (worse). Side-only .85 is paler (.137787); multiple other candidates rejected. 18/18 every-four sampled Fast/Canonical/RGB hashes exact; GIF max channel 10, max frame mean 3.426881, zero tolerance failures, export 3.62s. No proof of general superiority or independent artistic acceptance, no high-res performance measurement. Existing default and source sessions unchanged. CI at observation: pull_request 45823835420 in_progress; push 45823824749 in_progress. #97 final integrated documentation CI `45822609914` SUCCESS. S00/S07 WIP, S08 OPEN, 6/9 (75%).
- Follow-up #99 `f980d65` (Draft, not integrated): read-only selected graphite contact overlap inspection uses actual canonical per-stroke supersampled alpha patches in an explicit ROI; reports support, multiple contacts, pair overlap, strips and analytical alpha union. Ignores unselected marks and ordered lifts, not causal final-raster attribution. Renderer/history unchanged, bounded raster-work estimate, 32 local focused tests PASS (8 new + 24 existing), six changed blobs match tested local source. Existing v3 68-action knit five selected contacts in front-plane ROI: 0 uncovered, .818662 multiple coverage; uneven strip overlap, not proof of cause. Three opacity-only previews rejected, original 68-action state retained (best variation .232127→.222424 but mean .175904→.159601, weak visual change). Copied 420×476 normalized-v1 portrait: manually observed landmark/ratio/axis comparison and explicit spline recipes, first preview rejected; second 472→553 actions (40 retire, 3 retune, 38 authored curves). Approximate unblinded normalized RMS .019756→.012991, mouth axis residual 1.6201°→0°, selected three lower-mouth contacts before/after multiple fraction .113993→.016527; not independent likeness or causal proof. Preview/apply pixel/state exact; 38 curve definitions restored, historical 472 PNG exact. 140/140 regenerated Fast sample hashes, 7/7 selected Canonical pixel matches, decoded GIF max 10 and max frame mean 3.035239, zero tolerance failures, export 14.51s, peak process RSS 266492 KiB; both portrait/knit relocated ZIP resumes reproduce final pixels. Facial expression, value continuity, and likeness remain unresolved. No private source imagery, geometry or large outputs committed. #98 PR/push CI SUCCESS but research remains Draft due to mixed artistic evidence. #99 CI at observation: pull_request 45825582454 in_progress; push 45825573394 success. S00/S07 independent comparison NOT_RUN, high-resolution long-session performance unresolved, S08 OPEN; 6/9 (75%).
- Portrait fidelity follow-up #100: specialist facial construction, feature geometry, expression, facial values, and portrait-local likeness review, including readable faces within full figures; explicit `compare_portrait_landmarks` and `portrait_likeness_packet` with named local groups and existing ratio/axis comparison (no recognition, automatic detection, score or rendering/history change). Ported earlier draft to current source instead of overwriting the newer runtime. Implementation `d1aa001`, 35 focused tests PASS (11 new, 24 prior), 14 original changed blobs match tested source. CI `45833511320` failed on unchanged exact export allowlist, corrected assertion in `60c04e1`; reruns `45833808801`/`45833797900` pending at checkpoint. Developer-authored full-figure face REOPEN from 623 to 787 actions, normalized-v2 unchanged: four prospective alternatives, 53 retire + 111 explicit curves, selected preview/apply and resumed curves exact. Prior 623 PNG exact and body unchanged; changed pixel bbox [172,48,298,199]. 198/198 regenerated samples, 7/7 selected Canonical matches, decoded max channel 10/max frame mean 2.93431, zero tolerance failures, 21.15s export, process peak RSS 272936 KiB. Extracted package final PNG exact. Approximate manual nonblind 11-anchor face-width RMS .028694→.006627 (91px local span; 1–2px reading uncertainty); not likeness score, does not measure nose shape/eye apertures/skin/hair. Actual likeness, facial expression and hair material remain unresolved. No private reference/geometry/output committed. #100 Draft pending full CI and integration. #98 research and #99 Draft unchanged. S00/S07 independent comparison and high-resolution long-session evidence NOT_RUN, S08 OPEN; 6/9 (75%).
- #100 integrated `1bc7df3` after both CI runs on `e356376` passed (`45845134490`, `45845118134`). The follow-up restored the original face-cross-axis orientation rule and explicitly registered the new instruction leaves in the existing boundary tests; it did not weaken the tests. Merge-head CI `45845821755` was in progress at observation. Private 787-action face follow-up: a broad prospective batch (45 retire, 15 material edits, 52 additions) softened some cheek/lip contacts but lost pupil definition; rejected. A narrower prospective batch (23 retire, 17 material edits, 32 additions) retained dark eye contacts and reduced some hard lip/jaw edges but still failed the reference expression and whole-head likeness; not applied. One intermediate alternative timed out. Original action log, state hash, render profile and 787 final pixels verified unchanged; only observation metadata was added in the private copy. No new final/GIF or independent visual pass. Do not mistake additional low-resolution feature edits for a solved head; revisit the cranial/hair envelope and visible eye aperture, midface planes, tooth-plane silhouette at matched crop and whole-figure scales. #98/#99 unchanged; S00/S07 WIP, S08 OPEN, 6/9 (75%).
- #99 integrated `2f88931` after synchronizing its branch with `cdfd4f9` in `4ee2ce7`. Resolved overlapping public-surface and runtime discovery edits, retaining #100 portrait and #99 contact-overlap APIs. Public surface 20,957 bytes within 21,000-byte budget. Prior #99 PR/push and development CI passed; combined local focused overlap 8/8 PASS. At merge, fresh combined CI `45854269291`/`45854258972` and merge-head CI `45854507478` in progress; do not claim final integration CI success yet. #98 remains research Draft due mixed tonal evidence. Private drawing follow-up 787→849 eye-local correction, then 879-action derivative with 30 authored lettering strokes before the original 849 actions; neither changes skill source or renderer. No private drawing data committed. Independent S00/S07 and long-session high-resolution performance remain open, S08 OPEN, 6/9 (75%).
- S01–S06 feature implementation and regression gates CLOSED (75% of weighted plan, six of nine slices). S00/S07 WIP; S08 OPEN. No private images, answer coordinates or large outputs committed.
- Release decision (2026-11-27): maintainer authorized bounded v1.3.0 publication after CI. #104 merged at `7856946`; CI `45868789654` passed 473 active and 44 focused tests. S01–S06 retain their verified 75% weight; S08 promotion validation is pending main CI. S00/S07 independent artistic comparisons and extended high-resolution performance are deferred, not PASS. #98 remains separate research.

## Historical quality and release decisions through v1.3.1

These earlier decisions remain historical; the v1.4.0 release checkpoint above owns current status.

- `v1.3.1` is the selected maintenance release, gated by successful main CI and manifest-driven publication. v1.3.0 and earlier tags are immutable. Default renderer v11 and all shipped opt-in material contracts are unchanged. Independent artistic improvement was not measured; the prior tasks were closed by maintainer acceptance.
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
- v1.3 opt-in `11-opacity-normalized-v1`/`v2`/`v3` → explicit new RenderProfile, distinct digest required; no legacy automatic migration;
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
- selected candidate: `dev/release/publish/v1.5.0.json`, `docs/releases/v1.5.0.md`, and `dev/release/vnext/CONTRACT_FREEZE_V1_5_0.json`; publication remains pending actual GitHub Release/tag/assets;
- observed published stable: [GitHub Release `v1.4.0`](https://github.com/ictseoyoungmin/img2drawing/releases/tag/v1.4.0) and its unchanged manifest/freeze;
- previous published stable: v1.3.1, v1.3.0 and earlier releases remain frozen at their existing tags, manifests and contract freezes;
- historical structural release: Git tag / GitHub Release `v1.1.0` + `dev/release/vnext/CONTRACT_FREEZE_V1_1_0.json`;
- historical published stable: Git tag / GitHub Release `v1.0.3` + `docs/releases/v1.0.3.md`;
- exact stable candidate: `dev/release/vnext/V1_0_3_STABLE_PROMOTION.json`;
- immutable v1.0.3 contract: `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- G01 evidence: `dev/dogfood/g01-gesture-rc2/README.md`;
- G02 evidence: `dev/dogfood/g02-broad-pencil-v11/README.md`;
- immutable v1.0.2 snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`.
