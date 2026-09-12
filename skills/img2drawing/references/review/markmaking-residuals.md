# Markmaking residuals

Use this leaf when the visible path is plausibly correct but the mark still reads wrong because of
line language or material behavior.

The purpose is to prevent two opposite errors:

- redrawing correct geometry to compensate for a material defect;
- blaming the renderer for a path, overlap, proportion, or structural error.

## Fast routing kernel

Ask these questions in order:

```text
1. Is the visible path / overlap / contact itself wrong?
   yes -> route to geometry/description/subject leaf
   no  -> continue

2. Is the semantic role wrong?
   yes -> choose the correct stroke role and public tool preset
   no  -> continue

3. Is local authored dynamics wrong?
   pressure / width / opacity / taper / terminal
   yes -> retune while preserving points
   no  -> continue

4. Is the active style policy producing the wrong material interpretation?
   yes -> change/retune style policy or record a renderer-policy defect
   no  -> continue

5. Is the runtime incapable of expressing the required public behavior?
   yes -> record a capability gap; do not bypass DrawingSession with an ad-hoc rasterizer
```

## Common residuals

- **broken continuous edge** — inspect taper/terminal before moving an already correct path;
- **blunt hair tip** — inspect thin-flick/terminal behavior before redrawing the hair direction;
- **all lines equally heavy** — inspect role/tool selection and local pressure hierarchy;
- **broad graphite too flat** — inspect broad material/style policy if geometry and value placement
  are already correct;
- **deliberately dark broad mark becomes pale** — under `canonical-pencil`, treat this as a value-
  authority/material-policy residual; under an explicitly selected `manga-light` policy, lighter
  broad contact may be intentional;
- **background competes with the subject** — inspect semantic role and tool hierarchy before
  deleting correct environment geometry.

## Proof of correction

A markmaking correction must be verified on a fresh render. State what should change in the pixels
without requiring a geometry change. If the same residual remains after a deliberate material
retune, reconsider the upstream semantic role or style policy rather than stacking more strokes.
