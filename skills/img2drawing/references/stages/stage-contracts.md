# Stage contracts

A StageSpec explains **how to work**. A StageContract freezes **how far the representation
may progress**.

The contract is not an artistic score and does not decide whether pose or anatomy is
correct.

## The pipeline in one table

Each stage settles one class of information. A stage is not "more lines than the last one";
it is a different question answered.

| Stage | Question it answers | Information it adds |
|---|---|---|
| P1 Gesture | How is this person standing? | flow, balance, centre of gravity |
| P2 Primary Axes | Where are the bones and joints? | axes, joints, direction |
| P3 Primary Masses | What volume does the body occupy? | ribcage, pelvis and limb masses |
| P4 Structural Connections | How does the real form connect to the body? | clothing, hair, equipment structure |
| P5 Clean Block-in | Which lines actually survive? | decided silhouette and internal line |

## P1 — Gesture / Weight Path
Owns head position and tilt, line of action, shoulder and pelvis tilt, limb direction
paths, ground contact, the overall silhouette envelope, and the major prop axis.

Must not contain facial features, hair, clothing, muscle definition or prop detail.

## P2 — Primary Axes
Owns joint positions, head centreline and face direction, the neck/ribcage/pelvis axes,
limb segment directions, and the prop's length and tilt against the body.

Joint circles and lightly cylindrical segment axes belong here. Finished limb contour,
clothing, hair and facial features do not.

## P3 — Primary Masses
Owns the three-dimensional volumes, ribcage and pelvis rotation, limb taper, overlap,
perspective and whole-figure proportion.

A few garment or gear marks are allowed where they materially change the occupied volume.
Folds, seams, finished garment silhouette, hair strands, hand/foot detail and facial
features are not.

## P4 — Structural Connections
Owns hair mass on the skull, garment structure over the body, waistline and openings, hand
and foot form, footwear, and the prop's major structure and body contact. Facial features
may be placed, minimally.

Buttons, stitching, individual hair strands, micro folds, texture and tonal rendering
are not.

## P5 — Clean Block-in
Owns the decisive silhouette, resolved face and hair, decided garment contour, tidied hands
and footwear, contour ownership between overlapping masses, and construction retirement.

Tonal shading, texture, excessive folds, fine skin rendering and structure-changing
beautification are not.

## Contract review
Every StageReviewRecord includes `contract_findings`.

The worker should answer:
- Did the drawing remain inside the allowed representation?
- Did it omit required stage-owned information?
- Did downstream vocabulary leak in early?

## Pipeline overview image

`pipeline-overview.png` beside this file shows one subject carried through all five stages
on a single sheet. It is the reference rendering of this pipeline: open it to see how much
changes between consecutive stages, and how each stage stays incomplete on purpose.

It illustrates the contracts; where a drawn line and a contract disagree, the contract
wins.
