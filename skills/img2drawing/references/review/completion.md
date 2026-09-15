# Completion

Completion is an Agent decision bound to current evidence, not a checklist verdict from the
runtime. The runtime may enforce mechanical preconditions, but it does not and cannot verify that
the drawing is artistically complete.

Before finishing, inspect the current drawing and ask:
- Does the whole pose/composition/depth read correctly?
- Are major masses, balance, silhouette, overlap, grounding, and object relations credible?
- Are identity-bearing head/face/hair, hands/feet, garment, or prop features sufficiently
  resolved for the requested finish?
- Does line hierarchy actually read at final output scale?
- Have redundant construction/search lines been classified and retired where they damage clarity?
- Do any final strokes lack a clear physical/semantic owner?
- Does any blocking authority-drift residual remain?
- Are remaining non-blocking weaknesses stated honestly in `accepted_limitations`?

Use `visual-quality-gates.md` for reference-fidelity, ownership, anti-symbol, hierarchy,
retirement, whole-read, and perspective-propagation acceptance. Canonical anti-normalization
semantics live in `../foundation/reference-authority.md`; completion only treats unresolved
authority drift as a blocker.

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

## Mode-specific completion ownership

Mode-specific finish semantics belong to the matching mode leaf. For gesture drawing, use the
completion test in `../modes/gesture-drawing.md`; do not repeat or weaken its pure/constructive
criteria here. Other modes likewise retain their own finish-specific expectations.

For `finish_intent="subject"` in particular, explicitly account for:

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
`accepted_limitations`. `accepted_limitations` is not permission to hide a blocking visual mismatch.
A rationale that only discusses pose while the drawing also claims a resolved subject is not a
completion decision; it is an unexamined one.

Do not finish because a predetermined number of passes or marks has been reached. A later edit or
newly discovered residual invalidates the earlier completion decision and the ordinary correction
loop resumes.

## Runtime completion boundary

The mechanical `DrawingSession.finish()` preconditions, evidence-read requirements, open-residual
rejection, and public call behavior are owned by `../api/public-surface.md`. This leaf owns the
artistic judgment only.
