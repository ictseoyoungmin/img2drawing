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
G01 RC1 DOGFOOD:    REOPEN · gesture runtime-mode gap + generic rounded-mass failure
PUBLISH STATE:      no v1.0.3rc2 publish manifest; v1.0.2 remains latest published stable
NEXT VALIDATION:    rerun pure + unqualified constructive gesture on rc2
```

## Current truth

- `v1.0.2` remains the latest published immutable stable release. Its tag, publish manifest, release notes, and `CONTRACT_FREEZE.json` are historical authority and are not rewritten for this RC line.
- PR #40 integrated `1.0.3rc1 / A11` into `main` at `dc36a86b45aaeed453505330a8bb423fc78405a2`; post-merge main CI run `34705776246` passed.
- G01 fresh-worker dogfood then found two reusable defects in rc1: `DrawingIntent(drawing_mode="gesture")` was rejected even though gesture is a user-facing skill mode, and anti-faceted mass guidance could still collapse torso/pelvis construction into smooth generic bean/oval/capsule shapes.
- The corrective candidate is `1.0.3rc2 / A12 / v1.0.3rc2_gesture_runtime_alignment` on `fix/g01-gesture-runtime-rc2`, with the same public contract identity `DrawingSession/1.0.3-vnext`.
- rc2 adds `gesture` to the public drawing-intent vocabulary and a gesture `ModeGuide`; it does not introduce a workflow stage.
- rc2 strengthens gesture specificity so `rounded` is not treated as a quality target by itself: head profile/jaw/nape, shoulder/back/side asymmetry, hip shelf, taper, near/far exposure, and leg-attachment relations must survive when observed.
- Renderer v10 and fast-timelapse implementation measured for rc1 promotion are byte-unchanged by this rc2 slice. The rc1 width×3 performance/parity evidence therefore remains the renderer/timelapse authority rather than being re-measured for an unrelated intent/docs correction.
- New sessions continue to select `pillow-pencil-contact-v10 / 1`; explicit historical v9 sessions preserve v9 replay semantics across checkpoint/resume.
- The installable R23 compatibility namespace and remaining R23 orchestration/runtime cluster remain physically retired from current `src`.
- New work uses one stage-free `DrawingSession` orchestration route.
- The deployable drawing authority is `skills/img2drawing/SKILL.md` plus `skills/img2drawing/references/`.
- Mechanical CI verifies repository/runtime/package/provenance contracts. It does not issue an artistic-quality verdict; G01 still requires visual dogfood evidence before stable promotion.

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

## G01 reopen evidence

The first rc1 fresh-worker pass used the same reference for two requested finish levels:

1. explicit pure/quick gesture;
2. unqualified `gesture drawing`, which should route to constructive gesture.

The run exposed two distinct failures:

- **runtime alignment:** the public `DrawingIntent` enum did not contain `gesture`, so a worker had to fall back to another drawing mode despite the skill defining gesture as user-facing;
- **visual specificity:** removing hard polygons was not enough. A constructive pelvis could become a smooth capsule/blob, and a nearly circular head could still satisfy the old wording too easily even when profile/jaw information was visible.

G01 therefore remains **REOPEN** until rc2 is rerun against the same two cases and the final visible marks pass the whole-pose, head-direction, subject-specific mass, limb/support, and anti-primitive checks.

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

1. **RC2 mechanical verification** — current docs/runtime/instruction graph/full suite/B17/B18 must pass with package metadata exactly `1.0.3rc2`; rc1 renderer promotion evidence must remain valid because its measured implementation paths are unchanged.
2. **G01 rc2 fresh-worker dogfood** — rerun explicit pure gesture and unqualified constructive gesture on the same reference. Reject circle-head, polygon masses, smooth stock blobs/capsules, missing major limb/support relations, or scaffold-only early finish.
3. **Stable promotion decision** — only after G01 passes decide whether rc2 is promoted to stable v1.0.3. Stable publishing requires a separate explicit freeze/publish manifest.
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
- rc1 integrated history: `main`, PR #40, and `docs/releases/v1.0.3rc1.md`;
- rc1 renderer promotion evidence: `dev/release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- deployable drawing behavior: `skills/img2drawing/SKILL.md` + references;
- latest published stable notes: `docs/releases/v1.0.2.md`;
- rc2 candidate notes: `docs/releases/v1.0.3rc2.md`;
- public change history: `CHANGELOG.md`;
- current near-term sequence: `ROADMAP.md`;
- immutable v1.0.2 contract snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`.
