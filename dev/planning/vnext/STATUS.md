# img2drawing current status

Updated: 2026-09-13

```text
RELEASED STABLE:    v1.0.2 · DrawingSession/1.0.2-vnext · A10
RC IN MAIN:         v1.0.3rc1 · DrawingSession/1.0.3-vnext · A11
RC SOURCE BRANCH:   release/1.0.3-rc
RC RENDERER:        new sessions → pillow-pencil-contact-v10/1
HISTORICAL REPLAY:  explicit v9/1 sessions remain v9/1
PROMOTION EVIDENCE: PASS · width×3 same-environment v9/v10 benchmark + canonical/fast exactness
MAIN INTEGRATION:   PASS · PR #40 merged as dc36a86b45aaeed453505330a8bb423fc78405a2
MAIN CI:            PASS · run 34705776246
PUBLISH STATE:      no v1.0.3rc1 publish manifest; v1.0.2 remains latest published stable
NEXT VALIDATION:    G01 fresh-worker gesture dogfood
```

## Current truth

- `v1.0.2` remains the latest published immutable stable release. Its tag, publish manifest, release notes, and `CONTRACT_FREEZE.json` are historical authority and are not rewritten for this RC.
- The release-candidate package identity now integrated into `main` is `1.0.3rc1 / A11 / v1.0.3rc1_renderer_v10_markmaking_rc` with public contract identity `DrawingSession/1.0.3-vnext`.
- PR #40 merged the validated RC into `main` at `dc36a86b45aaeed453505330a8bb423fc78405a2`; the subsequent main push CI run `34705776246` passed all applicable verification gates.
- New sessions select `pillow-pencil-contact-v10 / 1`; explicit historical v9 sessions preserve v9 replay semantics across checkpoint/resume.
- v10 removes compatibility `Stroke.stage` from hand-dynamics seed identity, closing inspect/current-state ↔ final/replay parity without changing frozen v9 behavior.
- Broad v10 graphite preserves authored pressure/opacity darkness in a core while material tooth/dry breakup remains in the shoulder; ordinary thin strokes retain the optimized thin path.
- The fast timelapse renderer follows the session renderer contract, including v9/v10 identity, and reconstructs late low-layer strokes through layer-order-aware dirty recomposition.
- Markmaking style/tool vocabulary is part of the instruction graph and runtime discovery surface; cache/provenance identity includes the renderer/style/tool state required for exact replay.
- The installable R23 compatibility namespace and remaining R23 orchestration/runtime cluster are physically retired from current `src`.
- New work uses one stage-free `DrawingSession` orchestration route.
- The deployable drawing authority is `skills/img2drawing/SKILL.md` plus `skills/img2drawing/references/`.
- Mechanical CI verifies repository/runtime/package/provenance contracts. It does not issue an artistic-quality verdict.

## RC promotion evidence

The exact GitHub Actions candidate wheel was measured against the 1,272-action `window-study` with authored stroke widths scaled ×3. Same-environment three-trial medians are authoritative for the relative comparison because absolute wall time varies across execution slots.

- v9 cold median: **27.389 s**
- v10 cold median: **28.727 s** (**+4.886%**)
- v9 warm median: **10.062 s**
- v10 warm median: **10.199 s** (**+1.365%**)
- v9 cold patch-build median: **16.247 s**
- v10 cold patch-build median: **18.206 s** (**+12.058%**)
- v9 fast = v9 canonical RGB: **pixel-exact**
- v10 fast = v10 canonical RGB: **pixel-exact**

Authority: `dev/release/vnext/V1_0_3_RC1_PROMOTION.md` and `.json`. CI runs `dev/tools/verify_v103_rc_promotion.py` and rejects changes to the measured renderer/timelapse runtime without renewed evidence.

## RC integration closure

The RC integration gate is **CLOSED**.

- final RC branch CI: PASS;
- exact `1.0.3rc1` wheel metadata: verified;
- pull-request CI for PR #40: PASS;
- merge commit: `dc36a86b45aaeed453505330a8bb423fc78405a2`;
- post-merge `main` CI run `34705776246`: PASS;
- no RC publish manifest was created, so integration did not alter the published-stable boundary.

The main-branch workflow intentionally skips the RC-only wheel-upload steps after merge; the exact candidate wheel was already built and verified on the release branch before PR #40.

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

## Remaining work after RC integration

1. **Fresh-worker gesture dogfood** — behaviorally verify explicit pure gesture and unqualified constructive gesture, including the anti-circle-head / anti-faceted-mass guidance. This is artistic-behavior evidence, not a blocker for the already integrated RC package identity.
2. **Stable promotion decision** — after the desired dogfood, decide whether `1.0.3rc1` is promoted to stable v1.0.3 or another RC is required. Stable publishing requires a separate explicit freeze/publish manifest; do not infer publication from the RC being present on `main`.
3. **Root compatibility shims** — deprecated pre-0.6.0rc2 root aliases remain intentionally supported in rc1 and are a separately versioned compatibility decision.

## Historical B18 boundary

At the B18 implementation freeze, the product foundation was **frozen through B18** and the formal **D01–D06 not started** campaign was still future work. Those phrases are retained only so frozen B18 evidence remains understandable and verifiable. They do not describe current sequencing.

## Historical boundaries

The following remain history/evidence, not current package-version authority:

- `docs/releases/v1.0.0.md`, `v1.0.1.md`, `v1.0.2.md`;
- closed A/B slice, capsule, baseline, and audit documents under this planning tree;
- benchmark reports tied to earlier versions;
- `dev/release/vnext/CONTRACT_FREEZE.json`, the immutable v1.0.2/A10 release snapshot.

## Authority map

- current integrated RC state: actual `main` + this file;
- RC source history: `release/1.0.3-rc` and PR #40;
- RC promotion evidence: `dev/release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- deployable drawing behavior: `skills/img2drawing/SKILL.md` + references;
- latest published stable notes: `docs/releases/v1.0.2.md`;
- RC candidate notes: `docs/releases/v1.0.3rc1.md`;
- public change history: `CHANGELOG.md`;
- current near-term sequence: `ROADMAP.md`;
- immutable v1.0.2 contract snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`.
