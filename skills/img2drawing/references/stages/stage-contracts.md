# Stage contracts

A StageSpec explains **how to work**. A StageContract freezes **how far the representation may progress**.

The contract is not an artistic score and does not decide whether pose/anatomy is correct.

## P1 — Gesture / Weight Path
Owns craniofacial direction, whole-body gesture, pelvis weight transfer, support/counterbalance and early major prop axis.
It must not contain ribcage/pelvis mass contours, full limb thickness, joint anatomy, clothing contour or facial detail.

## P2 — Primary Axes
P2 is deliberately **axes-only**.

It may add:
- head cross-axis;
- shoulder axis;
- pelvis axis;
- major arm/leg axes;
- attached-object extent/breadth axis.

It must not add:
- ribcage side/mass contour;
- closed pelvis mass;
- full arm/thigh/shin thickness;
- hand or foot/boot blocks;
- joint anatomy;
- clothing block-in;
- final silhouette.

If a stage example image contains those forbidden forms, it is over-developed for this contract. **Do not widen P2 to match a picture.**

## P3 — Connected Primary Masses
P3 unlocks organic head/ribcage/pelvis/limb/prop masses and torso bridge, while detailed joint articulation remains forbidden.

## P4 — Mannequin / Structural Connections
P4 unlocks functional joint transitions, hands/feet blocks and attachment/overlap logic, but not polished contour or tonal finish.

## P5 — Clean Block-in
P5 unlocks decisive silhouette, major clothing contour and construction-line retirement. It still stops before tonal rendering and micro texture.

## Contract review
Every StageReviewRecord includes `contract_findings`.

The worker should answer:
- Did the drawing remain inside the allowed representation?
- Did it omit required stage-owned information?
- Did downstream vocabulary leak in early?

The contract is the authority. A stage example image beside the stage reference is
illustration, never a competing contract.
