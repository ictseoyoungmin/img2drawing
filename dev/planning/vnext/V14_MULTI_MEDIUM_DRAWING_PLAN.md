# v1.4.0 — Multi-Medium Drawing design

Approved direction: 2026-11-27. Implementation contract proposal, not an implemented API.
Original design and comparison baseline: v1.3.0 / `fdaf6b15d3ce563789712be9206e6572dee812bd`.
Current implementation base: v1.3.1 maintenance main `820c88c5192f9425132386a7a64a78036776a647`; no drawing contract change.
Development integration: `dev/v1.4.0-multi-medium-drawing`. Work OS: [v1.4.0](https://app.notion.com/p/424c6a3b5bf1814ca9abe1ba2e3b60b1).
State authority: [STATUS.md](STATUS.md); sequencing and weights: [ROADMAP.md](ROADMAP.md).
Do not modify released tags, freezes, manifests or historical renderer outputs.

## 1. Problem and evidence

A v1.3.0 agent reported a two-panel manga-style drawing with 1,358 strokes, 15 groups,
680 frames at every 2 actions and approximately 57 seconds of playback. Its feedback
identified limits in uniform black ink and screentone. The supplied finished image
visually suggests graphite-like streaks in dark hair and water forms, and irregular
dark coverage. This is motivation, not a controlled material reproduction or proof
that all geometric/tonal residuals belong to the renderer. The original reference,
session, per-mark parameters and GIF have not been obtained here; figures are agent-
reported. Do not commit private inputs, answer geometry, sessions or large renders.

Current source at the pinned baseline:
- `core/action.py` validates new authored actions and explicitly requires a named
  pencil grade for stroke-producing actions; `core/tools.py` and
  `authoring/markmaking.py` resolve graphite-oriented ToolState and semantic presets.
- `core/ir.py` exposes Stroke/StrokeIR; `core/history.py` owns ordered stroke replay.
  Legacy `region.*` actions intentionally fail closed. `session/editing.py` derives
  authored elements from action provenance, `authoring/stroke_edits.py` supports
  guarded atomic stroke edit/preview.
- `render/contract.py` and `render/profile.py` bind immutable per-session material
  contracts; `render/pencil.py` composites a graphite canvas over paper.
  `timelapse/replay.py`, `dirty.py`, `patch_cache.py` and `export.py` assume stroke
  operations and graphite patches. Changing only presets is insufficient.
- `authoring/tonal_area.py` is observation-owned planning metadata, NOT a paint/fill
  command. Preserve that meaning; do not make existing tonal plans deposit pixels.

## 2. Scope and explicit authoring boundary

| Accepted feature | Explicit agent input / authority | Forbidden shortcut |
|---|---|---|
| Pencil / graphite | Existing authored strokes and existing immutable profiles | Change legacy pixel semantics or history |
| G-pen | Path, pressure/width, terminal intent and resolved ink state | Vectorize image edges or infer path from reference pixels |
| Fineliner | Authored path, calibrated constant diameter, cap/join choice | Automatic contour extraction |
| Ink brush | Authored path, contact width and opaque wet-ink intent; intentional dry brush only later | Substitute broad graphite or auto-paint source black regions |
| Solid ink area | Explicit agent-authored closed outer contour, optional explicit holes, ink state | Flood fill, bucket fill, region-growing, segmentation, raster mask import |
| White ink | Explicit path or explicit closed contour; deliberate covering mark | Erase or whiten source pixels automatically |
| Screentone | Explicit closed boundary and holes, dot pitch/coverage/angle/phase, optional authored gradient | Tone transfer, source-derived dot grid, image masks, automatic shadow selection |

Procedural rendering of an explicitly authored geometry is allowed; procedural
selection of what to draw from the reference is not. No tracing, image generation,
automatic hatching/fills or reference-to-pixel transfer. No private Pillow/OpenCV/SVG
workaround, arbitrary user raster upload as a mark, learned rasterizer or post-filter.
All visible output must be attributable to authored elements and ordered actions.
Observation/measurement remains read-only evidence. The Agent owns boundaries,
shape, occlusion, value hierarchy, line intent, highlight reserves and final quality.
Do not auto-close open contours, auto-infer holes or convert pencil plans into fills.
A mark can be corrected by the same observe/author/inspect/correct loop, not by rewriting
old history.

## 3. Architecture and compatibility contract (S01)

Keep one DrawingSession, one ordered authoritative CanvasHistory, one canonical
render orchestration, one public replay/export. Do not create a manga-only session,
second history, parallel persistent layer document, independent exporter or model
backend. The existing pencil implementation remains the legacy pixel authority.
New material kernels live under the existing render ownership and share validation,
composition and replay. Keep reference authority, inspection and semantic groups.

Proposed data model (names illustrative until S01 implementation freezes public
signatures):
- One resolved per-element material descriptor with immutable material/tool revision,
  media kind, authored path OR explicit area geometry, effective width/pressure or
  pattern parameters, explicit color/alpha, semantic role/part, observation/correction
  provenance, layer/order and stable element ID. Store the effective state, not only
  a preset label; reject unknown/ambiguous fields before history mutation. Keep
  legacy ToolState/pencil grade schema unchanged for legacy marks. Ink is not a
  fake pencil grade. No general plugin-defined executable material code.
- New opt-in mixed-media RenderProfile/contract identity and digest; proposed
  constructor `RenderProfile.mixed_media(...)` (implemented in S01). It pins the
  graphite sub-contract, compositing and every material/pattern revision that can
  affect pixels. Legacy default remains canonical v11; all published normalized
  variants and historical profiles remain readable under their original contracts.
  Unsupported mixed payloads/unknown digest must fail closed, including old
  runtimes. No implicit migration/reinterpretation of legacy histories. If a new
  session format is needed, version explicitly and retain old decoding/hashing path;
  no new default field may enter an old action/profile digest.
- Extend the existing ordered IR/history with discriminated authored elements
  for path marks and areas. Do not overload point pressure with contour data,
  fake thousands of strokes for dots, or revive retired `region.*` opcodes.
  Use versioned, explicit new operation names for area add/replace/retire; path
  strokes retain the existing APIs wherever compatible. One logical area is
  one identifiable, editable authored element, not an untracked bitmap. Choose
  exact schema/action identifiers in S01 after audit of session serializers,
  strict validators, state hashing, root surface and package tests.
- Provide atomic preview/apply, replacement, retirement and group membership
  against the same history. Preserve immutable prior cursors and stable references;
  changes invalidate dependent reviews. Preview carries cursor/state/action digest;
  commit either matches preview state and pixels or refuses stale input. Region
  transform updates explicit boundary and pattern coordinates under a declared
  rule. Unsupported edits fail explicitly; never silently approximate.
- Composition: preserve existing layer ordering and stable insertion order within
  layers. Under the mixed contract, path/area patches share this order.
  Pencil soft-lift is graphite-selective (including interleaved ink); use a
  canonical reconstruction of surviving graphite contributions when necessary,
  never erase ink because it overlaps a construction mark. Stroke/element retirement
  removes only its own contribution and reveals surviving underlying media.
  White ink is explicit opaque paint in the chosen layer, NOT alpha erase; it
  remains a white mark on a nonwhite/transparent canvas. Ink corrections use
  target element edit/retirement; optional typed path erase must declare target
  material and ordering, not inherit graphite lift silently.
- Every rendered pixel is produced from explicit action data and pinned deterministic
  math. Validate finite/bounded coordinates, pressure, widths, path sample count,
  contour/ring complexity, pattern frequency, supersampled work and memory before
  allocating. Invalid input/unknown fields/unsupported profile: atomic refusal.
  Color space, units, fill rule, sampling, antialiasing, tie-breaks and clipping
  are part of the contract; cache identity includes all relevant resolved state,
  profile and contract digest. No hidden randomness or source-image reads in
  render paths.
- Preserve legacy golden pixel/action/profile hashes, historical replay rejection
  policy and same one-package architecture. Add only intentional public capability
  discovery; expose capabilities by profile, with no ink feature under a legacy
  pencil contract. Keep the version 1.3.0 while planning; no promotion or manifest
  until S07 release approval.

S01 first vertical proof: select an opt-in contract, persist a minimal typed
path/area test element through new-action validation, history/state/hash/resume,
preview and canonical rendering; reject new elements under legacy contract.
Use synthetic tiny fixtures only. Establish format ownership, stable IDs, operation
dispatch and material-selective correction semantics before S02–S04 fan out.
If necessary, keep a new medium capability unavailable until its full route works.
All later slices require legacy golden and package/graph gates on their PR.

## 4. Tool contracts

### S02 — G-pen and fineliner

G-pen uses an explicitly authored path; pressure modulates geometric diameter,
not center opacity. Resample along arc length without changing intended shape;
smooth interpolated width, deliberate tapers, joins and sharp tips; no inherited
paper tooth, random hand jitter or graphite accumulation. A full-pressure stroke
has an opaque black interior (antialias only at edge). Support width knots and
existing curve editing, not automatic line hierarchy. Fineliner uses a fixed
diameter independent of pressure, explicit terminal/cap behavior; its intended
constant-width geometry must survive resampling and scale. Ink tone/color is
explicit black (initial palette: black/white only); no arbitrary color suite in
this release. Ink deposition and geometry parameters are resolved/persisted once.
Use existing curve/pressure helpers only where semantics match, do not repurpose
graphite opacity.
Acceptance: fixed/variable-pressure width swatches; measured monotone G-pen
diameter, constant fineliner diameter within declared AA measurement tolerance;
opaque interior, stable cap/join/taper/curve crossings; no halos or opacity seams
on same-black overlap; exact repeat/render/preview/resume on supported environment.
Compare same geometry using v1.3.0 graphite, separately label artistic judgment.

S02 implementation choice: keep the S01 opaque swept-disk kernel and its pixel
contract for original round/point paths. Maintainer-approved extension: miter,
bevel, butt and square are explicit styled-path geometry using normal strips,
local tapered-offset edge intersection and convex wedge unions. Round joins
in a styled path are local disk unions. Miter limit 1–16 (default 4) with
bevel fallback; reversal is flat for bevel/miter. Closed paths have a joined
seam and require matching endpoint width, default round cap declarations.
Styled paths are bound to additive mixed-media-v2, default for newly created
mixed sessions; styled_paths=False selects the unchanged v1 contract. Point
tapers retain the conservative original anti-swallow validation. Agent-authored polyline
corners and cubic-chain junctions are retained; pressure knots are inserted at
normalized arc positions. Straight constant-width paths do not need dense uniform
sampling. The optional versioned pen recipe is action provenance, validated
against the authoritative resolved InkPath on authoring/load and explicit read;
normal replay uses the resolved mark, not newly sampled geometry. No SciPy
dependency or additional raster engine is required for this bounded model.

### S03 — Ink brush, solid ink contour, white ink

Ink brush deposits an explicit black path with controllable width/contact and
shaped tip. Uniform interior, continuous turning path, no graphite mottling.
Separate intentional dry-brush research from this bounded wet-ink baseline.
Solid ink uses an explicit closed ring: validated finite vertices, at least
3 distinct noncollinear points, explicit closure, simple non-self-intersecting
ring; holes must be simple, strictly inside outer ring, non-touching/non-overlapping
with each other/boundary. Reject invalid rings rather than repair; fixed even-odd
rule and deterministic coverage/AA. Curves may be authored and sampled explicitly;
no pixel masks, contour discovery, seed point/flood fill or silent closure.
A separately authored outline is not automatically a fill; the agent chooses
each area and its holes. Add, replace, retire and transform by stable ID through
shared history, respecting bounds/order and atomic preview. White ink is a
distinct material/operation (explicit path or closed area), covering lower marks
instead of destructively lifting them; white over ink, white over tone, overlap
and later edits all obey history. Reserve paper holes intentionally when white
ink is not desired. Keep provenance.
Acceptance: uniform RGB/alpha interior and no unintended seams on brush overlap,
ring-with-holes with zero deposition outside coverage/holes away from AA edge,
edge clips, concavity, degenerate/NaN/self-intersection/touching rejection, rejected
batches leave history/state unchanged; white vs retire/lift tested on transparent
and nonwhite paper and mixed layer order. Preview/commit/resume/replay exact.

### S04 — Editable screentone

Start with analytic dot screentone. Each area includes explicit outer boundary,
holes, pattern kind=dot, pitch in canvas coordinates, normalized tone coverage,
angle, page-space origin/phase, optional explicit linear gradient defined by
start/end coordinates and coverage endpoints. No texture image or sampled
reference values. A deterministic lattice evaluates at working resolution, with
anti-aliased clipped masks and documented pitch limits, coverage transfer and
phase convention. Calibrate area fraction for the chosen dot family (avoid
claiming non-overlapping circles reach 100%); endpoints 0 and 1 map to transparent
and solid, respectively. Reuse the explicit ring validation from S03. Evaluate
local tiles/slabs and bounded work; no N-dot objects/history entries. Angle,
pitch, coverage, phase and gradient remain editable. Default phase is fixed in
page coordinates so adjacent equal tones align; explicit object-local anchoring
may be added only if persisted and tested, not inferred. For translate/group
transform, boundary changes and default page anchor stays fixed; reject unsupported
nonuniform transforms that cannot preserve the declared rule. Ensure no phase
jump on incremental recomposition. Patterns beyond dots/linear gradient, moiré
avoidance beyond bounded resolution rules, arbitrary textures and auto shading
are deferred.
Acceptance: measured coverage at specified pitches/angles/densities with
declared discretization tolerance; monotone linear gradient; 0/1 endpoints,
deterministic phase across adjacent tiles/crops/resume; no leakage to holes/reserves;
edit/delete/white-over-tone behavior, dirty bounds and sampled parity; budget
rejections for invalid/high frequency/too large work without allocation blowup.

### S05 — Skill and agent UX

Keep SKILL.md root routing, conditional expert leaves under existing markmaking/
style/output ownership and actual instruction graph CI budgets. A concise mixed
media/manga workflow covers light pencil construction, line hierarchy, G-pen vs
fineliner, form-driven ink masses, deliberate negative space/white highlights,
dot pitch/coverage relative to output, separate contour and shadow decisions,
selective graphite guide retirement and fresh comparison. No forced runtime stages;
croquis/pencil remain default when style unspecified. Use public discovery and
short example of actual supported mixed API (not invented placeholders).
Explain each edit/correction action and when unsupported, and distinguish
coverage diagnostics from artistic verdict. Add a reference authority rule:
agents must author closed contour/holes and pattern explicitly, may inspect
reference, never derive/trace a raster mask. Preserve existing graphite
TonalAreaPlan semantics. Keep skill attention budgets, no duplicate manuals,
private examples or large fixtures in deployable ZIP.
Acceptance: graph reachability, no orphan/broken links, skill/package allowlists,
fresh worker can discover available profile and tools without implementation source,
example actually executes/resumes and produces canonical final/GIF.

## 5. S06 — Replay, regression, install and performance

S01–S05 carry per-feature mechanical tests; S06 is final integration, not first
replay support. Audit all actual consumers: canonical render, inspection, preview,
completion/residual provenance, semantic groups, CanvasHistory state_at,
ForwardHistoryReplay, patch cache, dirty rectangles, exporter and manifest.
Fast must share material kernels/compositing and typed dispatch; cache keys and
invalidated dirty bounds include old/new region geometry, material, pattern,
output/profile and dependent coverage. Prefer conservative complete recomposition
or explicit canonical fallback until incremental parity is proven. Never silently
drop elements, flatten before history, change disposal/palette/loop or call a
fallback Fast. Legacy Fast/Canonical behavior and hashes unchanged. Mixed
unsupported explicit Fast rejects actionably, auto chooses only proven path.
All new authored actions appear from cursor 0 through latest (every_n default 4,
also test every 2 and every cursor), final independently rendered PNG agrees,
decoded GIF meets persisted tolerance; exact unquantized frame/state comparison
before GIF quantization. Transparent paper keeps canonical RGBA and documented
GIF background rule. Coalesced frame/duration and budgets tested. Use same
source/export API and no special manga exporter.

Regression matrix: pinned v1.3.0 baseline v11 and normalized v1/v2/v3 existing
fixtures; same checkpoint action/state/profile digest and PNG pixel exact;
no rewrite of historical release files. Mixed tiny fixture checks every cursor,
preview/commit/resume, edit/retire/erase/holes/white/overlap, cache isolation,
unsupported contracts, injected invalid actions and atomic rollback.
Benchmark synthetic representative 2048x2048 and >=1,358-action mixed session
with every-2 sampling (include 0/latest), and comparable graphite baseline.
Measure peak process RSS, wall/CPU, throughput, bytes and render parity/fidelity;
seal environment, supersample, budgets and thresholds before candidate run.
Do not claim real user 1,358-stroke session reproduced if unavailable. No hard
speedup or arbitrary memory target without measured baseline; if limits cannot
be met, report unsupported stress range and fail the relevant declared gate.
Retain compact metadata/hash evidence, not large artifacts. Verify wheel, sdist,
standalone skill ZIP in isolated environment and unchanged private-data boundary.
Require active suite, package/discovery, docs graph, growth and replay gates.

## 6. S07 — Compare and release decision

Compare (A) pinned v1.3.0 graphite and (B) mixed-media candidate with same authored
geometry where semantics are compatible. Freeze the actual reference scope,
canvas, explicit geometry, pressure/width intent, evaluation crops and environment;
document translations from graphite to ink without moving points. Separately
test authored area/tone primitives as new capabilities (not falsely called equal
geometry conversions). If the original session and authorized reference are
supplied, create an isolated derived copy, retain original session/hash, replay
end-to-end and compare; otherwise report controlled synthetic and new examples,
not reproduction of feedback. No copying source masks.
A separate fresh drawing comparison uses equal prompt/model/budget/reference,
isolated contexts and no answer paths. Include one manga-style composition
with figure/cloth/hair, overlapping effects, black masses and tone, plus a
graphite-only control. Compare anonymized crops and whole composition for line
hierarchy, clarity of black boundaries, hole/highlight intent, tone density,
contact/occlusion, likeness/form and overall aesthetic quality. Record time,
actions and token usage if metered, no automatic artistic score. Accept/tie/reject
by reviewer with residual ledger; classify geometry vs material. Record missing
evidence as NOT_RUN, not PASS. Mechanical gates are necessary but not artistic
proof. Release only after review and explicit maintainer decision; if a visual
campaign is waived, record USER_ACCEPTED and measured evidence separately.
Prepare version/docs/plugin metadata, new release freeze and publish manifest
only then; separate main promotion PR, green main CI, verify actual GitHub release
assets. Keep v1.3.0 immutable.

## 7. Bounded development workflow

Use independent feature PRs into the v1.4 development branch, not main. One
highest-impact slice at a time. S01 -> S02 -> S03 -> S04 -> S05 -> S06 -> S07,
with narrowly independent test/guide work allowed in parallel after contracts
are fixed. Each PR records changed ownership, reproducible tests and limits,
review status and a linked Work OS checkpoint; no large generated artifacts.
Track measured completion weights only when slice gates close; planned or
in-progress work is not completed. User-waived gates require separate
USER_ACCEPTED labeling, not fabricated measurements. No version bump,
renderer-generation counter, public feature claim or automatic publication
at design time.

Out of scope: color painting suites, arbitrary brushes/textures, full manga
editor/page layout/speech bubbles, new general raster layer editor, model-based
segmentation/tracing, automatic lighting/line extraction, new independent
renderer/session/exporter. These would require separate authorization.
