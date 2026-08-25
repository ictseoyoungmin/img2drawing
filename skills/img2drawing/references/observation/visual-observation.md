# Visual observation

Read whole → region → part → relation. Evidence maps are aids, not semantic deciders.

## Pre-draw lock

Before drawing, record the subject’s view as an agent-authored
`ViewObservation` inside an `ObservationContract`, then freeze it with
`DrawingRun.lock_observation()`.

At minimum, observe and record:

- body view and torso turn (`front`, `back`, `side`, or a qualified three-quarter view);
- near-side role, using subject-side or image-side language when anatomy labels are uncertain;
- visibility of both arms and what occludes each one;
- major prop/body overlap order;
- explicit uncertainties that a later region review must not silently resolve.

This lock prevents a later drawing review from changing the interpretation of the
subject without invalidating the drawing branch. It does not infer pose or decide
whether the drawing is correct. If the view observation changes after drawing
starts, use `DrawingRun.reopen_observation()` so P1 and downstream evidence are
reopened together.

## Region observation

For later fidelity slices, preserve the distinction between an axis and an
occupied envelope. An arm can have a plausible shoulder→elbow axis while its
upper/mid/lower widths or visible length are badly under-drawn. Record those as
separate region evidence; do not let a landmark delta stand in for silhouette
measurement.
