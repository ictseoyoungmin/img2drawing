# P5 Clean Block-in

P5 states the verified figure as a readable clean block-in. It is **not** a beauty pass
and it must not hide an upstream structural defect.

## What P5 owns

- decisive outer silhouette;
- major clothing silhouette;
- major internal contour breaks that explain the silhouette;
- hand/foot silhouette from verified P4 blocks;
- construction-line retirement.

Preserve P1 gesture, P2 axes, P3 occupied-volume masses and P4 connection logic.

## Construction retirement

Do not erase construction merely because a clean result looks nicer.

First draw the verified P5 silhouette. Then retire redundant construction:
- P2 axes usually become very faint;
- P1 centre gesture may survive faintly if it still explains weight;
- P3 mass guides recede once a P5 contour replaces them;
- P4 internal joint planes survive only when they still explain a directional break.

Retirement should be replayable (`soft_lift` / explicit deletion), not a destructive
raster cleanup.

## Line hierarchy

P5 outer contour may be approximately as wide as the dominant P1 gesture.
Expression comes from pressure/taper variation, not from making all other lines ghost-thin.

Use:
- strong but not ink-black outer contour;
- slightly subordinate major internal breaks;
- faint surviving construction only.

## Major silhouette vs. micro detail

Allowed:
- hair outer grouping;
- cardigan outer envelope and opening;
- tank-top neckline / major opening;
- jeans waist and crotch/inner-leg split;
- simple hand/foot silhouette;
- one or two major overlap lines needed to explain form.

Not yet:
- knit texture;
- denim seams/stitching;
- many folds;
- fingers;
- sneaker panel details;
- facial features;
- shading.

## Fresh residual sweep

Before ADVANCE ask:
- does the subject read immediately from silhouette?
- are shoulder, waist, leg spread and feet still credible?
- did cleanup accidentally change verified structure?
- did any old construction line remain dark enough to compete with the contour?
- did a major visible clothing/hair envelope get omitted?

If contour cannot fit the verified P1–P4 structure, reopen the earliest responsible stage.


## Silhouette ownership / contour separation

Adjacent visible masses must not become one continuous contour merely because their
strokes are close, parallel, or visually convenient to connect.

Distinguish:
- **outer contour** — the mass that actually touches the background;
- **overlap contour** — an internal boundary where one mass continues inside another
  mass's outer silhouette.

Example: when long hair crosses over a cardigan sleeve, hair may own the outer
silhouette above the shoulder, then hand off silhouette ownership to the cardigan.
The lower hair edge should continue as a separate overlap contour inside the garment,
not ride the sleeve boundary down to the hand.

A renderer does not need to literally merge two strokes for a weld to occur. Separate
strokes that come within a few pixels and share a near-parallel tangent can read as
one continuous line after normal display/downsampling.

`review.measure_contour_contact()` provides **mechanical evidence only** for an
Agent-selected contour pair: minimum sampled distance, closest points, local tangent
angle, and near-contact sample fraction. It never decides whether the contact is
semantically correct.

Fresh P5 review should explicitly inspect high-risk handoffs:
- hair ↔ shoulder / sleeve;
- garment hem ↔ jeans;
- hand ↔ pocket / waistband;
- overlapping limbs / props.


## Large attached-object topology

When a large attached object materially changes silhouette or overlap, P5 must not leave
it as two generic rails or one undifferentiated capsule.

Preserve its verified P1/P2 axis and P3 extent, then expose only the **major topology**
that makes the object readable at clean-block-in scale:

- major width changes;
- dominant subpart masses;
- one or two large openings/cutouts;
- primary attachment/sling/handle relationship;
- object↔body overlap ownership.

For a long tool/prop this means the worker should ask:

1. Where does the silhouette widen/narrow?
2. Which major subparts change the silhouette?
3. Which internal break is required to understand the topology?
4. Which micro-details can still be omitted?
5. Does the object remain a separate contour owner from the body?

If the global axis/extent is already credible, reopen P5 rather than needlessly moving
P1–P3. If the object cannot be made correct without changing its primary extent/breadth,
reopen the earliest responsible stage instead.
