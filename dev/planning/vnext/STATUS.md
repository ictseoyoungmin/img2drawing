# img2drawing vNext status

Updated: 2026-09-01

```text
SYSTEM:   B00–B08 closed; B07 reopened and reclosed as B07-R1 (value authoring + session compaction)
ACTIVE:   none
NEXT:     third dogfood on an unseen subject, then activate B09
SKELETON: B09–B18 platform/release
CLOSED:   B00, B01, B02+B03, B04, B05 construction + canonical route de-anchoring, B06, B07, B07-R1, B08
NEXT GATE: fresh dogfood whose canonical session stays within ~2x the R23 baseline AND
           whose major limb/torso/clothing volume + overlap remain readable with tone removed
```

## B01-R1 reopen — observation method, not observation ceremony

Reopened and closed: **2026-08-31** from the second dogfood. The line-only re-draw hit no
value-authoring problems (B07-R1 held) but still needed 12 residuals, six of them the
same three method failures repeating on a single figure.

The common shape: every one passed a self-consistent correction loop. Comparing the
drawing to itself cannot catch a boundary found with a method that could not see it, a
line that separates nothing, or an ending that was assumed rather than observed.

Scope taken:

- `SubjectPalette` — the Agent samples materials it has already identified by eye and the
  palette reports which one a pixel is nearest, plus `ambiguous_pairs()` naming the
  materials this subject cannot separate. A luminance threshold cannot find bare skin
  inside dark clothing; on the dogfood subject `background vs skin = 29.6`;
- `observation/measuring-boundaries.md` — a line separates two named things; a luminance
  profile answers only a luminance question; do not draw a termination you did not
  observe; a correction is a new premise and inherits none of these;
- the three questions promoted into `SKILL.md` at the point of use, and applied again on
  every correction rather than only before the first mark;
- "the chain before its end" in `figure/limbs-joints.md`, the duplication test in
  `resolution/contour-and-overlap.md`, repeated-mark variation in
  `finish/identity-and-value.md`.

Full failure table: [`dogfood/vnext-b07r1/README.md`](../../dogfood/vnext-b07r1/README.md).

## B07-R1 reopen — value authoring and canonical session compaction

Reopened and closed: **2026-08-31** from post-B08 dogfood evidence. A completed croquis
produced a **313,391-line** canonical session against R23's **39,866** (7.86x) with no
quality gain.

The reopen was triggered on the hypothesis that correction/inspection/residual
bookkeeping had over-grown. Measurement rejected that hypothesis: that bookkeeping is
**1.3%** of the file, and per stored point the vNext record is **2.6x more compact**
than R23. The real causes were a missing value primitive, uncalibrated deposition,
duplicated `tool_state`, and persisted derived pressure. Full breakdown:
[`dogfood/vnext-b07r1/README.md`](../../dogfood/vnext-b07r1/README.md).

Scope taken:

- `fill_region()` — one authored action per tone region, deterministically expanded on
  replay, with reserved lights instead of after-the-fact erasing;
- a cached tone scale so deposition is calibrated **out of session**, never probed
  inside a drawing;
- canonical compaction: `tool_state` recorded once per action, derived pressure
  recomputed on load, explicitly authored pressure still stored verbatim;
- guidance that names the failure directly, since a surface that permits brute-forced
  tone will be brute-forced.

Explicitly out of scope: residual/correction bookkeeping compaction (1.3%, not the
bottleneck) and any raw-trace/canonical file split, which the measurement did not
justify.

### 2026-09-01 post-review hardening

The first B07-R1 implementation was kept, then hardened without broadening into B09:

- pre-compaction histories that persisted derived pressure and `tool_state` inline carry
  a transient compatibility marker during replay. Only that proven old representation
  omits the later `pressure_authored` provenance field when reproducing its saved visual
  digest; already-emitted B07-R1 checkpoint digests remain byte-for-byte stable;
- value regions now have an append-only `replace_fill_region()` path. A later inspection
  revises the region definition instead of stacking another fill or enumerating hundreds
  of generated hatch strokes; the returned action id binds directly to B06 correction
  provenance;
- canonical value guidance now requires **form before value**. With tone mentally removed,
  major limb thickness, torso/limb separation, clothing volume, prop contact, and overlap
  must already read. `ReservedLight` may preserve observed light inside a correct form;
  it may not manufacture missing structure.

The next dogfood therefore has two simultaneous acceptance axes: **record cost** and
**representation quality**. Passing the session-size target alone is insufficient.

## B08 activation record — orthogonal plain-data intent

Activated: **2026-08-31** after B07 closure and green repository gates. B08 is the sole
production WIP. Its contract is intentionally small: introduce `DrawingIntent` with
independent `reference_mode`, `drawing_mode`, `finish_intent`, and `style_profile`
values, plus immutable `ModeGuide`/`StyleGuide` authoring guidance and explicit
override resolution. These names are data selections, never lifecycle cursors.

Activation risks and controls:

- mode names could become hidden pipelines or phase transitions → guides expose only
  observations, grammar, omissions, finish emphasis, and questions; no stage/cursor/
  advance/close/verdict fields or methods;
- intent changes could fork or rewrite drawing history → `DrawingSession` remains the
  sole authority and records append-only intent provenance beside the existing history;
- style could be mistaken for a renderer/post-filter → built-ins describe authoring
  behavior and explicitly do not alter pixels or select a renderer;
- legacy aliases could leak lifecycle semantics → `full_body_croquis` is an explicit
  compatibility lookup returning an orthogonal intent, not a mode pipeline.

While B08 hardening was active, no B09+ work or broad preset catalog, renderer,
completion, or legacy-retirement surface was allowed. B08 is reclosed; B09 requires a
fresh activation record before production work begins.

## B08 narrow reopen — provenance and capability truth

Reopened: **2026-08-31** by reviewer feedback. Scope is limited to two contract gaps:

- resume must reject a current intent with an empty intent history, because every live
  selection path creates an append-only `IntentChangeRecord`;
- canonical skill/docs must state that imaginative/hybrid/free-draw values are intent
  scaffolding only while `DrawingSession.create()` still requires a readable subject.

No subjectless runtime, mode pipeline, renderer, schema redesign, or B09 work is in scope.

Reclosed: **2026-08-31** after the invariant regression and capability wording passed.
The production scope remains subject-backed; B09 is still inactive.

## B05 second reopen resolution — attention boundary

The B05 construction and near/right-arm correction closure remain valid. A review of the
first documentation migration found that the full R23 body was still embedded in the
same `SKILL.md` file under a collapsed `<details>` element. That is not an LLM attention
boundary, so B05 was reopened narrowly on 2026-08-31 and reclosed after the physical
separation and fresh-worker evidence gates passed.

Affected surface and risk:

- `skills/img2drawing/SKILL.md`: remove the embedded legacy body while preserving one
  short pointer to `references/legacy-r23.md`;
- `skills/img2drawing/references/INDEX.md`: stop enumerating legacy descendants in the
  canonical index and retain only the gateway;
- `dev/evidence/vnext/b05/canonical-route-fresh-worker.md`: record the actual fresh-route
  file set and explicit non-reads;
- risk addressed: compatibility remains discoverable through the gateway, and the
  fresh-worker result is recorded as a concrete trace artifact.

The accepted construction geometry, `DrawingSession`, inspection/checkpoint semantics,
stage-free references, and subject-only example remain frozen.

The post-reclosure CI follow-up also updated `dev/release/validate_r23_release.py` so the
R23 release gate verifies identity and preserved compatibility assets instead of requiring
Pn doctrine in canonical `SKILL.md`. The fix is covered by
`dev/tests/test_r23_release_validator.py`; no drawing or canonical route content changed.

The reopen record and evidence are in [`slices/B05.md`](slices/B05.md),
[`capsules/B05.md`](capsules/B05.md), and
[`../evidence/vnext/b05/canonical-route-fresh-worker.md`](../../evidence/vnext/b05/canonical-route-fresh-worker.md).
B05 is closed. B06 was explicitly activated as the sole production WIP and is now closed;
B07 was then activated and closed under the same WIP rule.

## B06 closure — residual-driven correction

Activated: 2026-08-31 after B05 reclosure and the R23 release-gate compatibility fix.
The slice is deliberately narrow: add Agent-authored residual/correction provenance on
the existing `DrawingSession` and inspection boundary, prove premise/global and local
repairs against the B05 subject, and preserve checkpoint/resume integrity. No stage
runtime, renderer, inspection implementation, mode registry, or automatic visual score
is in scope.

Activation risks:

- stale before/after inspection evidence could be accepted after a later mutation;
- correction actions could become detached from the observation that motivated them;
- residual memory could accidentally become a lifecycle gate or duplicate history.

The B06 contract addressed these with immutable inspection digests, explicit action and
observation references, `keep`/`revise` decisions, and atomic checkpoint writes. The
closure evidence is [`../evidence/vnext/b06/REVIEW.md`](../../evidence/vnext/b06/REVIEW.md),
the executable fixture is [`../dogfood/vnext-b06/README.md`](../../dogfood/vnext-b06/README.md),
and the public API is compressed in [`capsules/B06.md`](capsules/B06.md).

## Closed foundation

| Slice | State | Authoritative context |
|---|---|---|
| B00 | CLOSED | [`capsules/B00.md`](capsules/B00.md) |
| B01 | CLOSED | [`capsules/B01.md`](capsules/B01.md) |
| B02+B03 | CLOSED | [`capsules/B02-B03.md`](capsules/B02-B03.md) |
| B04 | CLOSED | [`capsules/B04.md`](capsules/B04.md) |
| B05 construction + canonical route de-anchoring | CLOSED | [`capsules/B05.md`](capsules/B05.md) |
| B06 residual-driven correction | CLOSED | [`capsules/B06.md`](capsules/B06.md) |
| B07 evidence / cost control | CLOSED | [`capsules/B07.md`](capsules/B07.md) |
| B08 orthogonal intent scaffolding | CLOSED | [`capsules/B08.md`](capsules/B08.md) |

## Current repository truth

- Frozen R23 baseline: `25ec4544e86fe37fc28d64575df145a1b711d63a`
- Current HEAD: this branch's latest closure commit (use `git log` for the exact SHA)
- vNext code: `inspection/`, `vnext/session.py`, `vnext/construction.py`, `vnext/evidence.py`,
  `vnext/value.py`, and B08 `vnext/intent.py`
- vNext tests: inspection, session, construction, correction, evidence, value, and intent
  suites under `dev/tests/`
- B05 dogfood: `dev/dogfood/vnext-b05/`
- B06 correction dogfood: `dev/dogfood/vnext-b06/`
- Representative visual evidence: `dev/evidence/vnext/b02-b03/`, `dev/evidence/vnext/b05/`,
  `dev/evidence/vnext/b06/`, and `dev/evidence/vnext/b07/`; B08 trace is under
  `dev/evidence/vnext/b08/` (fixture source: `dev/dogfood/vnext-b08/`)
- Legacy stage runtime remains in `run.py`, `stages/`, `review/`, playbooks, and
  `references/stages/`; it is compatibility/reference material, not the vNext path.

## WIP guard

With B08 closed and before B09 activation:

- do not implement B09 or later slices until a fresh B09 activation record exists;
- do not reopen B05 unless new construction-quality evidence requires it;
- do not add mode/style registries, tonal/free-draw pipelines, completion contracts, or
  renderer families;
- do not physically remove R23 runtime or persistence;
- do not rewrite the accepted B05 drawing geometry unless new visual evidence triggers a
  separate construction-quality reopen.

## B07 closure — evidence and cost control

Activated and closed: **2026-08-31**. The existing `InspectionSheet` now carries an
Agent-authored quick/focused/deep presentation/read policy: quick rejects extras, focused
accepts only 1–3 prioritized ROIs, and deep allows up to three ROIs plus guide/grid/
measurement evidence with a reason. `DrawingSession` persists immutable telemetry for
inspection calls, review turns, generated/visual artifacts, elapsed work, and explicit
artifact reads; stale snapshots are visible and unreadable evidence fails explicitly.

The B05 representative correction used two review turns and four image reads, compared
with the preserved R23 fixture's five review ceremonies and twelve image files. The
vNext 8 visual/12 total generated-file inventory and R23's 60 total stage-review files
are recorded separately because those totals are not equivalent units. Direct sheets,
tests, and the capsule are committed under the B07 evidence paths.

## B07 narrow reopen — evidence hardening

Reopened: **2026-08-31** by reviewer feedback. The original B07 evidence implementation
was sound, but two contract gaps remained: mode names did not enforce their documented
presentation/read budgets, and checkpoint resume accepted orphan or cross-bound evidence
read records. Scope was limited to `EvidencePolicy.from_inputs()`, construction-helper
mode selection, resume validation, misuse/orphan regression tests, and the matching
documentation/capsule wording. No drawing geometry, renderer, inspection implementation,
or B08 surface was reopened. R1/R2 passed and B07 was reclosed on 2026-08-31.

## B08 closure

B08 closed on **2026-08-31** after plain-data models, session provenance, dogfood trace,
documentation, duplicate/orphan audit, capability-truth wording, and full repository
gates passed. The capsule is [`capsules/B08.md`](capsules/B08.md); B09 is the next slice
and is not active.
