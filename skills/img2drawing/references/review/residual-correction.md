# Residual-driven correction

vNext의 공통 review loop는 단계 통과가 아니라 현재 drawing의 가장 큰 visual
residual을 줄이는 것이다.

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

수정 action은 개선의 증거가 아니다. 이전 inspection은 mutation 뒤 stale하며,
새 state digest에 묶인 fresh evidence가 필요하다. local crop은 Agent가 선택하고
measurement는 관계를 더 잘 보기 위한 aid일 뿐 pose·anatomy·likeness의 자동
authority가 아니다.

## Residual categories

- macro: pose, balance, mass, composition, silhouette
- relationship: overlap, negative space, joint chain, prop/body contact
- finish: identity relation, value grouping, edge hierarchy, line economy

macro residual이 남아 있으면 micro detail을 highest-impact로 선택하지 않는다.
observed 작업은 subject ↔ drawing, imaginative 작업은 declared intent ↔ drawing,
hybrid 작업은 preserved constraint + transformation intent를 비교한다.

## Evidence boundary

`InspectionSheet`와 read-only measurements는 current state와 provenance를 기록하지만
자동 PASS/FAIL을 만들지 않는다. Agent가 직접 raw render, subject beside drawing,
overlay 또는 적절한 crop을 보고 acceptance를 결정한다.

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
