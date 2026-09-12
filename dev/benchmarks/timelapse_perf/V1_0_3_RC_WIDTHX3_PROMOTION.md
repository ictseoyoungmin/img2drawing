# v1.0.3 RC width×3 promotion evidence

This record closes the broad-stroke performance gate for the `release/1.0.3-rc` candidate after syncing current `main` history.

## Candidate authority

- RC head measured: `0b6432f1774015dc35cb62a2fc94ca58d8ebb6ef`
- GitHub Actions RC wheel artifact digest: `sha256:bf1284698e5ffd712c584bb290b01487d5db86be94bfeabd98881946499a7eba`
- source workload: 1,272-action `window-study`
- sampling: `every_n=2` → 637 sampled frames
- authored width transformation: width only ×3; coordinates, pressure, opacity, taper, layer/order, and edit/delete history unchanged
- transformed widths: median `3.15 px`, max `8.40 px`, 255 authored strokes above `4.5 px`
- transformed action-log SHA-256: `76a3cbcd3126f7e7b65d4c07252ae99677ecaeb6f794724c476caee18fb97a37`
- transformed drawing-state SHA-256: `da12f05fd39f6d2428b633c89305e23b0d6ad81e7d2211e798d987280afb24e0`

## Measurement method

The promotion comparison remeasures both v9 and v10 in the same current execution environment rather than mixing historical wall times from another machine/session.

Each trial uses the same `FastFrameSource` traversal and transformed history. Cold starts with an empty in-memory stroke-patch cache. Warm resets replay state and native/high-resolution canvases while preserving only the renderer's in-memory content-addressed patch cache; object-cache state is cleared before warm. GIF encoding, persistent-disk cache I/O, and standalone canonical-final rendering are outside these timings.

These values are renderer/frame-source comparison evidence, not an API latency guarantee. Historical width×3 evidence is an independent cross-check and is not mixed statistically into this median.

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

The hashes are intentionally different between renderer generations because v10 changes broad-pencil material/terminal behavior. The correctness claim here is deterministic repeatability and exact cold/warm fast-path output within each renderer; canonical↔fast v10 exactness is covered by the existing RC regression/evidence gates.

## Historical cross-check

The earlier same-workload width×3 study measured v9/v10 at `10.768/12.390 s` cold and `2.723/2.689 s` warm, or `+15.06%` cold and `-1.27%` warm. The present environment is slower in absolute cold wall time, so those old wall times are not combined statistically with this run. Both measurements agree on the material conclusion: v10 pays a bounded first-build cost on broad graphite while warm replay remains close to v9.

## Promotion decision

**PASS.** On a deliberately broad 3× stress history, v10's three-trial median cold overhead is `+12.57%` and warm overhead is `+3.30%`, with deterministic final pixels and complete cache transition (`1227` cold builds → `1227` warm hits) on every trial. This closes the broad-stroke performance evidence gate. The next gate is package-version declaration and final RC CI/wheel verification.
