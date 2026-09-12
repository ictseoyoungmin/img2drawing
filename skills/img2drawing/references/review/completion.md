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
- Are all open residual records resolved? Are any remaining non-blocking weaknesses stated
  honestly in `accepted_limitations` rather than hidden by the finish rationale?

When the requested drawing mode is gesture drawing, use the level-specific completion test in
`../modes/gesture-drawing.md`. Do not finish merely because a line of action, head/ribcage/pelvis
masses, or cross-axes exist. Pure gesture must still communicate the whole action, major visible
limb chains, support, and decisive spatial relations. Constructive gesture must additionally read
as specific occupied masses and connected joint chains rather than generic blobs, tubes, or axes.
An unqualified “gesture drawing” request defaults to constructive gesture.

For gesture completion specifically, treat surviving search primitives as a visual defect when they
dominate the read. Do not accept an orientationless circle-head, a flat/sharply faceted ribcage, a
triangle/hexagon/plate pelvis, **or the opposite failure of a smooth generic bean/oval/capsule** as
finished shorthand when the observed subject provides enough evidence for more specific structure.
Facial features may be omitted in sparse gesture, but head facing plus an observable
profile/jaw/nape relation may not disappear with them. Torso and pelvis turn should preserve the
few subject-specific asymmetries that explain shoulder/back/side transitions, taper, hip shelf,
near/far exposure, and leg-attachment spacing/direction. `Rounded` alone is not a completion
criterion: a smoothly organic mass that could fit many unrelated subjects is still unresolved.

For `finish_intent="subject"` in particular, do not finish without explicitly accounting for
each of face, hair, hands/feet, clothing, and prop (the relations `resolve_finish_guide("subject")`
names): either the relation is resolved, or a remaining non-blocking limitation is named in
`accepted_limitations`. `accepted_limitations` is not a bypass for an open residual record. A
`rationale` that only discusses pose while the drawing also claims a resolved subject is not a
completion decision, it is an unexamined one.

Do not finish because a predetermined number of passes or marks has been reached. A later
edit or newly discovered material residual invalidates the earlier finish decision and the
ordinary correction loop resumes.

## What `finish()` mechanically enforces

`DrawingSession.finish()` binds the decision to the latest inspection and rejects the call
outright when:
- the current rendered drawing has no authored strokes, including a session whose earlier marks
  were all erased again;
- the Agent never called `record_evidence_read()` against the final inspection — generating
  an inspection is not the same as having looked at it;
- the inspection is stale, superseded, or predates the current intent;
- any residual record is still open.

Call `session.record_evidence_read(inspection_id)` after actually viewing the inspection
artifact, not as a formality immediately after `inspect()`. None of this proves the drawing is
finished — it only proves the Agent inspected something current and read it before deciding.

Use `accepted_limitations` for weaknesses the Agent has consciously judged non-blocking for the
requested finish. If a weakness was recorded as a residual, resolve or re-record that finding
through the residual/correction provenance chain before finishing; merely repeating it in
`accepted_limitations` does not close the residual.
