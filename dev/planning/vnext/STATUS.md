# img2drawing current status

Updated: 2026-09-13

```text
PUBLISHED STABLE:   v1.0.3 · DrawingSession/1.0.3-vnext · A14
RELEASE TAG:        v1.0.3 → d6151ba8dfef8dc37ef5cddd24c2c6c974d53976
CURRENT SOURCE:     1.0.4rc1 · DrawingSession/1.0.4-vnext · A15
CURRENT RENDERER:   new sessions → pillow-pencil-contact-v12/1
HISTORICAL REPLAY:  explicit v9/1, v10/1, v11/1 remain supported
G01 GESTURE:        PASS/CLOSED in v1.0.3
G02 BROAD PENCIL:   PASS/CLOSED in v1.0.3
T01 TERMINAL SEMANTICS: ACTIVE · semantic mode → rendered pixels
NEXT GATE:          T01 end-to-end pixel distinction + v11 contact exactness + canonical/fast exactness
```

## Current truth

- `v1.0.3` remains latest published stable. Its tag, GitHub Release, A14 freeze, and v11 renderer authority are immutable.
- Mutable source has opened `1.0.4rc1 / A15 / v1.0.4rc1_terminal_mode_pixels` for the selected T01 bottleneck.
- New 1.0.4rc1 sessions select additive renderer `pillow-pencil-contact-v12 / 1`.
- Explicit v9, v10, and v11 renderer identities remain registered; persisted sessions are never silently migrated.
- The installable R23 runtime/legacy namespace remains **physically retired** from current `src`.
- One stage-free `DrawingSession` remains the only normal orchestration route.

## T01 — terminal-mode semantic → pixels

The public markmaking API has long persisted four semantic terminal intents: `contact`, `gentle`, `flick`, and `residue`. v1.0.3/v11 preserved that intent in provenance but did not consume the semantic field directly in rendering; preset taper values could create indirect differences, while changing only `terminal_mode` was not a pixel contract.

The 1.0.4rc1 candidate closes that gap additively:

- `contact` delegates to v11 exactly;
- `gentle`, `flick`, and `residue` apply distinct render-time pressure/deposition envelopes over a bounded physical suffix;
- sparse authored polylines are resampled before non-contact terminal envelopes so the fade span is measured physically rather than stretched across a long segment;
- authored geometry is not moved by terminal semantics;
- canonical final and fast replay use the same v12 prepare/build path.

T01 remains ACTIVE until CI proves all terminal modes produce the intended distinct pixels, v12 contact is pixel-identical to v11, v11 historical replay remains intact, and v12 canonical/fast final frames are pixel-exact.

## Published v1.0.3 authority

- release commit: `d6151ba8dfef8dc37ef5cddd24c2c6c974d53976`;
- immutable contract: `dev/release/vnext/CONTRACT_FREEZE_V1_0_3.json`;
- stable candidate authority: `dev/release/vnext/V1_0_3_STABLE_PROMOTION.json`;
- G01 evidence: `dev/dogfood/g01-gesture-rc2/README.md`;
- G02 evidence: `dev/dogfood/g02-broad-pencil-v11/README.md`.

The v1.0.3 stable verifier is tag/tree anchored. It must not require mutable `HEAD:skills/img2drawing` to remain byte-identical to the published package after later development begins.

## Release boundary

No v1.0.4 publish manifest exists. T01 is an unreleased candidate slice, not a public release. Future publication requires a separate stable-selection/freeze/publish decision; the v1.0.3 tag and frozen evidence must not be rewritten.
