# S02 near-arm envelope board

This fixture is a small, subject-only evidence board for the failure discussed
in the planning document: the shoulder→elbow axis remains plausible while the
upper, middle, and lower arm envelope collapses in the drawing.

- `near-arm_fixture.json` records independent reference/drawing provenance and
  the paired normalized station measurements.
- `near-arm-envelope-board.svg` is a human-readable board; it is not a stage
  decision and contains no artistic PASS/FAIL label.

The production utility that generated the same comparison shape is
`img2drawing.compare_region_envelopes()`. Its result is bound to the frozen
pre-draw observation digest and rejects a stale drawing state when the current
state digest is supplied.
