# A6 — structural orientation hardening

Status: **CLOSED**

## Trigger

Exploratory current-version dogfood produced a repeated visual failure pattern before formal
D01 sealing: individual contours could look plausible while the whole figure became flatter,
more frontal, more symmetric, or less twisted than the observed subject. Broad value/hatching
could then make that weakened construction look more finished without repairing the underlying
pose.

This is guidance evidence, not a D01 pass/fail result. The formal D01–D06 campaign still starts
from fresh sealed input under `VALIDATION_RELEASE.md`.

## Goal

Strengthen the deployable instruction graph so an observed figure moves through:

```text
whole observation
→ spatial mass/orientation hypothesis
→ structural-read check
→ local description/value only when structure supports it
```

without introducing a runtime stage machine, automatic pose estimator, numeric angle solver, or
new drawing API.

## Changes

### 1. Observation now separates tilt from turn

`references/observation/visual-observation.md` now asks for relative turn, near/far side,
projected centerline/cross-axis, visible plane exposure, and prop/body depth in addition to
screen-space tilt and ordinary proportions.

The guidance explicitly treats a clean silhouette as insufficient evidence that the spatial pose
has been understood.

### 2. Dedicated orientation/twist construction ownership

New leaf: `references/construction/orientation-and-twist.md`.

It owns:

- head / ribcage / pelvis turn relative to the viewer;
- near/far side and visible plane exposure;
- projected centerline/cross-axis reasoning;
- relative rotation between head, ribcage, and pelvis;
- shoulder/pelvis counter-relation;
- compression/stretch across the torso;
- prop depth against body planes;
- recurrent whole-pose flattening/symmetry drift.

It does not own final contour, anatomy detail, or value rendering.

### 3. Structural read before description

`SKILL.md` now makes a reversible drawing prerequisite explicit. Before local identity/detail or
broad tone, an observed figure should already communicate:

- head/ribcage/pelvis orientation and relative twist;
- shoulder/pelvis relation;
- support and weight tendency;
- major arm/leg anchor chains;
- stance and large negative spaces;
- major prop axis/body overlap.

This is not a lifecycle stage. Later evidence may invalidate the premise and route upstream
immediately.

### 4. Croquis broad-value policy tightened

`modes/croquis.md` now keeps broad value regions and dense regular hatch fields off by default.
Broad tone is eligible only when the request/intent materially calls for it and only after the
pose remains structurally readable without that tone.

The `fill_region` runtime capability remains available. A6 changes when the drawing guidance
should choose broad value, not the API contract.

### 5. Whole-pose flattening becomes an explicit residual class

`review/residual-routing.md` now routes cases where local parts look reasonable but the whole
pose loses turn/twist/asymmetry. It sends those cases upstream to orientation, mass, balance,
observation, or prop-depth ownership instead of encouraging local contour polish.

## Non-goals

A6 does not:

- change `DrawingSession`, schemas, render profile, fill-region implementation, or persistence;
- add an orientation stage or completion gate;
- require exact reconstructed 3D angles from a single image;
- add automatic pose/anatomy inference;
- remove tonal-study/value capability;
- claim formal D01 success from exploratory dogfood.

## Mechanical closure

`dev/tests/test_skill_surface_boundary.py` freezes the instruction changes mechanically:

- the new orientation/twist leaf is part of the construction graph;
- `SKILL.md`, `INDEX.md`, and residual routing expose it;
- observation includes tilt-vs-turn, near/far, and projected-axis language;
- croquis broad value is off by default;
- the whole-pose flattening residual routes upstream;
- no runtime-stage or release-control-plane language leaks into the deployable skill.

Mechanical CI proves the guidance surface is internally consistent. It does not prove that a
fresh worker will infer pose/orientation correctly; D01 must test that visually.

## Next

D01 difficult observed croquis remains the next bottleneck. Its review should prioritize
orientation/twist, support, limb anchors, negative spaces, and prop/body overlap before judging
line finish. A result must not pass because broad value or clean contour makes a flattened pose
look polished.
