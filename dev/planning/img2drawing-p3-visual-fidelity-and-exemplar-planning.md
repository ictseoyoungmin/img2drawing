# img2drawing P3 시각 충실도 게이트와 exemplar 전략 논의

- 상태: 논의 초안
- 저장소 기준선: `skills/img2drawing/src/img2drawing/_version.py`의 `0.5.2.dev22 / R22` (R23 가정 없음)
- 작성 목적: sniper-girl dogfooding 피드백, 독립 검토자 의견, 사용자 exemplar 문제 제기를 다음 개발 slice의 의사결정으로 통합한다.
- 우선 대상: `P2_primary_axes → P3_primary_masses`
- 근거 실행: `drawings/croquis_run`, `dev/dogfood/croquis-sniper-girl`

주요 근거 자료:

- `drawings/croquis_run/reviews/P3_primary_masses/pass_02/review.json`
- `drawings/croquis_run/reviews/P4_structural_connections/pass_02/review.json`
- `drawings/croquis_run/reopen_archive/reopen_01/reviews/P5_clean_blockin/pass_02/review.json`
- `drawings/croquis_run/reopen_archive/reopen_01/reviews/P5_clean_blockin/pass_02/grammar_vs_drawing.png`
- `skills/img2drawing/src/img2drawing/data/exemplars/full_body_croquis/audit_manifest.json`
- `skills/img2drawing/src/img2drawing/registration/human.py`
- `skills/img2drawing/src/img2drawing/registration/compare.py`
- `skills/img2drawing/src/img2drawing/review/comparison.py`

## 결론 요약

다음 vertical slice는 새 드로잉 단계나 곡선 렌더러가 아니라 **P3 Region Closure + Blind Visual Fidelity Review + Exemplar Mandatory-Path Cleanup**이어야 한다. 기존 registration subsystem을 P2/P3 critical path에 연결하고, 부위별 silhouette/width evidence를 추가하는 것이 그 기반이다.

이번 dogfood에는 이미 stage reopen, 국소 crop review, mechanical audit가 있었다. R22 기록은 P1, P3, P5를 실제로 reopen했고 P3와 P4도 다시 구축했다. 실패 원인은 “틀린 단계를 다시 열 수 없음”이 아니라 **다시 그린 P3도 여전히 틀렸는데 `ADVANCE`한 false positive**다.

exemplar 역시 전 단계에 일괄적으로 유익하지 않았다. P2의 axes-only exemplar는 도움이 됐지만, P3의 일반 mannequin은 효과가 입증되지 않았고 P4/P5의 FAIL exemplar는 작업자가 배워야 할 긍정 문법보다 “복사하지 말아야 할 결함”을 제공했다. 따라서 FAIL exemplar를 필수 비교에서 제외하고, subject-independent한 **모듈형 grammar card + 구체적인 transfer evidence**로 전환해야 한다.

## 1. 관찰된 실패

### 1.1 P2까지는 강했고 P3에서 붕괴했다

P1/P2의 제스처와 축은 reference의 큰 동작을 비교적 잘 보존했다. 그러나 P3에서 축을 실제 occupied volume으로 번역하면서 다음 정보가 손실됐다.

- 두상과 단발 실루엣이 subject보다 크고 구형인 일반적인 anime head가 됐다.
- back three-quarter torso와 jacket depth가 납작한 세로 통처럼 단순화됐다.
- 어깨와 골반의 상대 회전이 약해졌다.
- subject에서 충분히 드러난 오른팔 윗부분이 drawing에서는 매우 얇고 뒤로 멀어진 팔처럼 축소됐다. shoulder→elbow 축만으로는 가시 면적과 폭 손실을 검출하지 못했다.
- 두 다리가 서로 다른 깊이·방향·폭 변화를 잃고 긴 평행 레일에 가까워졌다.
- 장총의 global axis는 남았지만 receiver, scope, stock의 폭 변화와 몸과의 overlap topology가 약해져 “긴 소총 기호”가 됐다.

후속 얼굴, 머리카락, 패치, holster, boot 디테일은 식별 단서를 늘렸지만 이미 틀린 head/torso/leg mass를 복구하지 못했다. hatching도 완성도와 명암 분리를 늘릴 뿐 조형 오차를 고치지 못했다.

### 1.2 판정 기록과 실제 결과가 충돌했다

`drawings/croquis_run/reviews/P3_primary_masses/pass_02/review.json`은 다음과 같이 판단했다.

- bob, jacket bulk, pelvis breadth, unequal leg envelopes, rifle mass가 표현됐다.
- 전체가 eggs, boxes, rails가 아닌 asymmetric mass system으로 읽힌다.
- 남은 우려가 없으므로 `advance`한다.

하지만 subject/final 비교에서는 큰 구형 머리, 평탄화된 몸통과 골반, rail-like legs가 뚜렷하다. 즉 현 구조는 작업자의 서술과 contract 준수 여부는 기록하지만, 그 서술이 실제 그림에 부합하는지 독립적으로 검증하지 못한다.

### 1.3 lifecycle은 작동했고 visual judgement가 실패했다

초기 dogfooding 소감 중 “P3를 다시 열어야 했는데 P5만 reopen했다”는 설명은 R22 기록과 일치하지 않는다. 독립 검토자가 확인한 실제 흐름은 다음과 같다.

1. P1 reopen
2. P5 preflight에서 P3 reopen, 이후 P3/P4/P5 무효화 및 P3/P4 재구축
3. 별도의 P5 reopen

따라서 이번 사례가 입증한 것은 reopen 기능 부족이 아니다.

> 현재 img2drawing에는 다시 열고 다시 그리는 능력은 있다. 부족한 것은 다시 그린 결과가 여전히 틀렸음을 알아채는 능력이다.

## 2. 현재 시스템에서 이미 있는 것과 빠진 것

| 영역 | 이미 있는 것 | 현재 빠진 것 |
|---|---|---|
| Stage lifecycle | reopen, downstream invalidation, checkpoint/resume | 재작업 결과의 독립적 시각 closure |
| Registration | human landmark vocabulary, 독립 provenance, landmark delta, segment similarity, ROI proposal | P2/P3 필수 경로 연결, mass·silhouette용 측정 vocabulary |
| Part envelope measurement | global silhouette extrema, skeletal landmark/segment 비교 | arm/leg/head 등 semantic region의 양쪽 contour, 다중 단면 너비, 노출량, near/far dominance 비교 |
| Local review | `prepare_local_review()`과 agent-selected crop evidence | region별 필수 증거와 closure 조건 |
| Overlay | 선택된 두 crop의 resize overlay와 absdiff | landmark alignment, contour correspondence, 구조적 거리 evidence |
| Audit | provenance와 process completion 검사, `semantic_visual_audit_required` 명시 | mechanical PASS와 별개인 visual-fidelity 판정 artifact |
| Identity | R22의 실험적 `P6_identity_finish` 기록 | 정식 stage registry와 선행 구조 gate |

특히 `registration/human.py`에는 `head_top`, `chin`, shoulders, elbows, wrists, pelvis/hips/knees/ankles, foot extent, silhouette extrema가 이미 있다. `compare_registrations()`도 독립 등록 integrity, landmark delta, segment similarity, ROI proposal을 제공하며 reference 좌표를 drawing에 그대로 복사하는 경우를 경고한다. 새 subsystem을 만들기보다 이 기능을 P2/P3 closure에 연결하는 것이 먼저다.

반면 현재 이름이 “registered overlay”인 산출물은 진짜 registration 결과가 아니다. `crop_registered_overlay()`는 agent가 지정한 두 crop을 같은 크기로 resize해 겹치며 landmark detection, alignment optimization, similarity scoring을 수행하지 않는다. 이는 관찰 보조물로는 유효하지만 fidelity gate로 취급하면 안 된다.

현재 저장소에는 **부위별 실루엣과 너비를 reference↔drawing으로 직접 측정하는 전용 도구가 없다.** 관련 기능은 다음처럼 각각 일부만 담당한다.

- `compare_registrations()`는 landmark 위치와 landmark 사이 segment가 지나가는 grid cell을 비교한다. occupied volume의 양쪽 경계나 단면 너비는 비교하지 않는다.
- `DRAWING_LANDMARKS`의 `silhouette_leftmost/rightmost`는 전신 극점이며 팔 하나의 envelope를 설명하지 못한다.
- `prepare_local_review()`과 crop overlay는 관찰자가 고른 영역을 확대·중첩하지만 측정이나 semantic alignment를 하지 않는다.
- `observation.evidence.edges()`는 raw edge map만 만들며 어느 edge가 오른팔인지 판별하지 않는다.
- `measure_contour_contact()`는 drawing IR에서 선택한 두 stroke의 최소 거리와 접선 관계를 잰다. reference와 drawing 사이의 팔 너비 비교 도구는 아니다.

따라서 이번 오른팔 실패는 현재 도구로 충분히 설명된다. shoulder와 elbow landmark가 대략 맞고 arm axis가 그럴듯하면 registration은 큰 문제를 내지 않을 수 있다. 그러나 팔의 앞/뒤 contour, upper-arm 여러 높이의 폭, subject에서 드러난 길이와 면적을 기록하지 않으므로 “축은 맞지만 너무 얇고 멀리 보이는 팔”을 놓친다.

## 3. exemplar의 실제 효용 평가

서로 다른 피사체를 사용했다는 사실만으로 exemplar가 무효인 것은 아니다. 미술 교육의 문법 예시는 subject가 달라도 taper, insertion, overlap 같은 원리를 전달할 수 있다. 이번 문제는 현재 exemplar가 **전이 가능한 문법을 고립시키지 못한 채 pose, subject, style, detail을 한 장의 전신 그림에 결합했다는 것**이다.

| 단계 | audit 상태 | dogfood에서의 실효성 판단 | 계획상 처리 |
|---|---:|---|---|
| P1 gesture | FAIL | counterbalance와 crown-origin gesture를 충분히 가르치지 못함 | 필수 비교 제외, 교체 전 warning 자료로만 사용 |
| P2 primary axes | PASS | axes-only vocabulary가 명확하고 subject 차이의 간섭이 작음. 실제 결과도 가장 안정적 | 유지, positive control로 사용 |
| P3 primary masses | PASS | organic taper라는 약한 힌트는 가능하나 back 3/4 clothed mass, 비대칭 leg depth, prop overlap을 가르치지 못함. generic egg/tube/rail anchoring 위험 | 현 상태 효용을 미입증으로 분류하고 ablation 수행 |
| P4 structural connections | FAIL | joint 위치 점은 있으나 insertion/transition grammar가 부족함 | 필수 비교 제외, 모듈형 positive/negative card로 교체 |
| P5 clean block-in | FAIL | shading, micro-fold, 얼굴·머리카락 렌더링이 contract 상한을 넘음 | 필수 비교 제외, 동일 추상도 direct-stroke exemplar로 교체 |

현재 review의 exemplar finding도 유익한 전이 증거라 보기 어렵다.

- P3: “organic taper and connection economy에만 사용했다.”
- P4: “알려진 exemplar 결함을 복사하지 않았다.”
- P5: “over-finished exemplar의 shading과 micro-texture를 복사하지 않았다.”

P4/P5 문장은 exemplar가 무엇을 가르쳤는지가 아니라 무엇을 회피했는지만 말한다. 특히 `grammar_vs_drawing.png`는 정렬되지 않은 서로 다른 전신 그림을 나란히 놓아, 어떤 문법이 어느 부위에 전이됐는지 검증하지 못한다. 이 비교판을 생성했다는 사실 자체가 review completeness로 오인될 위험도 있다.

## 4. 제안: P3 Visual Fidelity Gate

### 4.1 목표

P2에서 보존된 축이 P3의 head, torso, pelvis, legs, attached object volume으로 변환될 때 생기는 조형 붕괴를 P4 진입 전에 발견한다. runtime이 예술적 정답을 자동 판정하는 것이 아니라, evaluator가 반박하기 어려운 구조 evidence를 보고 판단하도록 한다.

subject observation 자체의 오류가 이후 gate 전체를 오염시키지 않도록 drawing 전에 view/orientation 관찰을 동결한다. 이 pre-draw observation lock은 최소한 body view, torso turn, near/far side, 각 팔의 visibility와 occlusion, prop의 앞뒤 관계를 포함한다. 이후 evaluator가 보는 frozen evidence이지 자동 진실값은 아니다.

### 4.2 P2 closure registration

subject와 drawing을 **서로 독립적으로** 등록한다.

- `head_top`, `chin`
- left/right shoulder
- `pelvis_center`, left/right hip
- left/right knee, ankle, foot extent
- 주요 prop front/rear endpoint

등록 산출물에는 source artifact hash, observation id, observer/provenance를 포함하고 `compare_registrations(..., require_independent=True)`를 사용한다. reference landmark를 drawing registration에 복사해서 통과하는 경로는 허용하지 않는다.

### 4.3 P3 mass evidence 확장

기존 skeletal landmark 외에 P3용 mass profile을 추가한다.

- head width와 좌우 contour extent
- shoulder envelope와 torso width/depth proxy
- near/far arm의 upper/mid/lower width profile, visible-length fraction, occlusion order
- pelvis breadth와 torso-to-pelvis bridge
- 각 다리의 upper/mid/lower width profile
- 다리 사이 negative-space profile
- prop의 주요 width-change point, terminal mass, body overlap point

이 정보는 곧바로 하나의 자동 점수로 축약하지 않는다. 다음과 같은 사람이 해석 가능한 discrepancy evidence를 생성한다.

- `head_right_contour`: subject envelope 밖으로 벗어난 거리
- `near_arm_upper_width`: 동일한 normalized station에서의 팔 너비 차이
- `near_arm_visible_fraction`: shoulder→elbow 구간 중 subject/drawing에서 실제 드러난 비율 차이
- `pelvis_breadth`: normalized width 차이
- `leg_R_mid_width`: normalized width 차이
- `inter_leg_negative_space`: topology 또는 width-profile 불일치
- `prop_width_transition`: 관찰된 주요 폭 변화 지점 누락

silhouette 비교에는 단순 pixel absdiff 대신 contour distance field, Chamfer distance, Hausdorff 계열의 증거를 검토한다. 사진의 texture와 명암을 선화의 오차로 오판하지 않도록 subject segmentation/contour confidence와 occlusion을 함께 기록한다.

#### Region envelope profiler 요구사항

P3 gate에는 semantic region별로 subject와 drawing을 독립 관측하는 작은 측정 도구가 필요하다. 완전 자동 anatomy detector가 아니라 evaluator가 지정한 region axis와 contour samples를 검증·비교하는 evidence utility로 시작한다.

각 region profile은 최소 다음을 기록한다.

- region id와 `near / far / unknown` side role
- 중심축의 시작·끝점과 visibility/uncertainty
- 축을 따라 정규화한 여러 station의 양쪽 contour point
- 각 station의 너비와 전체 subject height 또는 local axis length 대비 normalized width
- visible-length fraction과 선택적 visible-area proxy
- torso/prop/다른 limb에 의한 occlusion 시작·끝 및 앞뒤 순서
- subject와 drawing을 독립적으로 관찰했다는 artifact hash와 observation provenance

오른팔 사례에서는 shoulder→elbow 축의 상·중·하 station 너비와 visible-length fraction이 subject보다 크게 축소된 사실을 evidence로 내야 한다. axis landmark가 threshold 안에 있더라도 envelope discrepancy는 별도 blocker가 될 수 있어야 한다.

### 4.4 Region closure matrix

P3 전체를 하나의 `ADVANCE` boolean으로 끝내지 않고 최소 다음 영역을 독립 closure한다.

| Region | 필수 evidence | 대표 blocker |
|---|---|---|
| `head_hair` | landmark, width/contour profile, subject/drawing crop | 과대 두상, 잘못된 턱·단발 비대칭 |
| `torso_orientation` | frozen view observation, shoulder envelope, torso axis/width, crop | side/3/4 오독, 회전 평탄화, jacket depth 손실 |
| `near_arm` | shoulder-elbow-wrist, multi-station envelope, visible fraction | 충분히 드러난 팔의 과도한 축소, 잘못된 depth dominance |
| `far_arm` | shoulder-elbow-wrist, multi-station envelope, occlusion order | 가려진 팔의 과장, 잘못된 overlap/visibility |
| `pelvis` | pelvis axis/breadth, torso bridge, crop | pelvis 폭·회전 손실 |
| `leg_A` | hip-knee-ankle, multi-height width profile | rail limb, 잘못된 taper·weight path |
| `leg_B` | hip-knee-ankle, multi-height width profile | 깊이·방향 비대칭 손실 |
| `attached_object` | generic prop-topology profile, overlap/occlusion order | generic prop symbol, body overlap 오류 |

각 region은 다음 네 항목이 있어야 `closed`가 된다.

1. subject에서 새로 관찰한 finding
2. 독립 registration/contour evidence
3. drawing에서 새로 관찰한 finding
4. `closed / revise / accept-with-rationale` 결정과 그 근거

하나라도 blocker 또는 `revise`가 남으면 P3 전체는 `ADVANCE`할 수 없다. `accept-with-rationale`은 실제 occlusion이나 높은 관찰 불확실성처럼 검증 가능한 이유에만 허용하며, 설명되지 않은 큰 discrepancy를 무시하는 우회로가 되어서는 안 된다.

### 4.5 일반화된 prop topology

`attached_object` evidence를 rifle 전용 vocabulary로 만들지 않는다. 최소 다음 관계를 가진 일반 `prop_topology`로 정의한다.

- `major_axis`
- `width_change_points`
- `terminal_masses`
- `body_overlap_points`
- `visible_interruptions`
- `occlusion_order`

이 정도면 총기뿐 아니라 검, 가방, 악기, 긴 도구에도 적용할 수 있다. subject별 부품 이름은 semantic note로 남길 수 있지만 closure는 위의 일반 관계로 판정한다.

### 4.6 독립 또는 blind visual review

기존 worker가 자신의 수정 의도를 근거로 결과를 확인하는 self-confirmation을 줄여야 한다.

- 가능하면 별도 evaluator가 `visual_fidelity_review.json`을 작성한다.
- 단일 worker 환경이라면 pass memory, 이전 correction rationale, worker의 advance 주장, exemplar verdict를 숨긴 blind packet을 만든다.
- packet은 subject, frozen pre-draw observation, current drawing, 등록/region evidence, stage contract만 제공한다.
- 결과는 mechanical `review.json`과 분리한다.

예상 artifact 초안:

```text
reviews/P3_primary_masses/pass_NN/
├── review.json
├── visual_fidelity_review.json
├── observation/
│   └── pre_draw_view.json
├── registration/
│   ├── subject.json
│   ├── drawing.json
│   └── comparison.json
├── region_closure.json
└── fidelity_evidence/
    ├── head_hair.png
    ├── torso_orientation.png
    ├── near_arm.json
    ├── far_arm.json
    ├── pelvis.png
    ├── legs.png
    └── prop_topology.json
```

`review.json`은 contract/process closure를, `visual_fidelity_review.json`은 subject fidelity를 담당한다. 둘 중 하나라도 blocker이면 stage를 닫지 않는다.

## 5. exemplar 전략 개편

### 5.1 FAIL exemplar 정책

- audit 상태가 FAIL인 exemplar는 worker packet의 필수 `grammar_vs_drawing` 비교에서 제외한다.
- 교체 전까지는 결함 설명과 금지 예시로만 노출한다.
- “결함을 복사하지 않았다”는 문장을 positive transfer evidence로 인정하지 않는다.

### 5.2 전신 exemplar에서 모듈형 grammar card로 전환

한 명의 다른 피사체를 완성도 높게 그린 그림 대신, 한 카드가 한 원리만 설명하도록 한다.

- back-turned head의 두상·턱·단발 비대칭
- clothed back 3/4 torso의 occupied volume
- pelvis-to-thigh insertion
- 서로 다른 leg depth와 multi-height taper
- wrist-to-hand occlusion
- prop width transition과 body overlap

각 카드는 positive/negative pair를 포함한다. 예를 들면 organic asymmetric taper와 parallel rails를 같은 pose skeleton 위에 비교한다. pose, 체형, 착장을 바꾼 복수 예시를 두어 특정 subject를 복사하지 않고 문법만 전이되는지 확인한다.

### 5.3 구체적인 transfer mapping

exemplar를 사용했다면 review에 다음 구조를 요구한다.

```json
{
  "grammar": "asymmetric multi-height leg taper",
  "applied_region": "leg_B",
  "subject_evidence": "...",
  "drawing_evidence": "...",
  "not_copied": "pose and coordinates"
}
```

“organic taper에 사용” 같은 일반 문장은 불충분하다. subject와 drawing에서 확인되는 위치와 결과가 없으면 exemplar contribution은 `unproven`으로 기록한다.

### 5.4 ablation으로 효용 검증

동일 subject와 동일 worker protocol에서 다음 세 조건을 비교한다.

- A: subject + stage contract만 사용
- B: 현재 full-body exemplar 사용
- C: annotated modular grammar cards 사용

blind evaluator가 P3 region blocker 수, residual discrepancy 수, reopen 횟수를 비교하고 P4까지 진행한 뒤 structural error가 다시 생기거나 확대되는지도 추적한다. B가 A보다 개선되지 않으면 현 P3 exemplar는 필수 경로에서 제거한다. C는 단순 미관이 아니라 head/torso/arm/pelvis/leg/prop discrepancy를 P3에서 줄이고 그 개선이 P4에서도 유지될 때만 채택한다.

## 6. 구현 순서

### Slice 1 — P3 Region Closure + Blind Visual Fidelity Review + Exemplar Mandatory-Path Cleanup

1. pre-draw view/orientation observation lock schema와 freeze 시점을 정의한다.
2. 기존 registration API를 `DrawingRun`의 P2/P3 review 경로에 연결한다.
3. head/torso/arm/pelvis/leg용 region envelope profiler를 구현한다.
4. 일반 `prop_topology` evidence vocabulary를 구현한다.
5. `region_closure.json`과 `visual_fidelity_review.json` schema를 추가한다.
6. blind review packet과 `process PASS ∧ visual PASS` blocking rule을 구현한다.
7. FAIL exemplar를 mandatory packet에서 제외한다.
8. sniper-girl의 오른팔·두상·torso·다리·rifle 사례로 회귀 검증한다.

### Slice 2 — exemplar 정비와 실험

1. 우선 P3용 모듈형 grammar card를 제작한다.
2. transfer mapping을 review schema에 추가한다.
3. A/B/C ablation을 P4까지 수행하고 채택 여부를 기록한다.

### Slice 3 — 후속 표현력

P3 gate가 닫힌 뒤에 다음 항목을 검토한다.

- formal P6 identity stage
- Bezier/spline stroke authoring
- clean value grouping과 선 품질 개선
- 더 정교한 CV-assisted registration/segmentation

곡선과 identity는 중요하지만 선행 조형이 틀리면 오차를 더 매끈하고 구체적으로 만들 뿐이므로 이번 slice의 blocker가 아니다.

## 7. 수용 기준

다음 조건을 모두 만족해야 Slice 1을 완료로 본다.

- 현재 sniper-girl P3를 입력하면 큰 구형 head, 평탄한 torso/pelvis, 축소된 오른팔 upper envelope, parallel-rail legs 중 최소 하나 이상이 blocker로 검출되어 기존 결과가 그대로 `ADVANCE`하지 못한다.
- P2의 axis 결과는 P3 재작업 중 보존되고 registration 비교로 확인된다.
- `head_hair`, `torso_orientation`, `near_arm`, `far_arm`, `pelvis`, `leg_A`, `leg_B`, `attached_object` 각각에 subject finding, drawing finding, 독립 geometry evidence, closure 상태가 있다.
- 오른팔 shoulder→elbow axis가 대략 맞더라도 multi-station width나 visible fraction이 크게 다르면 arm region이 `closed`되지 않는다.
- visual-fidelity review는 frozen pre-draw observation을 받되 worker의 이전 rationale과 exemplar verdict를 보지 않은 evaluator 또는 blind packet으로 수행된다.
- mechanical/process PASS와 visual PASS가 별도 artifact로 존재하고 둘 모두 PASS일 때만 P3가 `ADVANCE`한다.
- reference와 drawing registration은 서로 다른 artifact 및 observation provenance를 가진다.
- FAIL exemplar가 필수 비교에 포함되지 않는다.
- 최소 한 번의 A/B/C ablation이 P4까지 추적되고, exemplar의 채택/제거 결정이 region blocker와 residual structural error evidence에 연결된다.

## 8. 비목표

이번 slice에서는 다음을 완료 조건으로 삼지 않는다.

- 자동 anatomy 판정기 또는 단일 “art quality score” 제작
- P1~P6 전체 pipeline 재작성
- photorealistic rendering이나 tonal finish
- spline 도입만으로 선 품질 문제를 해결하려는 시도
- identity detail을 이용해 잘못된 primary mass를 가리는 것

## 9. 남은 논의점

- contour distance threshold를 hard blocker로 쓸지, evaluator에게 강한 evidence로만 제공할지
- 수동 landmark 등록 비용을 어느 단계까지 허용할지
- region envelope의 기본 sampling station 수와 width discrepancy normalization 기준을 어떻게 정할지
- 사진에서 semantic contour가 모호할 때 수동 contour, segmentation 보조, uncertainty 중 무엇을 우선할지
- 단발, 옷, 소품 때문에 신체 contour가 가려질 때 visibility와 uncertainty를 어떻게 표현할지
- 동일 worker의 blind review가 실제로 self-confirmation을 충분히 줄이는지
- `accept-with-rationale`를 승인할 권한과 허용 가능한 uncertainty 기준을 어떻게 제한할지

## 제안 의사결정

1. 다음 개발 우선순위를 **P3 Region Closure + Blind Visual Fidelity Review + Exemplar Mandatory-Path Cleanup**으로 확정한다.
2. 기존 registration subsystem을 재사용하되 P3 mass/contour evidence를 확장한다.
3. pre-draw view observation을 먼저 동결하고, blind evaluator에는 그 관찰과 독립 geometry evidence만 제공한다.
4. torso orientation과 near/far arm을 독립 region으로 닫고, 부위별 다중 단면 width와 visible fraction을 측정한다.
5. attached object는 rifle 전용이 아닌 일반 `prop_topology`로 닫는다.
6. process review와 visual-fidelity review를 별도 artifact와 별도 closure로 분리한다.
7. P1/P4/P5 FAIL exemplar를 필수 비교에서 즉시 제외한다.
8. P3 exemplar는 유효하다고 가정하지 않고 P4까지 추적하는 A/B/C ablation 전까지 `unproven`으로 취급한다.
9. modular grammar card가 실제 discrepancy를 줄이고 그 개선이 P4에서도 유지된다는 증거를 얻은 뒤에만 exemplar 체계를 확대한다.

이 순서는 현재 강점인 P1/P2와 lifecycle을 보존하면서, 이번 dogfood가 드러낸 가장 큰 결함인 false-positive `ADVANCE`를 가장 작은 vertical slice에서 직접 겨냥한다.
