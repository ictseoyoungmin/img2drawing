# A9 — Astra authoring absorption

State: **CLOSED**

## Purpose

Absorb only reusable authoring mechanics exposed by the successful GPT-6 Astra observed-croquis
run. The run is evidence about workflow friction, not a source of answer geometry.

A9 does **not** copy the subject image, authored coordinates, solution scripts, control-point
tables, or final drawing into the deployable skill. It does not add a model-specific route,
automatic artistic scoring, a runtime stage, or a second history model.

## Evidence distilled from the run

The curated v1.0.0 session contained 490 actions: 358 stroke additions, 120 replacements,
12 deletions, and no fill actions. The relevant implementation signals were:

1. **Material-only replacement dominated correction cost.** 111 of the 120 replacements were
   intended to keep geometry while reducing premature endpoint taper at connected boundaries.
2. **The old replacement call could violate that intent.** Because `replace_stroke()` requires
   points to be supplied again, 15 smooth strokes were resubmitted as control-point polylines while
   the correction rationale claimed geometry was retained.
3. **A shared smooth-curve authoring utility was missing.** The successful worker implemented a
   local Catmull-Rom sampler in its run workspace instead of using package functionality.
4. **One material family was missing a continuity-oriented endpoint behavior.** Repeated connected
   edges needed very low taper even though the global `form_pencil` defaults remained useful for
   ordinary contour release.
5. **Good correction scope followed semantic relations.** The worker authored/reviewed coherent
   groups such as one contour relation, hair mass, equipment subassembly, or contact rather than
   arbitrary stroke counts, then used fresh renders and replacement/deletion rather than line
   accumulation.

## Absorbed product changes

### Geometry-preserving material retune

`img2drawing.vnext.retune_stroke()` resolves the current replacement descendant and reuses the
existing `replace_stroke` history action while preserving the current points, semantic part/role,
confidence, layer, stable stroke identity, and explicitly authored pressure.

Derived pressure is regenerated when the tool is retuned so changes to taper/pressure can take
effect. Existing action metadata, including authored control-point/interpolation notes when
present, is carried forward. No new persistence action or schema is introduced.

### Shared Catmull-Rom sampling

`img2drawing.vnext.sample_catmull_rom()` provides deterministic curve sampling with approximate
arc-length spacing so workers do not need to recreate spline math per task. It is an authoring
utility, not geometry authority. Guidance explicitly requires splitting real cusps, corners,
tangency breaks, component joins, or other topology changes rather than smoothing through them.

### Continuous-edge pencil

`continuous_pencil` keeps the `form_pencil` material family while reducing endpoint taper to
approximately zero. The existing `form_pencil` defaults remain unchanged. The preset applies to
any observed continuous boundary; it is not a mechanical-object preset.

### Reusable authoring discipline

The instruction graph now makes two distinctions explicit:

- organize related marks/corrections by one coherent visible or structural problem rather than an
  arbitrary stroke count;
- distinguish a **geometry residual** from a **material residual** before editing. Correct points
  are retained for material-only changes, while wrong geometry is explicitly replaced or edited.

Curve smoothness follows observed topology rather than a preference for splines.

## Deliberately not absorbed

- Astra's subject-specific coordinates or control-point tables;
- its task-local drawing scripts;
- its answer image as a worker example;
- automatic likeness, quality, or completion scoring;
- model-name checks or an Astra-specific runtime path;
- semantic-group lifecycle state or stage gates;
- a new persisted action kind for retuning.

## Contract effect

- Package: `1.0.1`
- Public contract identity: `DrawingSession/1.0.1-vnext`
- Release revision: `A9`
- `DrawingSession` member set: unchanged
- package-root exports: unchanged
- persisted schemas: unchanged
- canonical `RenderProfile`: unchanged
- R23 checkpoint compatibility: unchanged
- specialized `img2drawing.vnext` surface: adds `retune_stroke` and `sample_catmull_rom`
- tool preset registry: adds `continuous_pencil`

## Validation

Mechanical regression covers:

- exact point preservation through `retune_stroke()`;
- stable stroke identity, role, part, confidence, layer, and metadata;
- explicit-pressure preservation and derived-pressure regeneration;
- checkpoint/resume parity after a retune;
- unchanged `form_pencil` behavior alongside the low-taper preset;
- deterministic shared curve sampling;
- no widening of the canonical package-root API.

A9 does not count as D01–D06 artistic validation. The next integrated step remains a fresh sealed
D01 run using the current package without access to the Astra answer/session geometry.