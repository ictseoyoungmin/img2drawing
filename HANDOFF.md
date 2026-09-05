# img2drawing project handoff

Current direction: **publish v1.0.0 as the bounded A8 stable baseline, then absorb generalized
Astra authoring lessons in v1.0.1.**

Runtime/package version: `1.0.0` (`DrawingSession/1.0.0-vnext`).

## Current truth

- B00–B18 and A1–A8 are CLOSED.
- The deployable skill starts at `skills/img2drawing/SKILL.md`; its references remain the only
  drawing-instruction authority.
- v1.0.0 adds release identity/documentation/showcase evidence, not new post-A8 drawing behavior.
- The curated GPT-6 Astra observed-croquis result demonstrates a 490-action, explicit-stroke,
  line-only session with 0 fill actions and exact canonical PNG/replay final parity.
- The demo is positive capability evidence, not a formal D01-D06 PASS and not an answer template.
- Subject-specific Astra scripts, coordinates, and control-point tables must not enter the skill or
  fresh-worker input surface.
- `dev/release/vnext/CONTRACT_FREEZE.json` is the stable package/API/schema/render snapshot.
- R23 remains explicit compatibility only; physical retirement remains a later bounded decision.

## Read first

1. `README.md`
2. `showcase/entries/croquis-sniper-girl-astra-v1/README.md`
3. `docs/releases/v1.0.0.md`
4. `skills/img2drawing/SKILL.md`
5. `dev/planning/vnext/STATUS.md`
6. `dev/planning/vnext/ROADMAP.md`
7. `dev/planning/vnext/VALIDATION_RELEASE.md`

## Next work — v1.0.1

Absorb the Astra run's reusable authoring lessons only where they remove demonstrated friction.
Current high-value candidates are:

- geometry-preserving `retune_stroke()`-style ergonomics so tool/taper changes cannot accidentally
  resample good geometry;
- a small shared curve-sampling utility so capable workers do not repeatedly rebuild spline code;
- continuous-edge pencil handling for real connected boundaries without globally flattening normal
  pencil taper;
- reusable semantic authored-element grouping and replacement/deletion ergonomics where current
  public APIs are unnecessarily verbose.

Do not add model-specific branches, subject-specific coordinates, a new stage/lifecycle, or
automatic artistic scoring.

After this bounded absorption pass, return to fresh sealed D01-D06 validation. The Astra demo may
serve as a human quality reference, but never as worker input or coordinate authority.

## Authority

- current state: `dev/planning/vnext/STATUS.md`
- sequence: `dev/planning/vnext/ROADMAP.md`
- stable release notes: `docs/releases/v1.0.0.md`
- curated demo: `showcase/entries/croquis-sniper-girl-astra-v1/`
- formal future validation: `dev/planning/vnext/VALIDATION_RELEASE.md`
- stable machine-readable contract: `dev/release/vnext/CONTRACT_FREEZE.json`
- runtime retirement inventory: `dev/planning/vnext/R03_RUNTIME_OWNERSHIP_INVENTORY.md`
