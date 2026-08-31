# B07 direct evidence review

The representative fixture is `dev/dogfood/vnext-b07/run.py`; its committed trace is
[`b07_evidence_trace.json`](b07_evidence_trace.json).

| route | review turns | visual artifacts | generated artifacts | image reads |
|---|---:|---:|---:|---:|
| vNext quick → focused | 2 | 8 | 12 | 4 |
| preserved R23 stage-review fixture | 5 ceremonies | 12 images | 60 files | not instrumented |

`quick-inspection-sheet.png` shows the whole view before the correction. The Agent then
restores the bent near-arm premise. `focused-inspection-sheet.png` adds only the two
selected relation ROIs after a recorded escalation reason. Both sheets visibly contain
subject, raw drawing, contrast overlay, and the selected ROI tiles.

This is a direct visual inspection record, not a likeness score. The trace also proves
that each read was a valid artifact, that the current-state hashes were bound to the
read events, and that the checkpoint resumed with the same telemetry digest.
