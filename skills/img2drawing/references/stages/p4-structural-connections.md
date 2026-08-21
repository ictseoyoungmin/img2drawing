# P4 Structural Connections

P4 turns P3 masses into a connected mannequin. It does **not** clean the final silhouette.

## Structural ownership

Read and draw:
- shoulder insertion into upper-arm/sleeve mass;
- elbow change-of-direction as a transition/wedge, not a dot;
- wrist direction and hand block;
- pelvis→thigh insertion;
- knee plane / directional break;
- ankle→foot transition and simple grounded foot block;
- major attachment/overlap when present.

Preserve P1 gesture, P2 axes, P3 occupied-volume masses and negative spaces.

## Transition, not symbol

A joint mark must explain how two neighboring masses connect.

Bad:
- a circular elbow dot;
- a horizontal knee tick floating inside a leg;
- a shoe shape detached from the ankle;
- a hand polygon floating beside the sleeve.

Better:
- a short cross-plane or wedge whose endpoints agree with both sides of the limb mass;
- an ankle bridge that flows into a simple foot block;
- an occluded hand block that visibly enters the waistband/pocket instead of drawing a complete floating hand.

## Clothing-aware articulation

When loose clothing hides the anatomical joint:
- infer only the **functional transition needed to explain the visible chain**;
- do not expose a naked elbow/knee shape through the sleeve or jeans;
- use the observed clothing volume as the outer evidence;
- keep folds, seams and polished clothing contour for P5 or later.

## Grounding

P4 must no longer end long leg masses at anonymous line endpoints.
Where the subject shows feet:
- establish ankle narrowing / direction;
- add simple shoe/foot blocks;
- verify the sole/landing relation against the subject;
- preserve support-vs-counterbalance roles.

## Hardening order

1. shoulder→elbow→wrist continuity;
2. wrist→hand overlap;
3. pelvis→thigh insertion;
4. knee directional plane;
5. ankle→foot and ground contact;
6. fresh whole-view chain check;
7. fresh local residual-mismatch sweep.

If P4 requires moving an entire P3 mass to make a joint work, reopen P3 instead of
hiding the upstream error with articulation.
