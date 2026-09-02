# Residual-driven correction

The shared vNext review loop reduces the largest visual residual in the current
drawing; it does not pass through stages.

```text
capture current snapshot
→ inspect whole / focused relation
→ name one highest-impact mismatch
→ identify responsible premise or strokes
→ replace / soft-lift / delete / add explicitly
→ render the new snapshot
→ inspect again
→ keep, revise, or finish for the declared intent
```

A correction action is not evidence of improvement. A previous inspection becomes
stale after mutation, so fresh evidence bound to the new state digest is required.
The Agent selects local crops when a subject exists. Measurements only help expose
relationships; they are not automatic authority over pose, anatomy, or likeness.
Subjectless work uses the drawing-only sheet and declared-goal observations. It cannot
request subject overlays, registration, subject-space crops, or subject measurements.

## Residual categories

- macro: pose, balance, mass, composition, silhouette
- relationship: overlap, negative space, joint chain, prop/body contact
- finish: identity relation, value grouping, edge hierarchy, line economy

While a macro residual remains, do not select micro detail as the highest-impact
issue. Compare subject ↔ drawing for observed work, declared intent ↔ drawing for
imaginative work, and preserved constraint + transformation intent for hybrid work.

## Evidence boundary

`InspectionSheet` and read-only measurements record current state and provenance,
but they do not produce an automatic PASS/FAIL. The Agent decides acceptance by
viewing the raw render, subject beside drawing, overlay, or an appropriate crop.

The default evidence budget is one tiled sheet from
`session.inspect(mode="quick")`; it accepts no ROI, guide, grid, or measurement.
Only when a relationship needs narrowing, add one to three prioritized ROIs with
`mode="focused"`. When guides, a grid, or measurements are also needed, use
`mode="deep"` with at most three ROIs and a short `escalation_reason`. These modes
are neither lifecycle states nor quality scores. The current implementation limits
the inspection presentation/read budget rather than the number of generated files.
Record which sheet or artifact was actually read with
`session.record_evidence_read(inspection_id, artifact="sheet")`. Reading an artifact
from an earlier state is not rejected, but is marked by a `stale=True` telemetry
event.

For authority-specific behavior, see [`../reference-authority.md`](../reference-authority.md).

## vNext correction records

`DrawingSession.record_residual()` anchors the Agent's concern to the current
`inspection_id`, observation, drawing-state digest, scope (`global` or a local relation),
impact rationale, responsible premise/strokes, and planned edit. The session rejects a
concern whose before inspection is no longer the current snapshot.

Use the existing explicit stroke actions for the edit, then inspect again and bind those
action IDs to fresh evidence:

```python
residual_id = session.record_residual(
    observation_id="observation-0001",
    observation="pelvis mass sits too high and weakens the weight shift",
    scope="global",
    severity="high",
    impact_rationale="the pose reads upright instead of counter-tilted",
    responsible_premise="pelvis tilt",
    responsible_stroke_ids=("pelvis", "support_leg"),
    planned_edit="replace the pelvis premise, then re-check the whole figure",
    before_inspection_id="000001",
)
new_id = session.replace_stroke(
    "pelvis",
    corrected_points,
    observation_id="observation-0001",
    reason="correct pelvis premise from the current residual",
)
sheet = session.inspect(rois=(pelvis_roi,))
session.resolve_residual(
    residual_id,
    action_ids=(new_id,),
    after_inspection_id=session.inspection_history[-1]["inspection_id"],
    rationale="fresh whole/relation inspection shows the weight shift now reads",
)
```

`decision="revise"` on `record_correction()` records an attempt without closing the
residual. `decision="keep"` (or `resolve_residual()`) closes it only when the current
after inspection is fresh and its drawing digest differs from the before snapshot. This
is correction memory, not a numerical quality gate or an automatic priority selector.

For long histories, locate current responsibility with `session.authored_elements()` and
follow replacement ancestry with `session.resolve_authored_element()` before editing.
`session.authoring_summary()` provides a bounded cursor/state-bound view without becoming
a second history. See [`authored-element-navigation.md`](authored-element-navigation.md).
