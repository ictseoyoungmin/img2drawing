# A6 — Markmaking vocabulary and runtime-awareness boundary

Status: OPEN on `release/1.0.3-rc`

## Problem

The drawing worker must not have to read the renderer implementation in order to draw, but it also
must not behave as if the runtime does not exist. Previous guidance could be followed visually while
a worker still authored the final drawing through ad-hoc Pillow code. That bypasses history,
inspection, replay, render-profile authority, and finish provenance.

At the same time, renderer research showed that one global pencil behavior is not sufficient. A
single drawing may legitimately mix construction lines, gesture sweeps, weighted contours, dark
accents, hair flicks, hatching, broad graphite, and environment lines. Style policy and per-mark
vocabulary therefore need separate instruction and runtime layers.

## Boundary

The target worker is **runtime-aware and implementation-blind**.

The worker MUST know:

- `img2drawing` has a supported public runtime;
- programmatic drawing marks enter through `DrawingSession` and documented public helpers;
- the public API leaf describes how to operate that runtime;
- rendered PNGs are evidence/output, not a raster surface to edit directly;
- style policy, semantic mark role, tool preset, and authored dynamics are distinct decisions.

The ordinary drawing worker MUST NOT need to know:

- private renderer classes or module layout;
- patch-cache internals;
- renderer implementation algorithms;
- history storage implementation;
- private compatibility shims.

Reading `src/` is reserved for framework development, debugging a demonstrated runtime defect, or
an explicitly requested implementation task. It is not a prerequisite for drawing.

Pillow, NumPy, OpenCV, or similar libraries may be used for bounded evidence operations when the
skill allows them, but they are not alternative drawing runtimes. They may not author the final
stroke/fill history outside `DrawingSession`.

## Instruction-graph change

Add a cross-cutting `references/markmaking/` branch. Geometry answers **what relation to draw**;
markmaking answers **what kind of mark should express that relation**.

```text
reference / declared intent
        |
        v
observation + geometry routing
        |
        +-------------------------+
        |                         |
        v                         v
what relation changes?       what mark language fits?
construction/description     markmaking/
        |                         |
        +------------+------------+
                     v
           public runtime authoring
                     |
                     v
                 render/inspect
                     |
                     v
              residual routing
          geometry | mark | material
```

The markmaking branch initially owns:

- `style-policy.md`
- `stroke-role-vocabulary.md`
- `tool-preset-selection.md`
- `stroke-dynamics.md`
- `pressure-and-terminals.md`
- `broad-graphite.md`
- `custom-tools.md`

Review gains `markmaking-residuals.md` so a worker can distinguish a wrong path from a wrong line
language or material policy.

## Runtime model to implement after the graph is stable

The intended representation is:

```text
RenderProfile
  renderer identity
  style_preset_id / style_preset_rev
  resolved global material policy

Stroke
  semantic_role
  tool_preset_id / tool_preset_rev
  resolved_tool_state
  authored dynamics (pressure/width/opacity/taper/...)
```

Preset names explain intent; resolved state is replay authority. Historical sessions must not
silently change because a later preset revision changes.

## Initial style families

- `canonical-pencil`: authored value authority and observation fidelity first.
- `manga-light`: airy broad contact and elegant monochrome line language are intentional.
- `dry-graphite-expressive`: paper tooth, broad contact, grain, and local deposition variation are
  emphasized.

These are policies, not lifecycle stages. Different semantic line roles can coexist within one
style.

## Customization ladder

Prefer the smallest scope that expresses the intent:

```text
existing preset fits
  -> preset + per-stroke modifier

one unusual mark only
  -> one-off authored dynamics

special behavior repeats within this artwork
  -> session-local custom tool

behavior recurs across unrelated works with one clear semantic purpose
  -> candidate builtin tool preset
```

Do not promote every local experiment into the global vocabulary.

## Research that must survive integration

The 1.0.3 implementation must preserve the validated renderer research rather than replacing it:

- v9 historical replay identity;
- v10 broad radial contact and paper-fixed tooth behavior;
- local deposition variability and pressure contrast;
- physical-pixel terminal behavior and thin-flick specialization;
- ordinary-thin fast path and v9-compatible thin semantics;
- canonical/fast layer-order correctness;
- renderer/contract-aware persistent patch cache identity;
- `window-study` as thin-preservation/performance evidence;
- scaled-width `window-study` as broad-contact performance evidence;
- material-stress fixtures for broad graphite and flick behavior.

## Acceptance criteria for this slice

1. The shipped instruction graph explicitly exposes the markmaking branch.
2. A programmatic drawing worker is told before authoring marks that the public runtime exists and
   must be used.
3. The worker is explicitly told not to inspect the whole implementation for ordinary drawing.
4. The worker is explicitly told that raw Pillow/NumPy/OpenCV raster drawing is not a replacement
   for `DrawingSession` history authoring.
5. Mark selection guidance separates geometry, semantic role, style policy, tool preset, and
   per-stroke dynamics.
6. Residual routing can distinguish geometry errors from mark-language/material-policy errors.
7. Runtime data-model implementation begins only after these semantic boundaries are committed.
