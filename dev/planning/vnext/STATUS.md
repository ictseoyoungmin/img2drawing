# img2drawing current status

Updated: 2026-09-13

```text
RELEASED STABLE:   v1.0.2 · DrawingSession/1.0.2-vnext · A10
RC CANDIDATE:      v1.0.3rc1 · DrawingSession/1.0.3-vnext · A11
RC BRANCH:         release/1.0.3-rc
RC RENDERER:       new sessions → pillow-pencil-contact-v10/1
HISTORICAL REPLAY: explicit v9/1 sessions remain v9/1
PROMOTION EVIDENCE: PASS · width×3 same-environment v9/v10 benchmark + canonical/fast exactness
PUBLISH STATE:     no v1.0.3rc1 publish manifest; v1.0.2 remains latest published stable
NEXT INTEGRATION:  final RC CI/wheel verification → PR to main
```

## Current truth

- `v1.0.2` remains the latest published immutable stable release. Its tag, publish manifest, release notes, and `CONTRACT_FREEZE.json` are historical authority and are not rewritten for this RC.
- The current release candidate package identity is `1.0.3rc1 / A11 / v1.0.3rc1_renderer_v10_markmaking_rc` with public contract identity `DrawingSession/1.0.3-vnext`.
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

## Remaining work after RC declaration

1. **RC integration** — require final source tests, current-package B17 clean wheel/install audit, historical B18 verification, promotion-evidence verification, and a wheel whose metadata is exactly `1.0.3rc1`; then merge through a PR to `main`.
2. **Fresh-worker gesture dogfood** — behaviorally verify explicit pure gesture and unqualified constructive gesture, including the new anti-circle-head / anti-faceted-mass guidance. This is artistic-behavior evidence, not a blocker for renderer package identity.
3. **Stable promotion decision** — only after RC integration and desired dogfood, decide whether to publish stable v1.0.3. Stable publishing requires a separate explicit publish manifest; do not create one implicitly from the RC version bump.
4. **Root compatibility shims** — deprecated pre-0.6.0rc2 root aliases remain intentionally supported in rc1 and are a separately versioned compatibility decision.

## Historical B18 boundary

At the B18 implementation freeze, the product foundation was **frozen through B18** and the formal **D01–D06 not started** campaign was still future work. Those phrases are retained only so frozen B18 evidence remains understandable and verifiable. They do not describe current sequencing.

## Historical boundaries

The following remain history/evidence, not current package-version authority:

- `docs/releases/v1.0.0.md`, `v1.0.1.md`, `v1.0.2.md`;
- closed A/B slice, capsule, baseline, and audit documents under this planning tree;
- benchmark reports tied to earlier versions;
- `dev/release/vnext/CONTRACT_FREEZE.json`, the immutable v1.0.2/A10 release snapshot.

## Authority map

- current RC state: actual `release/1.0.3-rc` + this file;
- RC promotion evidence: `dev/release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- deployable drawing behavior: `skills/img2drawing/SKILL.md` + references;
- latest published stable notes: `docs/releases/v1.0.2.md`;
- RC candidate notes: `docs/releases/v1.0.3rc1.md`;
- public change history: `CHANGELOG.md`;
- current near-term sequence: `ROADMAP.md`;
- immutable v1.0.2 contract snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`.
