# v1.0.3 RC width×3 secondary cross-check

This record is an **independent secondary remeasurement** of the broad-stroke renderer comparison for `release/1.0.3-rc`. It does not replace the authoritative promotion record in `dev/release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`, which includes render+pack timings and canonical↔fast exactness.

## Candidate measured

- RC head measured: `0b6432f1774015dc35cb62a2fc94ca58d8ebb6ef`
- GitHub Actions RC wheel artifact digest: `sha256:bf1284698e5ffd712c584bb290b01487d5db86be94bfeabd98881946499a7eba`
- source workload: 1,272-action `window-study`
- sampling: `every_n=2` → 637 sampled frames
- authored width transformation: width only ×3; coordinates, pressure, opacity, taper, layer/order, and edit/delete history unchanged
- transformed widths: median `3.15 px`, max `8.40 px`, 255 authored strokes above `4.5 px`
- transformed action-log SHA-256: `76a3cbcd3126f7e7b65d4c07252ae99677ecaeb6f794724c476caee18fb97a37`
- transformed drawing-state SHA-256: `da12f05fd39f6d2428b633c89305e23b0d6ad81e7d2211e798d987280afb24e0`

## Measurement method

This secondary comparison remeasures both v9 and v10 in the same execution environment rather than mixing historical wall times from another machine/session.

Each trial uses the same `FastFrameSource` traversal and transformed history. Cold starts with an empty in-memory stroke-patch cache. Warm resets replay state and native/high-resolution canvases while preserving only the renderer's in-memory content-addressed patch cache; object-cache state is cleared before warm. GIF encoding, persistent-disk cache I/O, delta-pack writing, and standalone canonical-final rendering are outside these timings.

Because this method is narrower than the release promotion benchmark, the values are supporting renderer/frame-source evidence rather than package latency or release-gate authority.

## Three-trial results

| renderer | trial | cold (s) | warm (s) | cold misses | warm hits | cold→warm final exact |
|---|---:|---:|---:|---:|---:|---|
| v9 | 1 | 20.0133 | 3.1336 | 1227 | 1227 | yes |
| v9 | 2 | 19.4797 | 2.8705 | 1227 | 1227 | yes |
| v9 | 3 | 19.2058 | 2.7372 | 1227 | 1227 | yes |
| v10 | 1 | 21.6849 | 2.9653 | 1227 | 1227 | yes |
| v10 | 2 | 22.0802 | 2.9338 | 1227 | 1227 | yes |
| v10 | 3 | 21.9274 | 2.9976 | 1227 | 1227 | yes |

Median comparison:

| metric | v9 median | v10 median | v10 delta |
|---|---:|---:|---:|
| cold frame-source sweep | 19.4797 s | 21.9274 s | **+12.57%** |
| warm frame-source sweep | 2.8705 s | 2.9653 s | **+3.30%** |

Deterministic final RGB SHA-256 across all three trials:

- v9: `3cbbce01c35cdad0acfb852e5f06bfe67d05a0e7f7e4b8e2eacb7c6d2b0e9aca`
- v10: `72aa16996a6ce5ec8db672782e7ab1487f5593aae77afbe2769b4396c4842205`

The hashes are intentionally different between renderer generations because v10 changes broad-pencil material/terminal behavior. This secondary check establishes deterministic repeatability and exact cold/warm fast-path output within each renderer. Canonical↔fast exactness is owned by the authoritative RC promotion record and CI verifier.

## Cross-check against authoritative promotion evidence

The authoritative release record measures full fast render+pack and reports v10 vs v9 medians of `+4.886%` cold, `+1.365%` warm, and `+12.058%` cold patch-build, with v9 and v10 each pixel-exact against their canonical renderer.

This narrower direct sweep reports `+12.57%` cold and `+3.30%` warm. The methods therefore should not be numerically pooled, but both support the same conclusion: v10 adds bounded broad-material first-build work while the cached replay path remains close to v9.

## Secondary verdict

**SUPPORTING PASS.** The direct frame-source remeasurement independently supports the existing `PASS_FOR_1.0.3rc1_VERSION_DECLARATION` decision. Release authority remains `dev/release/vnext/V1_0_3_RC1_PROMOTION.{md,json}` and `dev/tools/verify_v103_rc_promotion.py`.
