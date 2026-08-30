# B05 Initial Construct Review

Status: `PASS`; B05 was reopened for right-arm alignment and reclosed after the
updated subject-only render passed independent visual review.

## Input boundary

The canonical dogfood received only:

- `dev/dogfood/target-subject/subject.png`;
- the B05 drawing mode and skill instructions.

`dev/dogfood/vnext-b05/ideal-stroke-reference.png` was not loaded by the runner. It is
kept as a capability exemplar only. The construction marks are authored in the runner's
subject-space x/y/z hypothesis and projected into the existing `DrawingSession`.

## Evidence reviewed

- `initial_construct.png` — the current raw whole-figure construct;
- `inspection_sheet.png` — subject, raw drawing, contrast overlay, and focused crops;
- `contrast_overlay.png` — the current direct same-coordinate comparison;
- `dev/dogfood/vnext-b05/run-subject-only/inspections/000001/` — the canonical current
  raw, overlay, and inspection artifacts.

## Reopen reason

The canonical subject-only raw drawing and `ideal-stroke-reference.png` do not agree
on the near/right arm's visible envelope and shoulder-to-elbow-to-forearm path. This
slice is reopened for that arm only; all other prior B05 closure findings remain
unchanged until the new arm evidence is reviewed.

## Findings retained from the prior closure

- `PASS`: a back/three-quarter turn is present in the torso, head-turn plane, neck-to-back
  connection, and prop relationship rather than a frontal torso scaffold.
- `PASS`: the near/right arm is a broad bent, depth-aware path that overlaps the torso;
  it is not a single vertical drop or a joint-circle chain.
- `PASS`: the far arm keeps a visible elbow projection toward image-left even though the
  rifle occludes its continuation.
- `PASS`: head, ribcage, pelvis, leg axes, knee planes, feet, and prop masses are present
  before contour or detail work.
- `PASS`: pelvis tilt, the image-left support leg, and the image-right counterbalance leg
  establish the subject-specific weight shift; the legs no longer read as parallel rails.
- `PASS`: no joint circles are used.

The phase labels remain drawing vocabulary only. The authored tuple order is preserved,
including when labels are interleaved; no runtime phase progression or advancement gate
was used.

## Reopen resolution

The reopen changed only `NEAR_ARM_CENTER`, `NEAR_ARM_OUTER`, `NEAR_ARM_INNER`, and
the two near-arm depth contours in `dev/dogfood/vnext-b05/run.py`. The accepted head,
torso, pelvis, far/left elbow, legs, feet, and prop geometry were left unchanged.

The final projected near-arm paths are:

- center: `(530,365) → (540,410) → (554,471) → (571,524) → (588,570) →
  (606,625) → (612,665) → (592,706)`;
- outer: `(545,355) → (560,400) → (581,471) → (606,530) → (613,586) →
  (629,636) → (638,671) → (620,699) → (595,726)`;
- inner: `(500,376) → (490,420) → (475,474) → (469,530) → (475,570) →
  (496,620) → (524,665) → (570,705) → (604,729)`.

The canonical runner remains subject-only; `ideal-stroke-reference.png` was not loaded
at runtime. The final native subagent review returned `PASS — ADVANCE: YES`: the arm
reads as a broad foreground mass with the target shoulder-to-elbow angle, outward
forearm turn, inward wrist/hand return, torso overlap, and no joint circles.

## Decision

`PASS`: close B05. The reopened near/right arm now matches the requested target-specific
stroke structure in the fresh subject-only evidence. B06 remains inactive pending a
separate manual activation decision.
