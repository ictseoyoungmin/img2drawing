# img2drawing vNext architecture contract

Status: **CURRENT**
Updated: 2026-08-31 (B08 reclosed)

이 문서는 `temp/img2drawing_vnext_universal_drawing_plan.html`의 설계를 현재
B00–B08 구현과 맞춰 압축한 architecture contract다. 이미 구현된 계약과 미래
slice의 제약을 구분한다.

## 1. 현재 닫힌 core

현재 실행 가능한 canonical vNext surface는 다음이다.

```text
DrawingSession
  ├─ observe
  ├─ draw / draw_many
  ├─ replace / soft_lift / delete
  ├─ inspect
  ├─ record_residual / record_correction
  ├─ intent / intent_history / set_intent
  ├─ checkpoint / resume
  └─ finish

PoseObservation + ConstructionMark* → InitialConstruct
InitialConstruct → author_initial_construct → inspect_initial_construct
```

권위와 소비 방향:

```text
Agent observation / authored intent
              ↓
DrawingSession → one authoritative action history → StrokeIR snapshot
                                                     ├─ renderer
                                                     ├─ inspection
                                                     └─ replay (future canonicalization)
```

- `DrawingSession`과 shared history가 session/action state의 유일한 권위다.
- renderer와 inspection은 같은 read-only snapshot의 consumer다.
- B02+B03 `InspectionSheet`가 유일한 vNext inspection 구현이다.
- geometry 변화는 명시적 action으로 history에 남는다.
- visual acceptance와 highest-impact residual 선택은 Agent가 담당한다.

## 2. canonical lifecycle

```text
create → observe → draw → inspect → choose residual → correct → inspect → repeat → finish
```

여기에는 `P1`–`P6`, `stage_start`, `advance`, `close_stage`, `reopen_stage`,
downstream invalidation이 없다. ordered drawing grammar는 권장 authoring policy이며
runtime cursor나 gate가 아니다.

## 3. 보존할 불변식

- 한 session/history/renderer/inspection core를 모든 drawing intent가 공유한다.
- public vNext API는 Pn이나 stage registry에 분기하지 않는다.
- legacy stage label은 opaque compatibility provenance로만 남을 수 있다.
- inspection은 exact subject bytes, drawing artifact, stage-free state digest에 묶인다.
- checkpoint는 portable하고 atomic하며 resume 후 history/evidence 연속성을 보존한다.
- 수정 action 자체는 개선 증거가 아니다. fresh render/inspection이 필요하다.
- `ResidualRecord`는 Agent가 선택한 mismatch를 observation, before inspection digest,
  responsible premise/strokes, scope, severity, impact rationale, planned edit에
  묶는다. `CorrectionRecord`는 explicit history action과 fresh after inspection을
  묶으며 `keep`만 residual을 resolved로 만든다; `revise`는 열린 concern으로 남긴다.
- residual/correction records are correction memory, not a score, priority selector,
  lifecycle gate, or duplicate history. Stale before/after evidence and orphan action
  references are rejected on record and checkpoint resume.
- macro pose/form/composition residual이 detail/style polish보다 우선한다.
- evidence budget은 `quick` whole-sheet(추가 evidence 없음), Agent-selected 1–3 ROI만
  허용하는 `focused`, 최대 3 ROI와 guide/grid/measurement를 허용하며 reason이 필요한
  `deep`으로 제한한다. 이는 lifecycle stage가 아니며 file generation count를
  줄이는 계약이 아니라 inspection presentation/read budget 계약이다.
- `EvidenceTelemetry`는 inspection/read/artifact/review-turn/elapsed work만 세며,
  `EvidenceReadRecord.stale`로 과거 immutable sheet를 표시한다. telemetry는 geometry,
  residual priority, artistic PASS/FAIL을 결정하지 않는다.

## 4. B08 current intent model

`DrawingIntent`, `ModeGuide`, and `StyleGuide` are current portable plain-data APIs.
They are data selections and guidance records, not lifecycle APIs.
The current production `DrawingSession.create()` still requires a readable subject
image; imaginative/hybrid and free-draw values are scaffolded declarations, not a
subjectless blank-canvas runtime.

```text
DrawingIntent
  ├─ reference_mode: observed | imaginative | hybrid
  ├─ drawing_mode: croquis | figure_drawing | tonal_study | free_draw
  ├─ finish_intent: pose | subject | form_light | expressive
  ├─ style_profile: pencil_loose | graphite_academic | custom:<identifier>
  └─ provenance: optional source/reason/compatibility key
```

네 축은 독립적이다. 어느 값도 lifecycle state나 phase cursor가 아니다.
`IntentChangeRecord` stores a full intent snapshot, previous digest, reason, and the
existing action-history cursor. `DrawingSession` is the sole owner; changing intent
never rewrites geometry or creates a parallel history branch. Sessions without intent
remain resumable.

## 5. residual 의미

- **observed:** subject와 drawing의 material mismatch
- **imaginative:** 선언한 intent와 drawing의 mismatch
- **hybrid:** 보존해야 할 reference constraint와 transformation intent의 mismatch

B06은 이 차이를 구현하지 않고 먼저 observed correction loop를 닫는다. B08 이후
intent model이 들어와도 correction core 자체를 복제하지 않는다.

## 6. mode와 style

`ModeGuide`는 primary observations, recommended grammar, omissions, finish emphasis,
completion questions를 선언한다. required phase count, stage/cursor, advance/close
operation, or visual verdict를 갖지 않는다. `resolve_mode_guide()`는 one of the
small built-in data records를 반환한다.

style은 두 층으로 분리한다.

- `StyleGuide`: line behavior, construction visibility, detail/value/edge policy 등
  Agent의 authoring guidance
- `RenderProfile`: renderer, brush/material, paper, supersample, compositing,
  deterministic seed domain

style은 완성 PNG post-filter가 아니며 renderer가 geometry를 몰래 바꾸는 권한도
아니다. B08은 `pencil_loose`와 `graphite_academic` 두 base 및 one-base + explicit
field overrides만 제공한다. custom prose를 자동 구조화하거나 plugin registry를
만들지 않는다.

## 7. replay/output parity

같은 canonical history와 `RenderProfile`에서 final PNG, replay의 최종 상태, GIF
최종 frame이 같은 출력 family를 재현해야 한다. renderer/version/material/seed/
sampling policy는 provenance에 기록한다.

## 8. persistence와 legacy 경계

- R23 baseline `25ec4544e86fe37fc28d64575df145a1b711d63a`는 read-only다.
- 현재 shared core와 lazy compatibility export는 보존한다.
- B05는 normal reading route의 Pn 지침만 제거·이관한다.
- runtime/persistence namespace 격리는 B12, 물리적 R23 제거는 B18의 책임이다.
- 새 co-equal `CroquisSession`, `TonalSession`, `FreeDrawSession` tree를 만들지 않는다.

## 9. architecture review trigger

다음이 생기면 작업을 중지하고 contract를 재검토한다.

```text
ModeStage / StyleStage / FinishStage
advance_mode / close_mode / mode_complete / style_complete
automatic likeness/style/artistic PASS
mode별 session/history/renderer/inspection 복제
legacy Pn 문서의 normal reading route 재유입
history 밖의 raster-only geometry mutation
```

## 10. 아직 동결하지 않은 것

- `RenderProfile`의 구체 schema/API 이름
- custom prose parsing 전략
- charcoal/ink 등 새 renderer family
- mode별 최종 completion record shape
- R23 checkpoint의 최종 제거/마이그레이션 정책

각 항목은 해당 slice의 disposable spike 또는 dogfood로 불확실성을 해소한 뒤
동결한다.
