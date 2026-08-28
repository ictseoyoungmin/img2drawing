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
| P1 Gesture | How is this person standing? | construction centrelines, joints, limb flow |
| P2 Primary Axes | How long is each bone and how is it turned? | measured segments, ribcage/pelvis boxes |
| P3 Primary Masses | What volume does the body occupy? | ribcage, pelvis and limb masses |
| P4 Structural Connections | How does the real form connect to the body? | clothing, hair, equipment structure |
| P5 Clean Block-in | Which lines actually survive? | decided silhouette and internal line |

## P1 — Gesture / Construction Centrelines
Owns the observed head outline with its curved facial centreline and eye-line cross, the spine's
S-curve from behind the neck, the pelvis and shoulder centrelines, every joint centre, the curvature of each limb, occluded
limbs, foot direction and ground contact, the silhouette envelope and the major prop axis.

P1 may include an open neck connection from the jaw into the clavicle so the head does not
float above the torso. This is a connection cue only, not the measured neck axis; P2 owns
that independent axis.

P1 is a whole-body pose hypothesis, not a few lines. Each foot states the direction it points and its
foreshortening, because foot direction carries body direction. Neither the head nor a foot
may be a generic ellipse dropped in to fill the slot. Must not contain
facial features beyond the centreline and eye-line, hair, garment structure, footwear
detail, muscle or closed volume — and must not merge the face and spine centrelines, join
joints with straight lines, or drop an occluded limb.

P1 defaults to one flowing centre-path curve per arm and leg. It must pass through the
observed joint centres rather than bracket garment width. An optional second cue is allowed
only to explain a curvature reversal or necessary silhouette-envelope fact, remains
subordinate and has non-metric spacing. P2 must preserve the P1 pose intent and joint
evidence while independently measuring shoulder -> elbow -> wrist and hip -> knee -> ankle
axes, segment length/foreshortening, neck axis, turned ribcage and pelvis boxes, and
hand/foot placement blocks.

## P2 — Primary Axes
Owns segment length and foreshortening, the neck axis, the ribcage and pelvis boxes and
their turn, hand and foot placement blocks, and the prop's length and tilt against the
body. It may correct a P1 joint when the subject says so.

P1 observed curvature; P2 measures the span. P2 must not copy P1 flow-line spacing as a
thickness or mass measurement. Finished limb contour, clothing, hair and
facial features do not belong here.

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

Tonal shading, texture, excessive folds and fine skin rendering are not.

If P5 exposes a structural error, correct it — reopen the earliest responsible stage. P5
may not paint over a wrong structure, but it is not forbidden from fixing one.

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
