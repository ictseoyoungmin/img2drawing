# Residual correction

A residual is a visible mismatch between the current drawing and its reference authority or
declared intent.

Use the loop:

`inspect current render → name mismatch → rank impact → choose responsible premise → edit → inspect fresh render`

For observed finished/substantially-resolved work, close the loop through
`visual-quality-gates.md` before accepting the edited semantic group.

## Residual description

Describe what is wrong as a relationship, not a vague quality label. Prefer:
- “far knee is too low relative to pelvis” over “leg feels off”;
- “hair contour is too round at the jaw handoff” over “head needs detail”;
- “shoe toe points forward but reference turns outward” over “foot is simple”;
- “connected part is too narrow after the joint” over “needs more detail.”

Also name false ownership when present:
- “hair stroke continues into the sleeve although ownership changes at the shoulder”;
- “context diagonal has no visible plane/edge owner”;
- “rifle rail overlaps the torso without a resolved front/behind handoff.”

## Scope

Use a global correction when pose, mass, balance, scale, orientation, topology, depth propagation,
or a large silhouette premise is wrong. Use a local correction only when the parent structure is
credible and the mismatch is genuinely bounded.

Do not route by the noun that looks wrong. A foot residual can belong to the local foot,
the parent leg chain, the ground relation, or contour ownership. A component residual can belong
to its local boundary, parent axis, anchor relation, overlap, or contact. When the responsible
scope is uncertain, use `residual-routing.md` to select the smallest leaf that can actually repair
the relationship and to identify when an upstream premise must be reopened.

## Authority drift is an upstream residual

Canonical authority and anti-normalization are defined in `../foundation/reference-authority.md`.
This leaf owns the correction decision: if a proposed fix becomes more plausible or familiar but
less faithful to the supplied authority, reject that fix and reopen the responsible observation or
parent geometry. Use `../observation/visual-observation.md` when the visible evidence itself is
uncertain, then re-run `visual-quality-gates.md` before acceptance.

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
  ownership, or other spatial fact is wrong;
- **material residual** — the path and owner are already correct, but width, pressure, taper,
  opacity, grade, grain, terminal, or another rendering property makes the line read incorrectly.

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

Before accepting the corrected group, identify its visible authority, neighboring anchors, line
owners, geometry claim, and the visual evidence that would disprove the fix. Use
`visual-quality-gates.md` rather than accepting a group because it merely became cleaner.

The group is not a stage and does not earn preservation. If the fresh render shows that its parent
premise was wrong, replace the responsible geometry rather than continuing to polish the group.

Fix one to three highest-impact residuals at a time. After every mutation, inspect a fresh
render; do not accept a correction from stale evidence.

## Busier is not better

After the fresh render, ask whether the whole became more specific or merely busier.

Escalate upstream when:

- a region gains lines but not subject-specific geometry;
- a limb becomes cleaner yet remains rails/tubes;
- hair gains strands while mass/clump ownership is still unresolved;
- prop details multiply while thickness/contact remain unclear;
- context lines accumulate without visible owners;
- local parts improve while the whole becomes flatter, more parallel, more symmetric, or less
  convincingly foreshortened;
- a correction introduces a new tangent/merge/ownership conflict;
- a correction becomes more anatomically conventional or more canonically familiar while drifting
  away from readable reference evidence.

A repeated local repair that leaves the same mismatch visible is an escalation signal, not
a request for more local strokes. Re-observe the parent relation and route upstream.

The Agent decides whether the mismatch is resolved. Tooling may record evidence and edits
but must not emit an artistic verdict on the Agent's behalf.

## Runtime provenance boundary

This leaf decides **what** must change and **why**. The supported `record_residual() → corrective
edit → inspect() → resolve_residual()` call sequence, `observation_id` binding, compatibility notes,
and freshness requirements are owned by `../api/public-surface.md`.

Use that API owner when executing the correction; do not duplicate runtime mutation tutorials in
review leaves.
