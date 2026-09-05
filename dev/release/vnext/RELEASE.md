# 1.0.0 stable release notes

img2drawing 1.0.0 publishes the A8-aligned stage-free drawing system as the first stable
baseline. This release intentionally does **not** add new drawing/runtime behavior after the
successful Astra demonstration; it freezes the current instruction graph, package surface,
persisted schemas, renderer/replay contract, and compatibility boundary under a stable version.

## What is demonstrated

A curated GPT-6 Astra observed-croquis run shows that the current system can produce a detailed,
recognizable full-body drawing using explicit authored strokes only, while preserving whole-body
orientation, counter-turn, asymmetry, prop/body overlap, identity-bearing details, and replayable
correction history.

The demonstrated run used no `fill_region` actions and finished with 490 actions:
358 stroke additions, 120 replacements, and 12 deletions. Its end-to-end GIF samples action 0
through action 490 every four actions; the replay final PNG matches the canonical final PNG and
the decoded GIF final-frame maximum channel error is 1.

See `../../showcase/entries/croquis-sniper-girl-astra-v1/README.md` and
`../../docs/releases/v1.0.0.md`.

## What 1.0.0 does not claim

- D01-D06 formal sealed validation is not complete;
- cross-agent or cross-subject statistical generality is not claimed;
- the Astra subject-specific coordinates/control-point scripts are not shipped as worker examples;
- visual quality is still Agent capability plus instruction/runtime affordance, not an automatic
  runtime PASS score.

## Stable contracts

- `DrawingSession` remains the canonical orchestration surface;
- observed, imaginative, and hybrid authority share one session/history/correction/output core;
- `DrawingSession/1.0.0-vnext` is the stable package public-contract identifier;
- persisted schema identifiers remain unchanged from the A8 baseline;
- R23 remains explicit compatibility only;
- `CONTRACT_FREEZE.json` pins the stable package/API/schema/render boundary.

The next planned patch release is 1.0.1, focused on evidence-backed authoring ergonomics learned
from the Astra run rather than subject-specific answer imitation.
