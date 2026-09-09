# Residual correction

A residual is a visible mismatch between the current drawing and its reference authority or
declared intent.

Use the loop:

`inspect current render → name mismatch → rank impact → choose responsible premise → edit → inspect fresh render`

## Residual description

Describe what is wrong as a relationship, not a vague quality label. Prefer:
- “far knee is too low relative to pelvis” over “leg feels off”;
- “hair contour is too round at the jaw handoff” over “head needs detail”;
- “shoe toe points forward but reference turns outward” over “foot is simple”;
- “connected part is too narrow after the joint” over “needs more detail.”

## Scope

Use a global correction when pose, mass, balance, scale, orientation, topology, or a large
silhouette premise is wrong. Use a local correction only when the parent structure is credible and
the mismatch is genuinely bounded.

Do not route by the noun that looks wrong. A foot residual can belong to the local foot,
the parent leg chain, the ground relation, or contour ownership. A component residual can belong
to its local boundary, parent axis, anchor relation, overlap, or contact. When the responsible
scope is uncertain, use `residual-routing.md` to select the smallest leaf that can actually repair
the relationship and to identify when an upstream premise must be reopened.

## Revalidate inherited construction

Earlier construction is provisional. Before refining a child contour, detail, value region, or
accent, ask whether the parent structure still agrees with the current authority. A mark does not
become correct because later marks were placed relative to it.

If the parent placement, orientation, proportion, envelope, width/depth change, overlap, contact,
negative space, or connected-part relation is wrong, replace that upstream geometry first. Do not
spend additional local marks preserving a false premise.

## Distinguish geometry residuals from material residuals

Before replacing a stroke, ask which fact is actually wrong:

- **geometry residual** — the path, anchor, silhouette, overlap, contact, cusp/corner, width relation,
  or other spatial fact is wrong;
- **material residual** — the path is already correct, but width, pressure, taper, opacity, grade,
  grain, or another rendering property makes the line read incorrectly.

For a geometry residual, replace or locally edit the responsible points. For a material residual,
preserve the points and retune the stroke. Do not re-author a correct curve merely to change taper
or weight: that can silently destroy smooth geometry, control-point intent, or topology while the
correction rationale claims that geometry was retained.

If several connected strokes share the same material residual, treat them as one semantic review
problem even though history still records explicit individual edits. Render the whole group after
the retune and verify continuity in context.

## Correct coherent groups, not arbitrary stroke counts

A correction batch should correspond to one visible problem: a connected contour interval, one
component relation, one hair-mass transition, one contact, one clothing tension family, one prop
subassembly, or another coherent relation. This keeps the scope large enough to preserve context
but small enough that the next render reveals whether the chosen cause was correct.

The group is not a stage and does not earn preservation. If the fresh render shows that its parent
premise was wrong, replace the responsible geometry rather than continuing to polish the group.

Fix one to three highest-impact residuals at a time. After every mutation, inspect a fresh
render; do not accept a correction from stale evidence.

A repeated local repair that leaves the same mismatch visible is an escalation signal, not
a request for more local strokes. Re-observe the parent relation and route upstream.

The Agent decides whether the mismatch is resolved. Tooling may record evidence and edits
but must not emit an artistic verdict on the Agent's behalf.

## Recording the correction

The current public mutation surface binds a correction to the observation that found the problem.
Author the corrective edit under the **same `observation_id` passed to `record_residual()`**, then
inspect the edited state and resolve the residual:

```python
observation_id = session.observe({"jaw": "contour sits too low at the cheek handoff"})
before_inspection_id = session.inspection_history[-1]["inspection_id"]

residual_id = session.record_residual(
    observation_id=observation_id,
    observation="jaw contour sits too low at the cheek handoff",
    scope="head/jaw",
    severity="material",
    impact_rationale="the face shape reads heavier than the reference",
    responsible_premise="jaw contour placement",
    responsible_stroke_ids=(jaw_stroke_id,),
    planned_edit="raise the jaw contour while preserving the cheek anchor",
    before_inspection_id=before_inspection_id,
)

fix_action_id = session.replace_stroke(
    jaw_stroke_id,
    corrected_jaw_points,
    observation_id=observation_id,
    reason="raise the jaw contour to the observed cheek-to-chin relation",
)
session.inspect()
after_inspection_id = session.inspection_history[-1]["inspection_id"]

session.resolve_residual(
    residual_id,
    action_ids=(fix_action_id,),
    after_inspection_id=after_inspection_id,
    rationale="the fresh inspection now matches the observed jaw handoff",
)
```

If a later `session.observe(...)` call has happened, do **not** rely on the mutation methods'
default-to-latest observation behavior for an older residual. Pass that residual's original
`observation_id` explicitly on the repairing edit. An edit authored under a different later
observation is rejected with `correction action observation mismatch`.

If the finding itself has materially changed by the time it is repaired, record it again as a new
residual under the new observation instead of pretending the old provenance still owns the fix.
Persisted historical actions may contain legacy/unobserved provenance tolerated for compatibility;
that tolerance is not the authoring contract for new corrections.

`resolve_residual()` also requires an after-inspection whose drawing state differs from the
before-inspection and matches the current drawing, so inspect *after* the edit, not before. The
runtime's freshness checks are mechanical provenance checks; the Agent must still actually look at
the fresh artifact before deciding that the visible mismatch is resolved.
