# Authored element navigation

Before editing a mature drawing, identify which current authored element owns the visible
problem. Use semantic fields such as part, role, action, or observation when available
instead of guessing from raw history order.

The public session can expose current authored elements and bounded authoring summaries.
Use those views to locate the current stroke or explicit ink/tone element to correct or retire.
Filter `session.authored_elements(element_type="ink")` for ink and tones. Use
[current mixed-media API](../api/mixed-media.md) for typed retrieval/replacement;
graphite-only operations do not edit ink. These are derived navigation aids, not a second
ownership lifecycle or drawing authority.

Always pair element lookup with a current visual inspection. Correct element identity does
not guarantee that the proposed geometric change is artistically correct.

## Explicit semantic group relationships

Declare `SemanticGroup(group_id, member_ids, guide_ids=(), depends_on=())` and
record a plan via `record_semantic_groups(session, groups, evidence=...)`.
Membership is explicit, disjoint, and acyclic. Inspect its current descendants
with `inspect_semantic_groups(session, plan_id)`. Changing a member or an upstream
group invalidates the corresponding review; unrelated edits do not. A split's
new fragment is not silently inherited. Redeclare a new plan after changing
membership or replacing deleted descriptive marks. Previous plans remain evidence.

Use `prepare_group_transform` with the selected group to get edits and base
cursor/state hash, then preview/apply through the existing stroke-edit API.
For an ink-only group use `prepare_ink_group_transform` and the typed ink preview/apply route.
Mixed graphite/ink group transforms are not a supported atomic group operation.
Use `retire_group_guides` only with explicit current guide IDs and reason. It
creates ordinary atomic delete actions. To recheck a group, inspect and record
the image read, then `review_semantic_group(..., inspection_id=..., evidence=...)`.
This acknowledges review of that version, not artistic PASS or a finish verdict.
Parent reviews must be current before dependent reviews. No automatic drawing
stage, inherited geometry correction, or blanket guide deletion is imposed.
