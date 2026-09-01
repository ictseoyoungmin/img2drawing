# img2drawing vNext architecture contract

Status: **CURRENT**
Updated: 2026-09-01

이 문서는 현재 닫힌 B00–B10(+B01-R1/B07-R1) 기반과 B11–B18 구현 phase가
공유해야 하는 architecture invariant를 정의한다. 새 fresh visual dogfood는 B18
freeze 이후에만 시작한다.

## 1. 현재 닫힌 core

현재 canonical vNext surface의 중심은 하나의 `DrawingSession`이다.

```text
DrawingSession
  ├─ observe
  ├─ draw / draw_many
  ├─ replace / replace_segment / soft_lift / delete
  ├─ fill_region / replace_fill_region
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
                                                     └─ replay/output
```

- `DrawingSession`과 shared history가 session/action state의 유일한 권위다.
- renderer와 inspection은 같은 read-only authored snapshot의 consumer다.
- B02+B03 `InspectionSheet`가 유일한 vNext inspection 구현이다.
- geometry/value 변화는 명시적 authored action으로 history에 남는다.
- visual acceptance와 highest-impact residual 선택은 Agent가 담당한다.

## 2. canonical lifecycle

```text
create → observe/declare → draw → inspect → choose residual → correct → inspect → repeat → finish
```

여기에는 `P1`–`P6`, `stage_start`, `advance`, `close_stage`, `reopen_stage`, downstream
invalidation이 없다. ordered drawing grammar는 authoring guidance이며 runtime cursor나
gate가 아니다.

## 3. durable invariants

- 모든 reference/mode/finish/style intent는 한 session/history/renderer/inspection/
  correction core를 공유한다.
- public vNext API는 Pn이나 stage registry에 분기하지 않는다.
- inspection은 exact evidence/state digest에 묶이고 stale evidence는 current truth로
  재사용되지 않는다.
- checkpoint는 portable/atomic하며 resume 후 history/evidence/intent/correction
  provenance 연속성을 보존한다.
- 수정 action 자체는 개선 증거가 아니다. fresh render/inspection이 필요하다.
- `ResidualRecord`는 Agent가 선택한 mismatch를 evidence와 responsible premise/action
  context에 묶는다. `CorrectionRecord`는 explicit history action과 fresh after
  inspection을 묶는다. 이 records는 score나 lifecycle state가 아니다.
- macro pose/form/composition residual이 detail/style polish보다 우선한다.
- **form before value**: tone을 제거해도 major limb/torso/clothing volume, overlap,
  prop contact가 읽혀야 한다. value primitive가 구조 부족을 대신할 수 없다.
- broad value는 `fill_region()` 같은 authored region decision으로 표현하고 generated
  hatch microstrokes를 개별 artistic decisions로 persistence하지 않는다.
- disproved value premise는 `replace_fill_region()` 같은 append-only revision으로
  correction provenance에 연결한다.

## 4. observation and measurement authority

관찰 도구는 Agent의 시각 판단을 보조하며 correspondence/geometry truth를 자동
결정하지 않는다.

- crop/grid/plumb/angle/relative-distance/profile은 질문에 답하는 read-only evidence다.
- luminance profile은 luminance 차이만 볼 수 있다. 보지 못하는 material boundary를
  geometry authority처럼 사용하지 않는다.
- `SubjectPalette`는 Agent가 이미 식별한 material patches를 기반으로 nearest-material
  evidence와 ambiguous pair를 제공한다. semantic identity를 스스로 발견하는 detector가
  아니다.
- line을 추가하기 전에 무엇과 무엇을 분리하는지 이름을 붙인다.
- 보지 못한 termination을 anatomy default로 발명하지 않는다.
- correction은 새 premise이므로 같은 관찰 질문을 다시 통과한다.

## 5. evidence budget

`EvidencePolicy`의 quick/focused/deep은 lifecycle stage가 아니라 presentation/read
budget이다.

```text
quick   → whole sheet only; no ROI/guide/grid/measurement extras
focused → exactly 1–3 prioritized ROI; no guide/grid/measurement extras
deep    → up to 3 ROI + guide/grid/measurement; escalation_reason required
```

`EvidenceTelemetry`는 inspection/read/artifact/review-turn/elapsed work만 기록하고
geometry/residual priority/artistic PASS를 결정하지 않는다.

## 6. current intent model

`DrawingIntent`, `ModeGuide`, `FinishGuide`, `StyleGuide`는 portable plain-data API다.

```text
DrawingIntent
  ├─ reference_mode: observed | imaginative | hybrid
  ├─ drawing_mode: croquis | figure_drawing | tonal_study | free_draw
  ├─ finish_intent: pose | subject | form_light | expressive
  ├─ style_profile: preset/custom identifier
  └─ provenance
```

네 축은 독립적이다. 어느 값도 lifecycle state나 phase cursor가 아니다.
`IntentChangeRecord`는 intent snapshot과 reason/history cursor를 append-only로 보존하고
intent change는 geometry를 자동 rewrite하지 않는다.

현재 B08 implementation은 readable subject를 요구하는 production path까지만 닫혔다.
B13에서 subjectless imaginative runtime과 hybrid authority semantics를 완성한다.

## 7. residual meaning by reference authority

B13 이후 하나의 correction core가 다음 의미를 공유해야 한다.

- **observed:** reference subject와 drawing의 material mismatch
- **imaginative:** declared intent/composition/shape goal과 drawing의 mismatch
- **hybrid:** preserved reference constraints와 explicit transformation intent의 mismatch

imaginative/hybrid를 위해 가짜 subject overlay나 fake measurement authority를 만들지
않는다.

## 8. mode, finish, and style

### ModeGuide

primary observations, recommended grammar, omissions, finish emphasis, completion
questions만 선언한다. required phase count, cursor, `advance`, `close`, PASS를 갖지
않는다.

B14의 target capability set은 작게 유지한다.

```text
croquis
figure_drawing
tonal_study
line_study
free_draw
```

### Finish intent

B09은 `pose | subject | form_light | expressive`를 actual authoring guidance에 연결했고
`FinishStage`나 P7를 만들지 않는다. recognition은 relational target이다.

### StyleGuide vs RenderProfile

```text
StyleGuide    = Agent가 marks를 어떻게 author할지
RenderProfile = authored marks를 renderer가 어떻게 materialize/rasterize할지
```

Style은 post-filter가 아니고 renderer가 geometry를 몰래 바꾸는 권한도 아니다.
B15에서도 one base + explicit overrides를 유지하며 inheritance graph/DSL은 금지한다.

## 9. completion

B10에서 `finish()` 의미를 portable `FinishRecord`로 강화했다.

```text
FinishRecord
  intent_digest
  drawing_state_hash
  final_inspection_id
  history_cursor
  accepted_limitations
  rationale
```

이 record는 Agent decision provenance이며 automatic artistic certificate가 아니다.
finish 이후 material mutation은 stale finish state를 만든다.

## 10. replay/output parity

B11 이후 같은 canonical history와 versioned `RenderProfile`에서 final PNG, replay
latest state, GIF final frame이 같은 output family를 재현해야 한다.

`RenderProfile`은 최소한 다음을 명시한다.

```text
renderer id/version
canvas size
material/pencil profile
paper/grain
supersample
seed domain
compositing
encoding
```

vNext timelapse는 action0부터 latest까지 end-to-end provenance를 사용하고 canonical
sampling policy(`every_n` 포함)를 명시한다.

## 11. persistence and legacy boundary

- R23 baseline `25ec4544e86fe37fc28d64575df145a1b711d63a`는 read-only historical truth다.
- B12는 legacy runtime/checkpoint compatibility를 explicit adapter/namespace로 격리한다.
- shared stroke/history/renderer capability를 `core_v2`처럼 복제하지 않는다.
- B12는 physical deletion을 하지 않는다.
- **physical R23 retirement는 B18이 아니라 full D01–D06 dogfood + R02 regression 이후
  R03에서만 수행한다.**

## 12. B09–B18 implementation / dogfood boundary

B09–B18은 product surface completion phase다.

허용:

- deterministic/synthetic fixtures
- migration/compatibility fixtures
- unit/integration/replay regressions
- already-preserved historical evidence
- direct contract/code review

금지:

- 새 unseen-subject dogfood를 slice closure gate로 사용
- cross-agent quality campaign
- answer image/subject-specific coordinate table을 generic proof로 사용
- dogfood 결과 하나에 맞춰 parallel workflow를 추가

B18 freeze 이후 D01–D06에서 처음으로 full fresh validation을 수행한다. 그때 발견한
결함은 responsible B-slice를 REOPEN해 수정한다.

## 13. architecture review trigger

다음이 생기면 작업을 중지하고 contract를 재검토한다.

```text
ModeStage / StyleStage / FinishStage
advance_mode / close_mode / mode_complete / style_complete
automatic likeness/style/artistic PASS
mode별 session/history/renderer/inspection 복제
legacy Pn normal route 재유입
history 밖 raster-only geometry mutation
style이 subject geometry truth를 덮는 renderer/post-filter
imaginative mode가 fake reference authority를 만드는 것
```

## 14. B11–B18 아직 구현할 surface

```text
B11  RenderProfile + replay/GIF parity
B12  legacy isolation
B13  subjectless/reference authority
B14  mode capability completion
B15  style authoring completion
B16  edit ergonomics
B17  package/public API/release-candidate truth
B18  system freeze for dogfood
```

구체 schema/API는 해당 active slice에서 최소 계약으로 동결한다. full visual
robustness는 B18 이후 dogfood에서 검증한다.
