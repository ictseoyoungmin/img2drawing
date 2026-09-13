# img2drawing current status

Updated: 2026-09-13

```text
PUBLISHED STABLE:   v1.0.3 · DrawingSession/1.0.3-vnext · A14
RELEASE TAG:        v1.0.3 → d6151ba8dfef8dc37ef5cddd24c2c6c974d53976
CURRENT RENDERER:   pillow-pencil-contact-v11/1
RENDERER POLICY:    no additive v12 for this quality cycle
ACTIVE BOTTLENECK:  S03 · fresh-worker visual dogfood
S01 DESIGN:         CLOSED
S02 INSTRUCTIONS:   CLOSED · CI 34761722278 PASS
PACKAGE VERSION:    no new RC/version authorized before integrated validation
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

- `v1.0.3` remains the latest published stable release and its tag, artifacts, freeze, and historical dogfood are immutable.
- PR #48's additive `v12` experiment was abandoned without merge. Renderer generation numbers are not a feature counter.
- **S01 design closure is complete.** The quality failure taxonomy, reversible evidence-gate model, and renderer-family/replay policy agree on one architecture.
- **S02 instruction execution gates are complete.** `review/visual-quality-gates.md` is reachable from the normal worker route; line ownership, anti-symbol, perspective propagation, hierarchy, retirement, and top-residual completion checks are integrated. CI run `34761722278` passed repository/docs/runtime/instruction graph, active tests, historical evidence, B17, and B18.
- **S03 fresh-worker visual dogfood is now the active bottleneck.** No renderer pixel change is authorized before S03 evidence is classified in S04.
- The redesign keeps `pillow-pencil-contact-v11 / 1` as the current renderer family. Exact pixel identity will move to a persisted renderer contract digest plus immutable package/tag boundary before intentional current-v11 pixel divergence.
- No `1.0.4rc1` or other package-version bump is authorized yet. Version selection happens only after visual and mechanical validation close.
- The installable R23 runtime/legacy namespace remains physically retired from current `src`.

## Active S03 evidence loop

Fresh workers receive the updated skill, the reference, and the normal public runtime surface without prior solution strokes.

Required classes:

1. strong-perspective close figure;
2. full-body 3/4 figure with attached or held prop;
3. frontal or near-frontal full body;
4. head/hair close-up.

Each run must preserve canonical provenance and provide a final PNG, action-0→latest GIF, comparison evidence, top remaining residuals, and a KEEP/SOFTEN/RETIRE audit. A blocking failure in any class stays open; results are not averaged into one score.

The next decision is S04 residual ownership:

```text
wrong path / proportion / ownership / overlap / contact
→ geometry/instruction owner

correct geometry but wrong weight / taper / terminal / grain / deposition
→ renderer-material candidate
```

A renderer candidate requires both real-drawing evidence and a minimal controlled reproduction.

## Renderer/replay direction

Before current-v11 pixel behavior is intentionally changed, persisted render identity must become capable of binding:

```text
renderer_id
renderer_version
renderer_contract_digest
```

Target replay rule:

- family/version/digest match → exact replay eligible;
- same family/version with digest mismatch → fail closed or require explicit migration;
- a legacy session without a digest remains loadable under an explicitly non-exact current-source policy;
- published `v1.0.3` package/tag/freeze remains canonical authority for its original v11 behavior.

Historical implementation accumulation in active `src` is not the long-term replay strategy.

## Stable release authority

Before publication, the selected package was rebuilt from `release/1.0.3-stable` commit `0de885e6d3f2ed6ac857c46e60875cc8c5c9f727` and verified by CI run `34749311565`.

- root tree: `996836ef4c2188ad39e621550575e0d9780d288f`
- package tree: `5758c5efa60d80a0d483bcb3573258e34d609055`
- workflow artifact: `10315122558`
- candidate artifact ZIP SHA-256: `2c7650e252b2b2f253630724bd35a30c348bd3114eebf034e45ec4f2cbdfe04a`
- candidate wheel: `img2drawing-1.0.3-py3-none-any.whl`
- candidate wheel SHA-256: `eaecfeb08100640211d3de73ea6dcfd1557d097c85318c814e217a3eb4265567`

`dev/release/vnext/V1_0_3_STABLE_PROMOTION.json` remains exact pre-publication authority. Current development must not rewrite it.

## Published release authority

Post-merge main CI run `34749869989` passed all current runtime, instruction-graph, active-suite, historical, B17, and B18 gates. Publish workflow run `34749920471` created GitHub Release `v1.0.3` from main commit `d6151ba8dfef8dc37ef5cddd24c2c6c974d53976`.

Published assets:

- `img2drawing-1.0.3-py3-none-any.whl` — SHA-256 `89061b74984e1ffbb78b48fa1de81aacd64c9d4bfb2ec6baadc41b703bc240f7`
- `img2drawing-1.0.3.tar.gz` — SHA-256 `08067b1aec8384a94dc323d6ea511be84ffe006069f5180ff3c44c9d9a1dd4c4`

## Historical B18 boundary

At the B18 implementation freeze, the product foundation was **frozen through B18** and the formal **D01–D06 not started** campaign was still future work. Those phrases are historical evidence only and do not describe current sequencing.

## Authority map

- execution plan: `V11_QUALITY_CONTROL_SLICE_PLAN.md`;
- design rationale: `V11_QUALITY_CONTROL_REDESIGN.md`;
- current published stable: Git tag / GitHub Release `v1.0.3` + `docs/releases/v1.0.3.md`;
- exact stable candidate: `dev/release/vnext/V1_0_3_STABLE_PROMOTION.json`;
- immutable v1.0.3 contract: `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- G01 evidence: `dev/dogfood/g01-gesture-rc2/README.md`;
- G02 evidence: `dev/dogfood/g02-broad-pencil-v11/README.md`;
- immutable v1.0.2 snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`.
