# img2drawing roadmap

Updated: 2026-09-13
Workflow: Bottleneck · one highest-impact open problem at a time

The v1.0.3 release cycle is closed. New work starts from the published v1.0.3 baseline and must preserve its immutable tag/freeze/replay evidence.

## Closed foundation

- v1.0.0 established the stage-free skill/runtime surface.
- v1.0.1 added authoring ergonomics.
- v1.0.2 promoted exact local-first timelapse.
- post-v1.0.2 cleanup physically retired the R23 runtime/legacy cluster.
- G01 closed gesture-mode/runtime/instruction alignment.
- G02 closed the reported square broad-terminal and flat broad-graphite failure class with v11.
- G03–G06 integrated, froze, verified, and published v1.0.3 / A14.

## Current sequence

```text
G01 gesture behavior validation                    CLOSED
G02 broad-pencil material/terminal hardening       CLOSED
G03 integrate validated rc3 into main              CLOSED
G04 stable-promotion decision                      CLOSED → v1.0.3
G05 stable freeze and wheel verification           CLOSED
G06 explicit publish manifest and publish          CLOSED
T01 terminal_mode semantic → rendered pixels       ACTIVE
NEXT PRODUCT BOTTLENECK                            T01
```

### G05 — stable freeze and wheel verification — CLOSED

The published package remains frozen as `1.0.3 / A14 / v1.0.3_gesture_renderer_quality`. `CONTRACT_FREEZE_V1_0_3.json` and `V1_0_3_STABLE_PROMOTION.json` are immutable release evidence.

### G06 — publish — CLOSED

Git tag / GitHub Release `v1.0.3` targets `d6151ba8dfef8dc37ef5cddd24c2c6c974d53976`. Later source work does not mutate that tag or its package tree.

### T01 — semantic terminal rendering — ACTIVE

**Observed contract gap:** `resolve_markmaking(..., terminal_mode=...)` persisted `contact / gentle / flick / residue`, and the instruction graph described distinct terminal behavior, but v11 did not directly consume that semantic field. The public semantic choice therefore was not an end-to-end pixel contract.

**Narrow slice:**

```text
persisted terminal_mode
→ current renderer prepare_stroke
→ bounded physical terminal envelope
→ shared v11 material deposition
→ canonical / fast exact output
```

**Implementation boundary:**

- additive renderer identity `pillow-pencil-contact-v12 / 1`;
- semantic Python filename, not a generation-tagged source basename;
- `contact` must remain pixel-identical to explicit v11;
- `gentle`, `flick`, and `residue` must differ with identical geometry/material inputs;
- terminal behavior may alter deposition/pressure only, not authored path geometry;
- non-contact behavior is measured over physical arc length after deterministic trajectory resampling;
- v9/v10/v11 replay identities remain registered and immutable.

**Closure gates:**

- [ ] current `RenderProfile.canonical()` selects v12;
- [ ] contact v12 ↔ v11 pixel exact;
- [ ] all four public terminal modes produce distinct rendered pixels from the same geometry;
- [ ] terminal change remains spatially bounded to the suffix;
- [ ] v12 canonical final ↔ fast final pixel exact;
- [ ] explicit v11 material/replay regression remains green;
- [ ] v1.0.3 stable verifier is anchored to immutable tag/package-tree evidence rather than mutable HEAD;
- [ ] full current + historical + B17/B18 CI green.

Do not widen T01 into anisotropic graphite, new brush families, or a general renderer rewrite. Those are separate later bottlenecks only if evidence selects them after T01 closes.

## Later candidates

Not active while T01 is open:

- deeper graphite contact realism such as directional edge breakup/deposition;
- fresh unseen-reference/cross-subject generalization dogfood;
- deprecated root-shim compatibility cleanup;
- representative teaching examples when they are strong enough not to become answer templates.

## Authority

- current mutable truth: `STATUS.md`;
- current published stable: Git tag/GitHub Release `v1.0.3` + `docs/releases/v1.0.3.md`;
- v1.0.3 freeze: `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- T01 implementation: current source + active tests;
- immutable v1.0.2 snapshot: `dev/release/vnext/CONTRACT_FREEZE.json`.
