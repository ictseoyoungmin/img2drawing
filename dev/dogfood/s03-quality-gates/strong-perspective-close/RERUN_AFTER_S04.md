# S03.1 rerun after S04.1 anti-normalization patch

Status: **READY / NOT_RUN**  
Reference: same Gojo strong-perspective close figure  
Reference SHA-256: `393e0ca4870079aa1e4723b13847c9d3fcec0750bd659a7827d00d891280a40d`  
Skill/source baseline: `main` after PR #52 (`18419e558a0cf7892261f6061cc8e49416beb441`)

This rerun exists to disprove or confirm the S04.1 diagnosis. It is **not** a new drawing target and must not be biased by showing the worker the earlier failed outputs or the S04 residual analysis.

## Fresh-worker isolation

A valid worker receives only:

- the current img2drawing skill/runtime from the baseline above;
- the exact reference image identified by the SHA-256 above;
- the ordinary user drawing request appropriate to the original task.

Do **not** provide:

- the Astra/Claude/Gemini comparison images;
- `review.md` from the first run;
- `dev/dogfood/s04-residual-ownership/README.md`;
- coordinates, corrected session data, prior solution strokes, or a list of the expected fixes;
- extra prompt text saying "do not normalize the hand" or "preserve the reference identity" beyond what the current skill itself already says.

The test is whether the **skill instructions themselves** change fresh-worker behavior.

## Ordinary task intent

The worker should be asked to make a reference-faithful img2drawing croquis/drawing using the supported runtime, with enough face/hair/clothing detail to identify the subject, no image generation or raster repair, and normal correction/review loops until the requested finish is reached.

Do not turn the request into a special benchmark prompt that names the previous failures.

## Required evidence

Preserve:

1. exact reference identity/hash;
2. worker/model/configuration when available;
3. fresh-worker confirmation;
4. complete canonical `session.json` from action 0 → latest;
5. final PNG from that session;
6. action-0→latest GIF, normally `every_n=4`, using the same pencil renderer family;
7. reference/final comparison evidence;
8. top three remaining visible residuals;
9. KEEP / SOFTEN / RETIRE audit;
10. final PASS/BLOCKED verdict.

Do not reconstruct a lost history from final coordinates and call it canonical provenance.

## Primary disproof tests

### D1 — supplied-instance authority

PASS requires that the supplied reference instance remains the identity/style authority.

The worker may simplify according to the requested drawing mode, but it must not replace the visible hairstyle, face design, eyewear/head detail, clothing design, pose, or silhouette with a remembered canonical or alternate design merely because that version is more familiar or seems preferable.

If a higher-priority limitation prevents faithful preservation, the worker must surface the limitation rather than silently substituting another design. Such a run is not a visual PASS for S03.1, but it is an honest authority outcome.

### D2 — visible projection before anatomy normalization

PASS requires that the near hand/terminal is solved from visible wrist entry, projected envelope, overlap, negative space, and terminal orientation.

A surprising or awkward image-space hand may trigger re-observation, but must not be flipped, unfolded, re-chiralized, rotated, or otherwise repaired toward expected anatomy unless the reference evidence itself supports that change.

### D3 — anti-symbol specificity

PASS requires instance-specific head/hair/hand/body relations rather than:

- starburst/radial hair symbols;
- generic mitten/fan hand;
- circle-head feature placement;
- rail/tube limbs;
- generic garment primitives that erase the projected pose.

### D4 — retirement and hierarchy

PASS requires replaced construction/search marks to be retired or intentionally subordinated. Recognition plus a field of faint scaffold lines is not sufficient.

### D5 — perspective propagation

PASS requires the strong projection to propagate across the connected figure, not stop at one enlarged head/hand while torso and surrounding relations remain diagrammatically flat.

## Renderer boundary

This rerun does not test broad-pencil material quality and does not authorize renderer modification.

A renderer candidate may only be recorded if authored geometry is judged correct and the same visible defect persists in weight/taper/terminal/grain/deposition. Any defect still explainable by point placement, overlap, ownership, projection, identity, or retirement remains instruction/geometry-owned.

## Verdict rule

`PASS` requires all five disproof tests above plus complete canonical evidence.

`BLOCKED` is required when any blocking authority/geometry/provenance failure remains. A visually attractive result with reconstructed history cannot substitute for a canonical fresh run.

If PASS is achieved, update the class `README.md` and current `review.md` without deleting the historical blocked evidence from Git history. If BLOCKED, record the new highest-impact owner before any further instruction change.
