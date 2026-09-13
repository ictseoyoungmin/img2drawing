# img2drawing current status

Updated: 2026-09-13

```text
PUBLISHED STABLE:   v1.0.3 · DrawingSession/1.0.3-vnext · A14
RELEASE TAG:        v1.0.3 → d6151ba8dfef8dc37ef5cddd24c2c6c974d53976
CURRENT RENDERER:   pillow-pencil-contact-v11/1
RENDERER POLICY:    no additive v12 for this quality cycle
ACTIVE BOTTLENECK:  Q01 · v11 quality-control + instruction-gate redesign
PACKAGE VERSION:    no new RC/version authorized during design
HISTORICAL REPLAY:  v1.0.3 package/tag remains immutable pixel authority
G01 GESTURE:        PASS/CLOSED
G02 BROAD PENCIL:   PASS/CLOSED
STABLE SOURCE:      release/1.0.3-stable @ 0de885e6d3f2ed6ac857c46e60875cc8c5c9f727
STABLE WHEEL GATE:  CI 34749311565 · package tree 5758c5efa60d80a0d483bcb3573258e34d609055
MAIN RELEASE CI:    34749869989 · PASS
PUBLISH WORKFLOW:   34749920471 · PASS
PUBLISH STATE:      GitHub Release v1.0.3 published
```

## Current truth

- `v1.0.3` is the latest **published stable** release and remains CLOSED.
- The Git tag `v1.0.3` and GitHub Release both target main commit `d6151ba8dfef8dc37ef5cddd24c2c6c974d53976`.
- New development has selected **Q01: v11 quality-control + instruction-gate redesign** as the next bottleneck.
- PR #48's additive `v12` experiment was explicitly abandoned without merge. Renderer generation numbers are not a feature counter.
- The redesign keeps `pillow-pencil-contact-v11 / 1` as the current renderer family and moves exact behavior identity toward a persisted renderer contract digest plus immutable package/tag boundary.
- No `1.0.4rc1` or other package-version bump is authorized during design. Version selection happens only after fresh-worker dogfood and runtime validation close.
- The installable R23 runtime/legacy namespace remains **physically retired** from current `src`.
- New work continues through one stage-free `DrawingSession` orchestration route.

## Why Q01 is active

Recent figure outputs exposed a higher-impact failure than terminal rendering alone: correct prose exists in the skill, but workers can still accept generic rail-like limbs, parallel hair strands, symbolic props/feet, weak line hierarchy, arbitrary context marks, and excessive surviving construction/search lines.

The bottleneck is therefore **instruction execution closure**:

```text
reference evidence
→ semantic-group anchors / ownership / geometry claim
→ authored marks
→ fresh render
→ anti-symbol + hierarchy + retirement audit
→ whole-subject recheck
→ accept, revise, or reopen parent premise
```

Design authority: `V11_QUALITY_CONTROL_REDESIGN.md`.

## Renderer/replay direction

The current registry exposes a contract digest but `RenderProfile` persists only renderer id/version. Q01/Q06 will redesign this boundary so that current v11 can improve without creating v12/v13 solely to distinguish every implementation patch.

Target replay rule:

- renderer family + matching contract digest → exact replay eligible;
- same family + different digest → fail closed or require explicit migration rather than silently claiming exact replay;
- published `v1.0.3` package/tag/freeze remains the canonical authority for its original v11 pixel behavior.

Historical implementation accumulation in active `src` is not the long-term replay strategy.

## Stable release authority

Before publication, the selected package was rebuilt from `release/1.0.3-stable` commit `0de885e6d3f2ed6ac857c46e60875cc8c5c9f727` and verified by CI run `34749311565`.

- root tree: `996836ef4c2188ad39e621550575e0d9780d288f`
- package tree: `5758c5efa60d80a0d483bcb3573258e34d609055`
- workflow artifact: `10315122558`
- candidate artifact ZIP SHA-256: `2c7650e252b2b2f253630724bd35a30c348bd3114eebf034e45ec4f2cbdfe04a`
- candidate wheel: `img2drawing-1.0.3-py3-none-any.whl`
- candidate wheel SHA-256: `eaecfeb08100640211d3de73ea6dcfd1557d097c85318c814e217a3eb4265567`

`dev/release/vnext/V1_0_3_STABLE_PROMOTION.json` remains exact pre-publication authority. No current design work may rewrite it.

## Published release authority

Post-merge main CI run `34749869989` passed all current runtime, instruction-graph, active-suite, historical, B17, and B18 gates. Publish workflow run `34749920471` created GitHub Release `v1.0.3` from main commit `d6151ba8dfef8dc37ef5cddd24c2c6c974d53976`.

Published assets:

- `img2drawing-1.0.3-py3-none-any.whl` — SHA-256 `89061b74984e1ffbb78b48fa1de81aacd64c9d4bfb2ec6baadc41b703bc240f7`
- `img2drawing-1.0.3.tar.gz` — SHA-256 `08067b1aec8384a94dc323d6ea511be84ffe006069f5180ff3c44c9d9a1dd4c4`

## Historical B18 boundary

At the B18 implementation freeze, the product foundation was **frozen through B18** and the formal **D01–D06 not started** campaign was still future work. Those phrases are historical evidence only and do not describe current sequencing.

## Authority map

- active design: `V11_QUALITY_CONTROL_REDESIGN.md`;
- current published stable: Git tag / GitHub Release `v1.0.3` + `docs/releases/v1.0.3.md`;
- exact stable candidate: `dev/release/vnext/V1_0_3_STABLE_PROMOTION.json`;
- immutable v1.0.3 contract: `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- G01 evidence: `dev/dogfood/g01-gesture-rc2/README.md`;
- G02 evidence: `dev/dogfood/g02-broad-pencil-v11/README.md`;
- immutable v1.0.2 snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`.
