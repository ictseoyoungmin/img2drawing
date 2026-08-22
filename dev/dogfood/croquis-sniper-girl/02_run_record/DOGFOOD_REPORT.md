# img2drawing run report — full-body croquis from a single subject photograph

Mode: **subject-only** (`subject_reference > grammar_exemplar`). No same-subject
`task_stage_targets` were supplied or used.

Canvas 512x768 at working supersample 3, mapping the 1024x1536 subject at exactly 0.5,
so every review crop box converts between subject and canvas without rounding.

## Subject reading
Back-three-quarter standing figure, torso facing away and toward image-right, head turned
further right so her right ear sits image-left of the facial mass. Weight on the far
image-left leg; the near image-right leg is braced outward and lands wider and lower.
A suppressed sniper rifle is slung across her back on a shoulder strap, its axis running
about 74 degrees from horizontal, muzzle upper-left and buttstock at the image-left hip.

## Stage history
| stage | passes | outcome |
|---|---|---|
| P1 gesture | 3 then rebuilt, 1 | advance |
| P2 primary axes | 1 then rebuilt, 2 | advance |
| P3 primary masses | 2 then rebuilt, 1 | advance |
| P4 structural connections | 2 then rebuilt, 1 | advance |
| P5 clean block-in | 1 then rebuilt, 1 | advance |

## Reopens
1. **P2 -> reopen P1.** The P2 braced-leg axis and the inherited P1 counterbalance flow
   ran as two separated near-parallel lines down the thigh, the pant-leg rail the P2
   reference forbids. Re-measurement put the subject's braced-thigh centre near canvas
   x=258-264 while the P1 flow sat at 267-273. Moving the P2 axis onto the P1 flow would
   have hardened a compensating axis, so P1 was rebuilt with a re-measured counterbalance.
2. **P5 preflight -> reopen P3.** Brightness-lifted inspection of the left flank resolved
   an outer edge the ordinary view could not: the rifle owns the silhouette down to about
   canvas y=205 and the jacket below. The inherited P3 prop mass drifted up to 16 canvas
   pixels right of the measured prop edge and the torso-left contour underfilled the
   observed occupied volume by about 12 pixels. P3 was rebuilt and P4 rebuilt on top.
3. **P5 -> reopen P5.** Close-range re-observation for the finishing pass showed three
   misplaced internal breaks: the belt is diagonal, the jacket is cropped and ends at the
   belt rather than 30 pixels below it, and the jaw break stopped well short of the
   observed face contour. P5 was rebuilt with all three corrected.

## Contract violations caught by review
- P3 pass 1 authored two boot masses. Hand and foot construction blocks are forbidden at
  P3 and belong to P4; both were hard-deleted rather than kept as a head start.
- P4 pass 1 authored full-width knee, ankle and elbow bands and a faceted mitten hand.
  All were re-authored as partial directional planes and a smooth occluded hand block.

## Silhouette ownership
`measure_contour_contact` was used as evidence at the high-risk handoffs. The prop and
garment edges met at 7 pixels with a 36 degree tangent while both were drawn as outer
contours, so ownership was split explicitly: each keeps the outer contour only where it
actually touches the background, and continues as a lighter overlap contour elsewhere.
Both bob tips were given the same treatment over the shoulders.

## Retirement
69 construction strokes were retired with replayable `soft_lift` at stage-appropriate
strengths. The dominant P1 gesture survives faintly because it still explains the weight
path. Three retired guides that still cut across the drawn eyes were removed with explicit
`delete_stroke`, because soft lift reduces stroke opacity but not the graphite this
renderer deposits from pressure.

## Post-pipeline identity pass
The task required the finished drawing to identify the subject, not only her form and
action. After P5 closed and `finish()` persisted the authoritative croquis, a declared
`P6_identity_finish` pass added eyes with irises and pupils, nose, mouth, ear, bob strand
groups and lock tips, collar, insignia patch, sling and buckles, side pouch, belt, cargo
pocket, thigh strap and pouch, sock bands, boot lacing and lug soles, and rifle scope,
turret, magazine and stock cutouts. **This pass deliberately exceeds the frozen P5 clean
block-in ceiling** and is recorded separately in `identity_pass.json` so the audited
five-stage croquis stays distinguishable from the finished deliverable.
