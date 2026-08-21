# P2 Primary Axes

Preserve P1 energy while stating head direction, shoulder/pelvis tilt, limb
directions and attached-object extent. Axes explain relationships; they are not a
substitute for observation.

## Representation boundary
P2 is axes-only.

Allowed:
- head cross-axis;
- shoulder axis;
- pelvis axis;
- single major arm direction chains;
- single major leg direction chains;
- attached-object extent/breadth axis when relevant.

Do not add:
- closed ribcage or pelvis masses;
- paired limb contours / limb thickness;
- hand or foot blocks;
- joint anatomy;
- clothing block-in;
- final contour or shading.

## Hardening order
On a subject-specific P2, review in this order:

1. **Preserve P1**
   - dominant crown→support gesture is still readable;
   - support/counterbalance roles have not changed.

2. **Head direction + shoulder axis**
   - head cross-axis matches face tilt/turn;
   - shoulder axis uses subject-derived endpoints and tilt.

3. **Pelvis counter-tilt**
   - pelvis axis explains the torso/pelvis relationship rather than becoming an
     unrelated horizontal bar;
   - compare shoulder and pelvis together.

4. **Arm direction chains**
   - each chain originates at the shoulder;
   - elbow-to-wrist direction change is explicit;
   - hanging-arm endpoint is not shortened into the torso.

5. **Leg direction chains**
   - each chain originates from the pelvis/hip region;
   - support leg remains weight-bearing;
   - counterbalance leg diverges according to the subject;
   - do not turn the axes into pant-leg contours.

6. **Whole-view contract check**
   - axes clarify P1 without replacing it;
   - no P3 volume vocabulary has leaked in.

## Useful local review intents
- `head_shoulders`: head cross-axis + shoulder tilt;
- `torso_pelvis`: shoulder/pelvis counter-tilt;
- `arms`: both arm direction chains;
- `pelvis_legs`: pelvis + support/counterbalance chains.

## Dogfood lessons
The first P2 pass can be structurally complete yet still wrong in axis direction.
Correct high-impact torso/head axes before polishing limb chains.

A successful correction action is not a PASS by itself. Re-render and inspect fresh
local evidence, then update `remaining_concerns`.

P2 is ready to advance only when:
- head/shoulder/pelvis axes explain the same pose established by P1;
- both arm chains and both leg chains are credible at axis abstraction;
- support/counterbalance roles remain clear;
- no major axis-level mismatch remains;
- no downstream mass/detail has been introduced.
