# Completion

Completion is an Agent decision bound to current evidence, not a checklist verdict from the
runtime. The runtime enforces a small set of mechanical preconditions so that decision is at
least bound to something real; it does not and cannot verify that the drawing is actually good.

Before finishing, inspect the current drawing and ask:
- Does the whole pose/composition/depth read correctly?
- Are major masses, balance, silhouette, overlap, grounding, and object relations credible?
- Are identity-bearing head/face/hair, hands/feet, garment, or prop features sufficiently
  resolved for the requested finish?
- Does line hierarchy actually read at final output scale?
- Have redundant construction/search lines been classified and retired where they damage clarity?
- Do any final strokes lack a clear physical/semantic owner?
- Has any readable reference relation been silently normalized toward expected anatomy, symmetry,
  a remembered canonical design, or a more generic/attractive substitute?
- Are all open residual records resolved? Are any remaining non-blocking weaknesses stated
  honestly in `accepted_limitations` rather than hidden by the finish rationale?

Use `visual-quality-gates.md` for the reference-fidelity, ownership, anti-symbol, hierarchy,
retirement, whole-read, and perspective-propagation checks.

A drawing may not finish as "faithful" when a visible hand, face, hair shape, costume/accessory,
pose, terminal orientation, or other identity-bearing relation was knowingly replaced because a
more conventional anatomy or remembered design seemed preferable. If the supplied reference is
uncertain, state the uncertainty; if a higher-priority constraint prevents faithful preservation,
surface that limitation instead of silently substituting another result.

## Rank the largest remaining visible mismatches

Before final finish, name the three largest remaining visible mismatches, or explicitly state that
fewer than three remain.

For each remaining mismatch record:

```text
owner
blocking? yes/no
why it remains
why it is acceptable if non-blocking
```

This is not a requirement to invent flaws. It is a forcing function against the common failure
where "recognizable" silently becomes "finished" while obvious generic rails, symbolic feet,
parallel strand fields, ownerless context lines, dominant construction, or authority drift remain
visible.

A blocking mismatch must be repaired or routed/reopened. A non-blocking mismatch may become an
`accepted_limitation` only after the Agent consciously judges it against the requested finish.

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

For `finish_intent="subject"` in particular, do not finish without explicitly accounting for:

- whole pose/composition/depth;
- face/head/hair;
- hands/feet;
- clothing;
- prop/body relation when present;
- grounding/context when present;
- line hierarchy;
- construction retirement;
- reference-fidelity / anti-normalization.

For each relation, either it is resolved or a remaining non-blocking limitation is named in
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
