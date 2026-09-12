# img2drawing v1.0.3rc1 promotion evidence

Status: **PASS FOR VERSION DECLARATION**

This record closes the performance/parity evidence required before changing the package identity from the published `1.0.2` line to `1.0.3rc1`.

## Authority

- candidate branch: `release/1.0.3-rc`
- measured commit: `0b6432f1774015dc35cb62a2fc94ca58d8ebb6ef`
- measured tree: `c8a40c5f2b10a74cfbfd5fd076c0f32a8e665221`
- GitHub Actions run: `34703239190`
- verified candidate artifact ZIP SHA-256: `bf1284698e5ffd712c584bb290b01487d5db86be94bfeabd98881946499a7eba`
- wheel SHA-256: `d6738164cef64f883fd0c64f648f165e5114cb4416281f338bd57650d87df6c1`
- window-study source ZIP SHA-256: `f17a5cd3ebb4ac5a6929d505a6ba7ce75129e86cd509d87553fc4566b750d96b`

The wheel still identifies itself as `1.0.2`; that is intentional. This evidence is the gate **before** the `1.0.3rc1` version declaration.

## Fixture

The original 1,272-action `window-study` history was stress-scaled by multiplying authored draw-stroke width and the mirrored resolved tool-state width by exactly `3.0`. Coordinates, pressure, opacity, taper, layers, action order, and deletes were preserved.

- actions: **1,272**
- sampled frames: **637** (`every_n=2`)
- canvas: **1536×864**
- historical width×3 characterization: median ≈ **3.15 px**, max **8.4 px**, **255** authored draw strokes above 4.5 px

Each trial used a fresh persistent patch cache for cold measurement, followed by a separate-process warm measurement against that completed cache. Cache storage was `/dev/shm` to avoid mounted-filesystem latency dominating patch-cache reads.

## Same-environment 3-trial result

Absolute wall times are intentionally not compared with older execution slots. The current container is materially slower than the earlier research slot, so promotion is based on **same-wheel, same-fixture, same-environment relative v9/v10 measurements**.

| width×3 render+pack | trial 1 | trial 2 | trial 3 | median |
|---|---:|---:|---:|---:|
| v9 cold | 26.861 s | 27.389 s | 27.937 s | **27.389 s** |
| v10 cold | 28.727 s | 28.234 s | 29.659 s | **28.727 s** |
| v9 warm | 10.062 s | 10.076 s | 9.989 s | **10.062 s** |
| v10 warm | 10.147 s | 10.199 s | 10.243 s | **10.199 s** |

Cold patch-build medians:

- v9: **16.247 s**
- v10: **18.206 s**

Same-environment v10 deltas relative to v9:

- cold render+pack: **+4.886%**
- warm render+pack: **+1.365%**
- cold patch build: **+12.058%**

Interpretation: the broad-material work still has a first-build cost, but the measured total cold delta is substantially below the earlier +15.06% width×3 research observation from its own environment. Warm operation remains in the same practical range.

## Pixel authority

Final-frame RGB hashes were checked independently with the fast path and the canonical renderer.

### v9 historical backend

```text
fast      3cbbce01c35cdad0acfb852e5f06bfe67d05a0e7f7e4b8e2eacb7c6d2b0e9aca
canonical 3cbbce01c35cdad0acfb852e5f06bfe67d05a0e7f7e4b8e2eacb7c6d2b0e9aca
```

**pixel-exact: PASS**

### v10 candidate backend

```text
fast      72aa16996a6ce5ec8db672782e7ab1487f5593aae77afbe2769b4396c4842205
canonical 72aa16996a6ce5ec8db672782e7ab1487f5593aae77afbe2769b4396c4842205
```

**pixel-exact: PASS**

The v9 and v10 hashes are not expected to match each other: v10 intentionally removes compatibility `stage` from hand-dynamics seed identity while v9 remains historical replay authority. The contract is v9-fast = v9-canonical and v10-fast = v10-canonical.

## Promotion verdict

The remaining pre-version gate is closed:

- current main history absorbed into the RC branch with no tree changes;
- v9 historical rendering preserved;
- v10 canonical/fast exactness preserved under broad width stress;
- broad cold cost measured against v9 in the same environment;
- warm cache path remains operationally equivalent;
- candidate wheel was produced by the branch CI, not a local source checkout.

**Verdict: PASS_FOR_1.0.3rc1_VERSION_DECLARATION.**

Machine-readable values are in `V1_0_3_RC1_PROMOTION.json`.
