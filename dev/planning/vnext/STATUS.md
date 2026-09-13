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
PUBLISH STATE:      v1.0.3 manifest intentionally absent until stable wheel verification
NEXT GATE:          stable branch CI → wheel metadata/hash → explicit publish manifest
```

## Current truth

- `v1.0.2` remains the latest **published** immutable stable release until the v1.0.3 publish manifest is intentionally added and merged.
- PR #42 integrated gesture/runtime corrective rc2; G01 is **PASS / CLOSED** with evidence in `dev/dogfood/g01-gesture-rc2/README.md`.
- PR #43 integrated `1.0.3rc3 / A13` at `bcc931c79a4c4cf799aec3a5265d21145bfb546b`; post-merge main CI passed all current, historical, package, and v1.0.2 freeze gates.
- G02 broad-pencil material quality is **PASS / CLOSED for the reported failure class**. Drawing-scale and 9–14 px heavy-graphite dogfood show v11 replacing the visible square/butt core termination with physical rounded contact and increasing local graphite/tooth breakup without obvious global value drift. Evidence is `dev/dogfood/g02-broad-pencil-v11/README.md`.
- `1.0.3 / A14 / v1.0.3_gesture_renderer_quality` is now the selected stable candidate on `release/1.0.3-stable`.
- New v1.0.3 sessions select `pillow-pencil-contact-v11 / 1`. Explicit v9 remains the v1.0.2 replay authority and explicit v10 remains available for rc1/rc2 replay.
- The installable R23 runtime/legacy namespace remains **physically retired** from current `src`.
- New work continues through one stage-free `DrawingSession` orchestration route.

## Stable promotion evidence

Stable selection is supported by the following independent gates:

1. **G01 gesture behavior** — public `gesture` runtime selection plus pure/constructive instruction behavior validated and corrected;
2. **G02 broad-pencil quality** — user-observed square-terminal/weak-graphite failure reproduced, corrected in v11, and visually rechecked under ordinary and heavy broad marks;
3. **thin non-regression** — ordinary 2 px v11 output is pixel-exact with explicit v10;
4. **renderer exactness** — current v11 canonical-final and fast-final pixels are exact under the active renderer-policy regression, including late lower-layer dirty recomposition;
5. **historical replay** — explicit v9 and v10 identities remain registered and resumable;
6. **package/history isolation** — B17 package/install checks and immutable v1.0.2/B18 history remain green.

The stable contract snapshot is `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`. The older `CONTRACT_FREEZE.json` remains the immutable v1.0.2/A10 authority and must not be rewritten.

## Remaining work

1. Run full CI on `release/1.0.3-stable` with package identity `1.0.3 / A14`.
2. Build the stable wheel from that exact branch HEAD and verify filename, METADATA version, and SHA-256 before publication.
3. Add the explicit `dev/release/publish/v1.0.3.json` manifest only after step 2 is green.
4. Open the stable promotion PR, rerun PR CI, merge with the head SHA pinned, and verify post-merge main CI.
5. Verify the automatic GitHub Release `v1.0.3` and its built wheel/sdist assets.

## Historical B18 boundary

At the B18 implementation freeze, the product foundation was **frozen through B18** and the formal **D01–D06 not started** campaign was still future work. Those phrases are historical evidence only and do not describe current sequencing.

## Authority map

- current stable-candidate state: `release/1.0.3-stable` + this file;
- G01 evidence: `dev/dogfood/g01-gesture-rc2/README.md`;
- G02 evidence: `dev/dogfood/g02-broad-pencil-v11/README.md`;
- rc1 renderer promotion evidence: `dev/release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- currently published stable: `docs/releases/v1.0.2.md`;
- selected v1.0.3 stable notes: `docs/releases/v1.0.3.md`;
- current near-term sequence: `ROADMAP.md`;
- deployable behavior: `skills/img2drawing/SKILL.md` + references;
- immutable v1.0.2 snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`;
- immutable v1.0.3 snapshot: `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`.
