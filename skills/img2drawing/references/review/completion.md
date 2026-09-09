# Completion

Completion is an Agent decision bound to current evidence, not a checklist verdict from the
runtime. The runtime enforces a small set of mechanical preconditions so that decision is at
least bound to something real; it does not and cannot verify that the drawing is actually good.

Before finishing, inspect the current drawing and ask:
- Does the whole pose/composition read correctly?
- Are major masses, balance, silhouette, overlap, grounding, and object relations credible?
- Are identity-bearing head/face/hair, hands/feet, garment, or prop features sufficiently
  resolved for the requested finish?
- Have redundant construction/search lines been retired where they damage clarity?
- Are all material residuals resolved or explicitly accepted as limitations?

For `finish_intent="subject"` in particular, do not finish without explicitly accounting for
each of face, hair, hands/feet, clothing, and prop (the relations `resolve_finish_guide("subject")`
names): either the relation is resolved, or its absence is named in `accepted_limitations`. A
`rationale` that only discusses pose while the drawing also claims a resolved subject is not a
completion decision, it is an unexamined one.

Do not finish because a predetermined number of passes or marks has been reached. A later
edit or newly discovered material residual invalidates the earlier finish decision and the
ordinary correction loop resumes.

## What `finish()` mechanically enforces

`DrawingSession.finish()` binds the decision to the latest inspection and rejects the call
outright when:
- the canvas has zero authored actions (there is nothing to have judged);
- the Agent never called `record_evidence_read()` against the final inspection — generating
  an inspection is not the same as having looked at it, and `finish()` will not accept the
  difference;
- the inspection is stale, superseded, or predates the current intent;
- any residual is still open.

Call `session.record_evidence_read(inspection_id)` after actually viewing the inspection
artifact, not as a formality immediately after `inspect()`. None of this proves the drawing is
finished — it only proves the Agent inspected something current and read it before deciding.
