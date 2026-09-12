# G01 gesture rc2 dogfood evidence

Date: 2026-09-13  
Candidate: **1.0.3rc2 / A12 / `v1.0.3rc2_gesture_runtime_alignment`**  
Reference: same rifle-bearing full-body subject used for the rc1 reopen  
Scope: pure gesture + unqualified gesture drawing (constructive default)

## Why G01 reopened

The rc1 dogfood exposed two reusable failures:

1. `DrawingIntent(drawing_mode="gesture")` was rejected although the skill defines gesture drawing
   as a user-facing mode;
2. anti-faceted construction guidance could overcorrect into a smooth generic circle/bean/oval/
   capsule language, so removing sharp polygons did not by itself produce subject-specific gesture.

During the rc2 rerun a third discoverability issue was found: semantic markmaking preset IDs such as
`gesture-flow` are not necessarily literal `DrawingSession.draw(tool=...)` names. Passing
`tool="gesture-flow"` directly failed closed. The public resolver is now the documented adapter:
`resolve_mark_for_intent(..., tool_preset="gesture-flow")` followed by
`session.draw(..., **mark.draw_kwargs())`.

## Corrective candidate

rc2 makes the following bounded changes:

- adds `gesture` to the public drawing-intent vocabulary and supplies a public `ModeGuide`;
- preserves the single stage-free `DrawingSession` architecture;
- rejects both hard construction icons and informationally empty rounded stock masses;
- requires observed head facing/profile, torso asymmetry, hip shelf/near-far relation, and
  leg-attachment evidence when those relations are visible;
- explicitly preserves **reference-supported roundness** instead of inventing corners merely to
  avoid a circle/blob appearance;
- documents and tests the semantic markmaking-preset → runtime draw adapter;
- leaves the rc1 renderer/timelapse implementation unchanged, so the frozen rc1 renderer promotion
  evidence remains applicable to that subsystem.

## Visual correction loop

The same reference was redrawn through independent fresh `DrawingSession` histories for pure and
constructive gesture. Earlier iterations were deliberately rejected rather than treated as passes:

- coarse unsampled control points produced visibly polygonal curves;
- closed head curves still read as circle-head shorthand;
- paired hip curves could still close into a capsule/bowl;
- later passes corrected those authoring errors using the documented `sample_catmull_rom()` helper,
  split true cusps/joins into separate strokes, and retained reference-specific anchors instead of
  adding arbitrary angularity.

The final v8 pass keeps the genuinely rounded bob-hair and shorts/hip silhouette because the
reference supports those curves, while preserving enough information to prevent a stock primitive
read:

### Pure gesture v8

- directional crown + face/jaw + nape/facing relation;
- both arm chains and both leg flows;
- shoulder tilt and support;
- waist/hip-to-thigh attachment relations;
- rifle counter-diagonal and body overlap;
- no scaffold-only early finish.

Local artifact: `pure_gesture_rc2_v8.png`  
SHA-256: `46bc0f079bdfaa99557149e66aa48018a6f1368bc15fd98932f4a91f148756b8`

### Constructive gesture v8

Adds to the pure read:

- torso near/far side and turn axes;
- differentiated near-arm inner/outer volume;
- jacket/shorts anchors and crotch/hip attachment structure;
- differentiated leg width transitions;
- a reference-supported near-thigh strap cue;
- stronger near/far hierarchy without turning the figure into faceted geometry.

Local artifact: `constructive_gesture_rc2_v8.png`  
SHA-256: `cb7772aa000726a6d337e9fa173b1cfb2abecbcdfd107976b6e248491a9a9922`

Comparison board SHA-256: `d471fde34aa6dacf5678f4629eb9d0db8f8dd322d72decfa736b4b803aca3b6c`

The binary dogfood images are not release/package inputs. The hashes identify the reviewed local
artifacts; this repository record captures the decision and reproducible failure/correction logic.

## Verdict

**G01 target failure class: PASS / CLOSED for rc2.**

This is a narrow verdict. It means the rc1 gesture-mode integration gap, orientationless circle-head
failure, faceted-mass failure, and generic rounded-mass overcorrection are no longer accepted by the
current runtime/instruction contract and the same-reference fresh-session result can satisfy that
contract.

It does **not** claim:

- production croquis/detail quality;
- cross-subject or cross-agent generalization;
- that every rounded silhouette is wrong;
- stable-v1.0.3 readiness by itself.

## Next bottleneck discovered outside G01

Stable promotion remains blocked by an independent renderer/material-quality defect already observed
with broad pencil marks: thick strokes can read too much like a digital ribbon, graphite/tooth feel
is weak, and terminals can appear blunt/square. That issue belongs to the pencil renderer/markmaking
material layer rather than gesture construction and should be closed before a stable v1.0.3
promotion decision.
