# S03.1 strong-perspective close figure

State: **NOT_RUN**

Use a reference where camera proximity or foreshortening makes near/far scale and overlap materially important. This class exists to test whether the updated instruction graph propagates depth through the connected figure rather than expressing perspective only as one enlarged local mass.

## Fresh-worker task contract

The worker receives the current skill, normal runtime, and exact reference. It must not receive prior solution strokes or the earlier failure output as an answer template.

Preserve the artifacts and fill a review using `../REVIEW_TEMPLATE.md`.

## Primary visual questions

- Does head scale/facing connect coherently into neck/shoulder, torso, pelvis, and legs?
- Are near/mid/far groups visible through projected spacing, apparent width, overlap, and terminal orientation?
- Does a near feature avoid becoming an isolated oversized symbol while the rest of the body stays diagrammatically flat?
- Are hidden continuations inferred only where entry/reappearance evidence supports them?
- Do hair, jaw, collar, arm, and environment boundaries keep separate physical owners?
- Are long context lines tied to actual planes/edges rather than generic perspective decoration?
- After local corrections, does the whole become more spatially specific rather than merely more detailed?

## Failure signatures to watch

- large near head with flat torso/pelvis/leg chain;
- limbs converted to parallel rails after foreshortening;
- symmetrical normalization of a strongly asymmetric projection;
- hair/body/background tangents caused by convenience strokes;
- unexplained vanishing-point rays or floor lines;
- weak construction retained because local detail is recognizable.

## Reopen routing

```text
projected spacing / overlap / path is wrong
→ observation or construction owner

local contour is plausible but parent depth relation is wrong
→ reopen parent perspective/orientation premise

geometry survives comparison but weight/taper/terminal/material still fails
→ record only as S04 renderer candidate; do not patch renderer here
```

## Required evidence

Before changing `State` from `NOT_RUN`, append or link a completed review containing:

- exact reference identity;
- canonical session provenance;
- final PNG and action-0→latest GIF;
- comparison evidence;
- top remaining residuals;
- KEEP/SOFTEN/RETIRE audit;
- PASS/BLOCKED verdict.

No evidence has been recorded yet.
