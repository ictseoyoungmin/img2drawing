# P3 reference run

The P3 reference run starts from a fresh replay of the committed P1/P2 predecessor,
then hardens `P3_primary_masses` through six autonomous passes. Its first P3 branch is
intentionally audited downstream; the whole/crop/overlay result exposes a flat torso and
rail-like legs, so the runner reopens P3, archives that branch, and rebuilds it through a
fresh six-pass loop. It demonstrates simple
head, torso, pelvis, limb, hand/foot and overlap volumes while preserving the P1 pose and
P2 axes. It intentionally stops before P4 surface connections.

Rebuild it with:

```bash
python3 dev/p3_reference_run/build.py
```

## Reading the result

- `run/reviews/P3_primary_masses/pass_01/current_drawing.png` is the deliberately weak
  first mass pass.
- `run/reviews/P3_primary_masses/pass_06/current_drawing.png` is the final raw P3 render.
- `run/reviews/P3_primary_masses/pass_06/region_closure_manifest.json` records all eight
  required regions.
- `run/reviews/P3_primary_masses/pass_06/blind_visual_packet.json` and
  `visual_fidelity_review.json` are the independent visual-fidelity gate.
- `compare.png` and `overlay.png` compare the subject, P1/P2 handoff and P3 hardening.
- `run/session/checkpoint.json` is resumable with `DrawingRun.resume(run/)`.
- `p2_trace.json` preserves the predecessor trace; `canonical_trace.json` is the P3 trace.
- `run/reopens/reopen_01.json` records why the first P3 branch was invalidated and where
  its archived reviews live.

The final pass closes `head_hair`, `torso_orientation`, `near_arm`, `far_arm`, `pelvis`,
`leg_A`, `leg_B` and `attached_object`. The last region is explicitly closed as “no prop”
because the frozen subject observation says `prop=none`; the runner does not invent one.

The process review and independent blind visual review are both required before the rebuilt
run advances to `P4_structural_connections`. Review rasters are regenerable from the
checkpoint; repeated crop/overlay boards are ignored by the repository `.gitignore`.
