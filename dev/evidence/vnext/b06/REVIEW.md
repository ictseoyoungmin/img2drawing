# B06 correction review

Fixture: [`dev/dogfood/vnext-b06/run.py`](../../../dogfood/vnext-b06/run.py) on the
accepted B05 subject-only construction.

The committed inspection sheets are `global-before.png`, `global-after.png`, and
`local-after.png`; each is a normal `InspectionSheet` containing the subject, raw
drawing, contrast overlay, and selected ROIs. The machine-readable provenance is in
[`b06_correction_trace.json`](b06_correction_trace.json).

## Direct visual comparison

- `global-before.png` (`inspection_id=000002`) shows the seeded near-arm premise as a
  long, over-vertical cue that reads like a pole and breaks the foreground overlap.
- `global-after.png` (`inspection_id=000003`) removes that cue and restores the authored
  bent near-arm path; the near-arm ROI and whole-figure overlay read as one foreground
  mass again.
- `local-after.png` (`inspection_id=000004`) follows the global repair with a bounded
  cross-contour segment edit. Its endpoints stay anchored while the middle contour is
  smoother.

These are visual observations by the Agent, not an automatic score. The trace binds
each claim to before/after drawing-state hashes, observation ID, action IDs, and fresh
inspection IDs, then verifies the same correction memory after checkpoint/resume.
