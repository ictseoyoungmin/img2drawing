# 1.0.1 stable release notes

img2drawing 1.0.1 publishes the A9 authoring-ergonomics patch over the v1.0.0 Astra-success
baseline. The release absorbs only generalized mechanics demonstrated by that run; it copies no
subject-specific answer geometry.

## What changed from 1.0.0

- `img2drawing.vnext.retune_stroke()` preserves authored geometry while changing material/tool
  behavior through the existing replacement history action;
- `img2drawing.vnext.sample_catmull_rom()` provides deterministic shared smooth-curve sampling;
- `continuous_pencil` provides low endpoint taper for genuinely continuous observed boundaries;
- instruction guidance distinguishes geometry residuals from material residuals, groups related
  marks by coherent semantic problems, and makes curve smoothness subordinate to observed topology.

The package-root API, `DrawingSession` method set, persisted schema identifiers, canonical
`RenderProfile`, and R23 checkpoint compatibility remain unchanged in structure. The stable public
contract identifier advances to `DrawingSession/1.0.1-vnext` with the package version.

## Astra evidence used

The v1.0.0 curated GPT-6 Astra observed-croquis run remains the source evidence: 490 actions,
358 stroke additions, 120 replacements, 12 deletions, 0 fill actions, 124 canonical replay frames,
and exact canonical PNG/replay final parity.

A9 specifically uses implementation-level signals from that run: 111 material-only replacements,
accidental geometry changes possible when a correct smooth path was manually resubmitted, repeated
low-taper continuity corrections, a task-local Catmull-Rom helper, and effective semantic-group
correction behavior.

See `../../../showcase/entries/croquis-sniper-girl-astra-v1/README.md`,
`../../../docs/releases/v1.0.1.md`, and
`../../planning/vnext/A9_ASTRA_AUTHORING_ABSORPTION.md`.

## What 1.0.1 does not claim

- D01-D06 formal sealed validation is not complete;
- cross-agent or cross-subject statistical generality is not claimed;
- Astra subject-specific coordinates/control-point scripts are not shipped as worker examples;
- visual quality remains Agent capability plus instruction/runtime affordance, not an automatic
  runtime PASS score;
- semantic groups are not stages or persisted lifecycle state.

## Stable contracts

- `DrawingSession` remains the canonical orchestration surface;
- observed, imaginative, and hybrid authority share one session/history/correction/output core;
- `DrawingSession/1.0.1-vnext` is the stable package public-contract identifier;
- persisted schema identifiers remain unchanged from v1.0.0;
- package-root exports remain unchanged from v1.0.0;
- R23 remains explicit compatibility only;
- `CONTRACT_FREEZE.json` pins the stable package/API/schema/render boundary.

The next integrated step is fresh sealed D01 validation.