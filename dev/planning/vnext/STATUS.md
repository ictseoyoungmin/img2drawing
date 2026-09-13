# img2drawing current status

Updated: 2026-09-13

```text
PUBLISHED STABLE:   v1.0.2 · DrawingSession/1.0.2-vnext · A10
RC1 IN MAIN:        v1.0.3rc1 · A11 · renderer v10 introduction
RC2 IN MAIN:        v1.0.3rc2 · A12 · G01 gesture runtime alignment
RC3 IN MAIN:        v1.0.3rc3 · A13 · broad-pencil renderer v11
STABLE CANDIDATE:   v1.0.3 · DrawingSession/1.0.3-vnext · A14
STABLE BRANCH:      release/1.0.3-stable
CURRENT RENDERER:   new sessions → pillow-pencil-contact-v11/1
HISTORICAL REPLAY:  explicit v9/1 and v10/1 sessions remain supported
G01 GESTURE:        PASS/CLOSED
G02 BROAD PENCIL:   PASS/CLOSED
STABLE WHEEL:       VERIFIED · CI 34749311565 · package tree 5758c5efa60d80a0d483bcb3573258e34d609055
RELEASE INTENT:     v1.0.3
PUBLISH STATE:      GitHub Release pending
NEXT GATE:          publish-intent PR → main CI → automatic GitHub Release verification
```

## Current truth

- `v1.0.2` remains the latest **published** immutable stable release until the v1.0.3 publish manifest is merged and the automatic release workflow succeeds.
- PR #42 integrated gesture/runtime corrective rc2; G01 is **PASS / CLOSED** with evidence in `dev/dogfood/g01-gesture-rc2/README.md`.
- PR #43 integrated `1.0.3rc3 / A13`; G02 broad-pencil material quality is **PASS / CLOSED for the reported failure class**.
- PR #44 removed generation-tagged Python module filenames from current `src`, preserved serialized v9/v10/v11 replay identities, and added a CI invariant preventing such filenames from returning.
- `1.0.3 / A14 / v1.0.3_gesture_renderer_quality` is the selected stable candidate.
- New v1.0.3 sessions select `pillow-pencil-contact-v11 / 1`. Explicit v9 remains the v1.0.2 replay authority and explicit v10 remains available for rc1/rc2 replay.
- The installable R23 runtime/legacy namespace remains **physically retired** from current `src`.
- New work continues through one stage-free `DrawingSession` orchestration route.

## Stable promotion evidence

The selected stable package was rebuilt from `release/1.0.3-stable` commit `0de885e6d3f2ed6ac857c46e60875cc8c5c9f727` and verified by CI run `34749311565`.

- root tree: `996836ef4c2188ad39e621550575e0d9780d288f`
- package tree: `5758c5efa60d80a0d483bcb3573258e34d609055`
- workflow artifact: `10315122558`
- artifact ZIP SHA-256: `2c7650e252b2b2f253630724bd35a30c348bd3114eebf034e45ec4f2cbdfe04a`
- wheel: `img2drawing-1.0.3-py3-none-any.whl`
- wheel SHA-256: `eaecfeb08100640211d3de73ea6dcfd1557d097c85318c814e217a3eb4265567`
- wheel METADATA: `Name: img2drawing`, `Version: 1.0.3`

Stable selection remains supported by G01 gesture closure, G02 broad-pencil closure, thin v10→v11 exactness, current fast/canonical exactness, explicit historical v9/v10 replay, B17 package/install checks, and immutable v1.0.2/B18 history.

The stable contract snapshot is `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`. The exact rebuilt artifact authority is `dev/release/vnext/V1_0_3_STABLE_PROMOTION.json`. The older `CONTRACT_FREEZE.json` remains the immutable v1.0.2/A10 authority and must not be rewritten.

## Remaining work

1. Add and validate the explicit `dev/release/publish/v1.0.3.json` manifest.
2. Merge the publish-intent PR to `main` with its head SHA pinned after PR CI is green.
3. Verify post-merge `main` CI and the automatic `img2drawing-publish-release` workflow.
4. Verify GitHub Release `v1.0.3`, its tag target, wheel/sdist assets, and release hashes.
5. Close documentation state from release-intent to **PUBLISHED STABLE v1.0.3** after the release exists.

## Historical B18 boundary

At the B18 implementation freeze, the product foundation was **frozen through B18** and the formal **D01–D06 not started** campaign was still future work. Those phrases are historical evidence only and do not describe current sequencing.

## Authority map

- publish intent: `release/v1.0.3-publish-intent` + this file;
- exact stable artifact: `dev/release/vnext/V1_0_3_STABLE_PROMOTION.json`;
- G01 evidence: `dev/dogfood/g01-gesture-rc2/README.md`;
- G02 evidence: `dev/dogfood/g02-broad-pencil-v11/README.md`;
- rc1 renderer promotion evidence: `dev/release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- currently published stable until workflow completion: `docs/releases/v1.0.2.md`;
- selected v1.0.3 stable notes: `docs/releases/v1.0.3.md`;
- deployable behavior: `skills/img2drawing/SKILL.md` + references;
- immutable v1.0.2 snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`;
- immutable v1.0.3 snapshot: `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`.
