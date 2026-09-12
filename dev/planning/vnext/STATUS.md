# img2drawing current status

Updated: 2026-09-13

```text
RELEASED STABLE:    v1.0.2 · DrawingSession/1.0.2-vnext · A10
RC1 IN MAIN:        v1.0.3rc1 · DrawingSession/1.0.3-vnext · A11
RC CANDIDATE:       v1.0.3rc2 · DrawingSession/1.0.3-vnext · A12
RC2 BRANCH:         fix/g01-gesture-runtime-rc2
RC RENDERER:        unchanged from rc1 · new sessions → pillow-pencil-contact-v10/1
HISTORICAL REPLAY:  explicit v9/1 sessions remain v9/1
RC1 PERF EVIDENCE:  PASS · renderer/timelapse paths unchanged by rc2
G01 GESTURE:        PASS/CLOSED · runtime alignment + anti-primitive/anti-blob dogfood
RC2 CI:             PASS · full current/historical/package verification on branch
PUBLISH STATE:      no v1.0.3rc2 publish manifest; v1.0.2 remains latest published stable
NEXT BOTTLENECK:    broad-pencil graphite feel + blunt/square terminal quality
```

## Current truth

- `v1.0.2` remains the latest published immutable stable release. Its tag, publish manifest, release notes, and `CONTRACT_FREEZE.json` are historical authority and are not rewritten for this RC line.
- PR #40 integrated `1.0.3rc1 / A11` into `main` at `dc36a86b45aaeed453505330a8bb423fc78405a2`; post-merge main CI passed.
- G01 rc1 fresh dogfood found two reusable defects: `DrawingIntent(drawing_mode="gesture")` was rejected despite gesture being a user-facing skill mode, and anti-faceted guidance could still collapse torso/pelvis construction into generic smooth bean/oval/capsule shapes.
- The corrective candidate is `1.0.3rc2 / A12 / v1.0.3rc2_gesture_runtime_alignment` on `fix/g01-gesture-runtime-rc2`, with the same public contract identity `DrawingSession/1.0.3-vnext`.
- rc2 adds `gesture` to the public drawing-intent vocabulary and a gesture `ModeGuide`; it does not introduce a workflow stage.
- rc2 gesture guidance rejects informationally empty geometric **and rounded** primitives while explicitly preserving roundness that is actually supported by the reference. Head facing/profile, torso asymmetry, hip shelf/near-far relation, and leg-attachment information remain the deciding evidence.
- G01 also exposed a markmaking discoverability gap: semantic preset IDs such as `gesture-flow` are resolved through `resolve_mark_for_intent()` / `ResolvedMark.draw_kwargs()` rather than being guessed as literal `DrawingSession.draw(tool=...)` names. The public docs and regression tests now lock that adapter boundary.
- The same-reference pure + constructive fresh-session dogfood reached the requested G01 target without scaffold-only finish, orientationless circle-head, faceted torso/pelvis icons, or attachment-free rounded blobs. Evidence is recorded in `dev/dogfood/g01-gesture-rc2/README.md`.
- Renderer v10 and fast-timelapse implementation measured for rc1 promotion are byte-unchanged by rc2. The rc1 width×3 performance/parity evidence therefore remains the renderer/timelapse authority rather than being re-measured for an unrelated intent/docs correction.
- New sessions continue to select `pillow-pencil-contact-v10 / 1`; explicit historical v9 sessions preserve v9 replay semantics across checkpoint/resume.
- The installable R23 compatibility namespace and remaining R23 orchestration/runtime cluster remain physically retired from current `src`.
- New work uses one stage-free `DrawingSession` orchestration route.
- The deployable drawing authority is `skills/img2drawing/SKILL.md` plus `skills/img2drawing/references/`.
- Mechanical CI verifies repository/runtime/package/provenance contracts. It does not issue an artistic-quality verdict.

## RC1 renderer promotion evidence retained

The exact rc1 GitHub Actions candidate wheel was measured against the 1,272-action `window-study` with authored stroke widths scaled ×3. Those measurements remain authoritative because rc2 does not change the measured renderer/timelapse paths.

- v9 cold median: **27.389 s**
- v10 cold median: **28.727 s** (**+4.886%**)
- v9 warm median: **10.062 s**
- v10 warm median: **10.199 s** (**+1.365%**)
- v9 cold patch-build median: **16.247 s**
- v10 cold patch-build median: **18.206 s** (**+12.058%**)
- v9 fast = v9 canonical RGB: **pixel-exact**
- v10 fast = v10 canonical RGB: **pixel-exact**

Authority: `dev/release/vnext/V1_0_3_RC1_PROMOTION.md` and `.json`. CI continues to reject changes to the measured renderer/timelapse implementation without renewed evidence.

## G01 closure evidence

The same reference was used for two user-facing finish levels:

1. explicit pure/quick gesture;
2. unqualified `gesture drawing`, which routes to constructive gesture.

The correction loop deliberately rejected intermediate results that still read as a circle-head,
faceted/closed construction icon, generic rounded mannequin mass, or coarse polyline. The final
review distinguished **reference-supported roundness** from a stock primitive: a rounded silhouette
is valid when facing, asymmetry, overlap, taper, and attachment evidence remain present.

G01 is therefore **PASS / CLOSED for its target failure class**. This does not claim production
croquis quality or cross-agent/cross-subject generalization. See
`dev/dogfood/g01-gesture-rc2/README.md` for the reviewed artifact hashes and bounded verdict.

## Next bottleneck: broad-pencil material quality

Stable v1.0.3 promotion is still blocked by a separate observed renderer/material defect. Thick
pencil marks can read as a uniform digital ribbon rather than graphite: paper/tooth interaction is
too weak at broad widths and stroke terminals can appear blunt or square. This problem was largely
hidden by earlier thin-line work and should be closed at the renderer/markmaking owner before stable
promotion.

The next slice should therefore validate and repair broad-pencil terminals, pressure/alpha release,
graphite density variation, and tooth interaction without regressing thin-line parity or historical
v9 replay.

## Current source surface

The installable top-level implementation remains intentionally narrow:

```text
img2drawing/
├── core/
├── data/
├── inspection/
├── observation/      # palette only
├── provenance/
├── render/
├── vnext/
├── runtime.py
├── __init__.py
└── _version.py
```

Retired from current `src`: `legacy/`, `run.py`, `stages/`, `exemplar/`, `review/`, historical `registration/`, `canvas/`, historical `reference/`, and non-palette R23 observation modules.

## Remaining work

1. **Broad-pencil renderer/material hardening** — reproduce the thick-line weak-graphite and square-terminal failure with a focused deterministic fixture; repair the smallest responsible v10 material/terminal owner while preserving thin-path behavior and historical v9 semantics.
2. **RC2 integration decision** — after the new gesture adapter/docs tests remain green, merge rc2 to `main` as the current candidate without creating a publish manifest.
3. **Stable promotion decision** — only after broad-pencil quality passes decide whether the resulting candidate is ready for stable v1.0.3 or requires another RC. Stable publishing requires a separate explicit freeze/publish manifest.
4. **Root compatibility shims** — deprecated pre-0.6.0rc2 root aliases remain intentionally supported in the 1.0.3 RC line and are a separately versioned compatibility decision.

## Historical B18 boundary

At the B18 implementation freeze, the product foundation was **frozen through B18** and the formal **D01–D06 not started** campaign was still future work. Those phrases are retained only so frozen B18 evidence remains understandable and verifiable. They do not describe current sequencing.

## Historical boundaries

The following remain history/evidence, not current package-version authority:

- `docs/releases/v1.0.0.md`, `v1.0.1.md`, `v1.0.2.md`;
- `docs/releases/v1.0.3rc1.md` and PR #40 as the rc1 integration record;
- closed A/B slice, capsule, baseline, and audit documents under this planning tree;
- benchmark reports tied to earlier versions;
- `dev/release/vnext/CONTRACT_FREEZE.json`, the immutable v1.0.2/A10 release snapshot.

## Authority map

- current rc2 candidate state: `fix/g01-gesture-runtime-rc2` + this file;
- G01 behavioral evidence: `dev/dogfood/g01-gesture-rc2/README.md`;
- rc1 integrated history: `main`, PR #40, and `docs/releases/v1.0.3rc1.md`;
- rc1 renderer promotion evidence: `dev/release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- deployable drawing behavior: `skills/img2drawing/SKILL.md` + references;
- latest published stable notes: `docs/releases/v1.0.2.md`;
- rc2 candidate notes: `docs/releases/v1.0.3rc2.md`;
- public change history: `CHANGELOG.md`;
- current near-term sequence: `ROADMAP.md`;
- immutable v1.0.2 contract snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`.
