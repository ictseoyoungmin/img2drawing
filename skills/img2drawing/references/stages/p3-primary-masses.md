# P3 Primary Masses — three-dimensional volume

**The question this stage answers: what volume does the body occupy?**

This is where the stick figure becomes a body. Wrap simple three-dimensional masses around
the P2 axes: head, ribcage, pelvis, shoulders, upper arms, forearms, thighs, calves, hands
and feet.

P3 is not a finished drawing. It is the volume the finished drawing will sit on.

## What P3 states
- torso thickness;
- ribcage and pelvis rotation;
- limb thickness and taper;
- which parts are in front of which;
- overlap;
- perspective;
- whole-figure proportion;
- the volume a large attached object occupies.

## The test that matters

A thigh is not two outlines. Ask:

> **Which way does this cylinder point?**

The same question applies to the ribcage and the pelvis. A cross-contour that states the
direction is worth more than a cleaner outline that states nothing.

## How much to draw
Simple volumes and the cross-contours that orient them. Limb taper. Overlap and
perspective cues. A few garment or gear marks **only** where they materially change the
occupied volume — the point of this stage is body volume, not decoration.

Keep out: facial features, hair strands, clothing folds and seams, finished garment
silhouette, hand and foot detail.

## Common failures
- **Parallel rails.** Two near-parallel lines per limb with no taper and no orientation.
- **A flat torso** that never states which way the ribcage is turned.
- **Symmetric widening** when only one side is wrong.
- **Overshoot.** Fixing an underfilled mass by pushing the opposite side past the subject's
  silhouette.
- **Detail smuggling.** Drawing the jacket's edge because it is easier to see than the
  volume beneath it.

## Mandatory visual assertions

P3 is visually FAIL, regardless of pass count, if any of these assertions is not supported
by the raw whole view, a subject/drawing overlay and the relevant crop:

- **Head:** the head volume follows the locked crown/chin and turn; it does not become a
  directionless symmetrical egg. Hair mass and strand detail remain deferred to P4.
- **Torso:** ribcage thickness and turn are visible in the mass and cross-contours; a flat
  rectangle or vertical tube is FAIL.
- **Arms:** near/far exposure, upper/mid/lower width and torso overlap agree with the
  subject; a plausible shoulder→elbow axis does not excuse an underfilled arm.
- **Pelvis:** breadth, rotation and both thigh insertions remain readable; a pelvis line
  that merely repeats the P2 axis is not a volume.
- **Legs:** support/counterbalance roles, taper and inter-leg negative space remain
  asymmetric; two long parallel rails are FAIL.
- **Hands/feet:** simple P3 endpoint volumes own placement. If a P2 placement block is
  still visibly duplicated beneath one, transfer ownership with `soft_lift` or
  `delete_stroke`, then prepare fresh evidence.
- **Whole figure:** the result reads as this subject's occupied volume, not a generic
  mannequin assembled from eggs, boxes and rails.

Mark every assertion `PASS`, `FAIL` or `UNCERTAIN` in the visual review. Any failed
stage-purpose assertion, critical uncertainty or missing high-risk crop forces
`decision="revise"`. If the mismatch is actually a P1/P2 axis or pose error, stop patching
P3 and reopen the earliest responsible stage.

## Hardening order
1. Head volume.
2. Ribcage volume and rotation.
3. Pelvis volume and rotation.
4. Shoulder volumes and the torso bridge.
5. Arm volumes with taper.
6. Leg volumes with taper.
7. Hands and feet as simple volumes.
8. Whole-figure proportion and overlap review.

## Useful local review intents
`head+ribcage`, `ribcage+pelvis`, `one full arm`, `one full leg`, `object volume`.
