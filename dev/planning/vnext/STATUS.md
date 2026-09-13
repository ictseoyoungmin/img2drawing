# img2drawing current status

Updated: 2026-09-13

```text
PUBLISHED STABLE:   v1.0.3 · DrawingSession/1.0.3-vnext · A14
RELEASE TAG:        v1.0.3 → d6151ba8dfef8dc37ef5cddd24c2c6c974d53976
CURRENT RENDERER:   new sessions → pillow-pencil-contact-v11/1
HISTORICAL REPLAY:  explicit v9/1 and v10/1 sessions remain supported
G01 GESTURE:        PASS/CLOSED
G02 BROAD PENCIL:   PASS/CLOSED
STABLE SOURCE:      release/1.0.3-stable @ 0de885e6d3f2ed6ac857c46e60875cc8c5c9f727
STABLE WHEEL GATE:  CI 34749311565 · package tree 5758c5efa60d80a0d483bcb3573258e34d609055
MAIN RELEASE CI:    34749869989 · PASS
PUBLISH WORKFLOW:   34749920471 · PASS
PUBLISH STATE:      GitHub Release v1.0.3 published
NEXT GATE:          none for v1.0.3 · release CLOSED
```

## Current truth

- `v1.0.3` is the latest **published stable** release.
- The Git tag `v1.0.3` and GitHub Release both target main commit `d6151ba8dfef8dc37ef5cddd24c2c6c974d53976`.
- PR #42 closed gesture/runtime corrective work; G01 is **PASS / CLOSED** with evidence in `dev/dogfood/g01-gesture-rc2/README.md`.
- PR #43 integrated renderer v11 and closed the reported broad-pencil failure class; G02 is **PASS / CLOSED** with evidence in `dev/dogfood/g02-broad-pencil-v11/README.md`.
- PR #44 removed generation-tagged Python module filenames from current `src`, preserved serialized v9/v10/v11 replay identities, and added a CI invariant preventing generation-tagged `src/**/*.py` basenames from returning.
- PR #45 promoted the verified `1.0.3 / A14 / v1.0.3_gesture_renderer_quality` candidate to `main` and added explicit v1.0.3 publication intent.
- New sessions select `pillow-pencil-contact-v11 / 1`. Explicit v9 remains the v1.0.2 replay authority and explicit v10 remains available for rc1/rc2 replay.
- The installable R23 runtime/legacy namespace remains **physically retired** from current `src`.
- New work continues through one stage-free `DrawingSession` orchestration route.

## Stable candidate authority

Before publication, the selected package was rebuilt from `release/1.0.3-stable` commit `0de885e6d3f2ed6ac857c46e60875cc8c5c9f727` and verified by CI run `34749311565`.

- root tree: `996836ef4c2188ad39e621550575e0d9780d288f`
- package tree: `5758c5efa60d80a0d483bcb3573258e34d609055`
- workflow artifact: `10315122558`
- candidate artifact ZIP SHA-256: `2c7650e252b2b2f253630724bd35a30c348bd3114eebf034e45ec4f2cbdfe04a`
- candidate wheel: `img2drawing-1.0.3-py3-none-any.whl`
- candidate wheel SHA-256: `eaecfeb08100640211d3de73ea6dcfd1557d097c85318c814e217a3eb4265567`
- candidate wheel METADATA: `Name: img2drawing`, `Version: 1.0.3`

`dev/release/vnext/V1_0_3_STABLE_PROMOTION.json` is the exact authority for this pre-publication candidate. The package tree remained unchanged through publication-control commits.

## Published release authority

Post-merge main CI run `34749869989` passed all current runtime, instruction-graph, active-suite, historical, B17, and B18 gates. Publish workflow run `34749920471` then created GitHub Release `v1.0.3` from main commit `d6151ba8dfef8dc37ef5cddd24c2c6c974d53976`.

Published assets are independently recorded by GitHub with these digests:

- `img2drawing-1.0.3-py3-none-any.whl` — SHA-256 `89061b74984e1ffbb78b48fa1de81aacd64c9d4bfb2ec6baadc41b703bc240f7`
- `img2drawing-1.0.3.tar.gz` — SHA-256 `08067b1aec8384a94dc323d6ea511be84ffe006069f5180ff3c44c9d9a1dd4c4`

The published wheel hash differs from the stable-candidate workflow wheel because the publication workflow performs a fresh build on the final main release commit. The package source tree is the same verified stable package tree; candidate and published build hashes are therefore separate evidence authorities rather than interchangeable values.

## Stable contract

Stable selection remains supported by G01 gesture closure, G02 broad-pencil closure, thin v10→v11 exactness, current fast/canonical exactness, explicit historical v9/v10 replay, B17 package/install checks, and immutable v1.0.2/B18 history.

The immutable v1.0.3 contract snapshot is `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`. The exact stable-candidate artifact authority is `dev/release/vnext/V1_0_3_STABLE_PROMOTION.json`. The older `CONTRACT_FREEZE.json` remains the immutable v1.0.2/A10 authority and must not be rewritten.

## Remaining work for v1.0.3

None. **v1.0.3 is CLOSED as a published stable release.**

Future changes start from the `Unreleased` section of `CHANGELOG.md` and must not mutate the v1.0.3 tag/release or its frozen contract evidence.

## Historical B18 boundary

At the B18 implementation freeze, the product foundation was **frozen through B18** and the formal **D01–D06 not started** campaign was still future work. Those phrases are historical evidence only and do not describe current sequencing.

## Authority map

- current published stable: Git tag / GitHub Release `v1.0.3` + `docs/releases/v1.0.3.md`;
- release main commit: `d6151ba8dfef8dc37ef5cddd24c2c6c974d53976`;
- exact stable candidate: `dev/release/vnext/V1_0_3_STABLE_PROMOTION.json`;
- immutable v1.0.3 contract: `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- G01 evidence: `dev/dogfood/g01-gesture-rc2/README.md`;
- G02 evidence: `dev/dogfood/g02-broad-pencil-v11/README.md`;
- rc1 renderer promotion evidence: `dev/release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- deployable behavior: `skills/img2drawing/SKILL.md` + references;
- immutable v1.0.2 snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`.
