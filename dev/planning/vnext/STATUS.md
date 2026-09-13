# img2drawing current status

Updated: 2026-09-13

```text
RELEASED STABLE:    v1.0.2 · DrawingSession/1.0.2-vnext · A10
RC1 IN MAIN:        v1.0.3rc1 · A11 · renderer v10 introduction
RC2 IN MAIN:        v1.0.3rc2 · A12 · G01 gesture runtime alignment
RC CANDIDATE:       v1.0.3rc3 · DrawingSession/1.0.3-vnext · A13
RC3 BRANCH:         fix/broad-pencil-material-rc3
CURRENT RENDERER:   new sessions → pillow-pencil-contact-v11/1
HISTORICAL REPLAY:  explicit v9/1 and v10/1 sessions remain supported
G01 GESTURE:        PASS/CLOSED
G02 BROAD PENCIL:   ACTIVE · round physical terminals + stronger graphite/tooth
PUBLISH STATE:      no v1.0.3rc3 publish manifest; v1.0.2 remains latest published stable
NEXT GATE:          full CI + canonical/fast exactness + visual broad-pencil QA
```

## Current truth

- `v1.0.2` remains the latest published immutable stable release. Its tag, publish manifest, release notes, and `CONTRACT_FREEZE.json` remain historical authority.
- PR #42 integrated `1.0.3rc2 / A12` into `main` at `5cd5ad9c14875c23aca962bc5bfbbae85c18442a`; post-merge main CI passed.
- G01 gesture runtime/instruction dogfood is **PASS / CLOSED for its target failure class**. Evidence remains in `dev/dogfood/g01-gesture-rc2/README.md`.
- The next user-observed blocker is broad-pencil material quality: transitional thick strokes can expose a high-alpha rectangular continuity core, producing blunt/square terminals, while the broad core's graphite/tooth modulation can read too flat.
- `1.0.3rc3 / A13 / v1.0.3rc3_broad_pencil_material` addresses that defect with a new immutable renderer identity `pillow-pencil-contact-v11 / 1`; it does **not** rewrite v10 semantics.
- v11 delegates ordinary thin strokes byte-for-byte to v10, preserves the v10 radial material shoulder and authored-value model, adds pressure-resolved round contact at broad core terminals, and strengthens deterministic page-fixed broad graphite/tooth modulation while mean-normalizing material density.
- Explicit v9 remains the released v1.0.2 replay authority. Explicit v10 remains available for rc1/rc2 replay. New canonical profiles select v11 only after this RC3 branch is used.
- The installable R23 runtime/legacy namespace remains **physically retired** from current `src`.
- New work continues through one stage-free `DrawingSession` orchestration route.

## Mechanical G02 gates

The focused deterministic broad-pencil fixture locks three properties before integration:

1. **thin non-regression** — ordinary 2px v11 output is pixel-exact with explicit v10;
2. **terminal morphology** — a no-taper transitional broad stroke deposits graphite behind the authored endpoint instead of exposing a square/butt core cut, without materially changing body mean value;
3. **graphite/tooth read** — a broad core shows stronger deterministic local material variation while mean density remains within authored-value tolerance.

Current canonical/fast output must also remain pixel-exact because both paths consume the same registered v11 patch builder.

## Release boundary

The rc1 width×3 performance evidence remains historical authority for v10 only. Because RC3 changes renderer bytes and selects a new current renderer identity, stable v1.0.3 promotion requires fresh v11 parity/quality evidence. No stable publish manifest is authorized by this corrective slice.

## Remaining work

1. Run full branch CI and repair only actual RC3 integration failures.
2. Produce deterministic v10↔v11 broad visual evidence and confirm the user's square-terminal / weak-graphite failure is visibly reduced.
3. Verify current v11 canonical/fast exactness and thin v10↔v11 pixel non-regression.
4. If green, integrate rc3 to `main` through PR; keep v1.0.2 as latest published stable.
5. Only afterward decide stable v1.0.3 versus another RC.

## Historical B18 boundary

At the B18 implementation freeze, the product foundation was **frozen through B18** and the formal **D01–D06 not started** campaign was still future work. Those phrases are historical evidence only and do not describe current sequencing.

## Authority map

- current rc3 candidate state: `fix/broad-pencil-material-rc3` + this file;
- G01 evidence: `dev/dogfood/g01-gesture-rc2/README.md`;
- rc1 renderer promotion evidence: `dev/release/vnext/V1_0_3_RC1_PROMOTION.{md,json}`;
- latest published stable: `docs/releases/v1.0.2.md`;
- rc2 history: `docs/releases/v1.0.3rc2.md`;
- rc3 candidate notes: `docs/releases/v1.0.3rc3.md`;
- current near-term sequence: `ROADMAP.md`;
- deployable behavior: `skills/img2drawing/SKILL.md` + references;
- immutable v1.0.2 snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`.
