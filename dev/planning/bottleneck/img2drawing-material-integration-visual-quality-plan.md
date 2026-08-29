# img2drawing material 통합 및 최종 시각 품질 개선 계획

- 방법: Bottleneck, Production WIP Limit = 1
- 작성 기준일: 2026-08-29
- 본체 기준선: 구현 전 `main`의 `0.5.2.dev22 / R22`; 완료 release `0.5.2.dev23 / R23`
- 병렬 실험 기준선: material-2의 `0.5.2.dev23 / R23_proportional_review_and_adaptive_evidence`
- 선행 계획: `dev/planning/bottleneck/img2drawing-bottleneck-implementation-plan.md`
- 근거 자료:
  - `temp/meterial-sources/img2drawing-material-1/`
  - `temp/meterial-sources/img2drawing-material-2/`
  - `dev/dogfood/croquis-sniper-girl/`
- 목적: 두 material에서 검증된 지식만 본체 계약으로 번역하고, 현재 최종 산출물의 낮은 얼굴·머리카락·의복·관절·선 표현 품질을 단계 책임에 맞게 개선한다.

```text
SYSTEM: 기존 P1→P5 architecture 유지 / 선택형 P6 경계는 S12에서 확정
ACTIVE: none
SKELETON: none
CLOSED: S01–S15
NEXT GATE: 다음 failure-regime subject를 한 번에 하나씩 fresh-worker로 검증
```

이 문서는 선행 계획의 상태 소유권을 대체하지 않는다. 구현 종료 시점에는 선행
계획의 S10과 본 문서의 S10–S15가 모두 `CLOSED`이고 각 context capsule이
작성되었다.

## 1. 결론

현재 병목은 renderer 기능이나 provenance 부족이 아니다. 본체와 material-2 모두
원본 비교, overlay, local crop, checkpoint, replay, stage review를 만들 수 있다.
문제는 그 증거를 보고도 큰 머리, 평면 몸통, 각진 관절, rail-like leg, generic
face를 `PASS`로 기록하는 **시각 closure의 false positive**다.

따라서 다음 순서를 고정한다.

1. P1/P2/P3 macro likeness를 먼저 닫는다.
2. 그 위에서 P4/P5의 hair/garment/joint/prop connection을 닫는다.
3. P5 clean block-in을 바꾸지 않고 identity가 필요한 요청에만 선택형 P6를 정의한다.
4. R23 변경은 전체 병합하지 않고 독립 patch로 검증한다.
5. 완전히 다른 subject의 packaged fresh-worker run으로 일반화를 확인한다.
6. 마지막으로 release artifact와 CI를 닫는다.

세부 묘사나 더 부드러운 선은 잘못된 mass를 고치지 못한다. 기존 sniper dogfood의
비공식 P6가 이미 이를 증명했다. 반대로 구조만 맞고 표현 단계가 없으면 현재
사용자가 요구하는 얼굴, 머리카락, 의복과 식별성에 도달할 수 없다. 이 계획은
두 문제를 순서대로 닫는다.

## 2. 검토한 증거와 판정

### 2.1 material-1: 실패한 critic과 유효한 선 운용 지식

주요 파일:

- `temp/meterial-sources/img2drawing-material-1/croquis_agent_handoff.md`
- `temp/meterial-sources/img2drawing-material-1/croquis_codex_learnings.md`
- `temp/meterial-sources/img2drawing-material-1/draw_subject_croquis.py`
- `temp/meterial-sources/img2drawing-material-1/runs/subject_croquis/critic_report.json`

확정된 실패:

- 복잡한 배경에서 자동 silhouette가 머리 일부만 검출했다.
- 수동으로 만든 거친 `subject_matte.png`가 observation aid를 넘어 critic reference가 됐다.
- critic은 원본 subject가 아니라 agent가 만든 matte와 drawing의 일치를 측정했다.
- 높은 bbox/contour/focus 수치와 `PASS`가 실제 likeness 실패를 가렸다.
- broad `charcoal_mass` band가 몸통과 다리를 brush/marker처럼 평탄화했다.
- 217개 stroke가 쌓였지만 volume과 identity는 개선되지 않았다.

본체로 번역할 지식:

- 원본 `subject_reference`는 immutable geometry authority다.
- segmentation, matte, edge, landmark, ROI proposal은 observation aid일 뿐이다.
- pressure calibration sheet를 실제 canvas/output scale로 먼저 확인한다.
- construction/form/accent 역할과 평균 weight를 구분한다.
- 한 stroke 안에서 시작→중심→끝 pressure taper를 사용한다.
- accent는 전체 contour가 아니라 중요한 약 15~25%에 선택적으로 사용한다.
- line-centric croquis에서 broad value band를 금지한다.
- value가 필요하면 form direction을 따르는 sparse pencil hatching을 사용한다.
- 마지막 pass는 blanket confirmation이 아니라 selective restatement다.

직접 가져오지 않을 것:

- `croquis-atelier`의 `scale`, `strength`, `wobble` 수치
- `charcoal_mass` tool semantics
- critic threshold와 단일 품질 점수
- `[x, y, pressure]`를 제외한 croquis-atelier 전용 API

현재 본체는 이미 `DrawingAction.pressure`, `shaped_pressure_profile()`,
construction/form/accent pencil preset과 pencil-contact renderer를 가진다. 새 renderer를
만들기보다 이 기능의 사용 계약과 visual gate를 보강한다.

### 2.2 material-2: 강한 process evidence와 약한 visual closure

주요 파일:

- `temp/meterial-sources/img2drawing-material-2/GATES.md`
- `temp/meterial-sources/img2drawing-material-2/output/subject_croquis/workflow.py`
- `temp/meterial-sources/img2drawing-material-2/output/subject_croquis/verify.py`
- `temp/meterial-sources/img2drawing-material-2/output/subject_croquis/final_subject_comparison.png`
- `temp/meterial-sources/img2drawing-material-2/output/subject_croquis/run/reviews/P5_clean_blockin/pass_01/review.json`

가져올 가치가 있는 증거:

- 원본 `subject.png`가 geometry authority로 유지된다.
- back-three-quarter view, head turn, support/counterbalance leg, rifle overlap이 observation lock에 기록된다.
- P4가 rifle을 suppressor/barrel/receiver/scope/stock/cutout/sling으로 분해한다.
- P5가 104개 construction stroke를 history-preserving delete하고 5개 gesture ghost만 남긴다.
- P5 whole-view에서 leg rail을 발견하고 `replace_segment` correction을 기록한다.
- artifact/provenance/hash/timelapse verification을 artistic score와 분리하려 한다.

그러나 직접 inspection에서 확인된 blocker:

- skull/face wedge/hair mass가 분리되지 않고 큰 원형 hair/head envelope로 읽힌다.
- 두 눈, 코, 입의 비율과 near/far 관계가 subject의 head turn을 충분히 보존하지 못한다.
- jacket이 torso와 arm volume 위에 걸린 옷보다 평면 다각형처럼 보인다.
- elbow/knee/ankle transition이 직선과 직각에 가깝다.
- P5 correction 후에도 다리의 inner/outer contour가 긴 rail로 읽힌다.
- 구조적 fold가 너무 적어 torso turn, cloth tension, compression이 사라진다.
- rifle component 이름은 늘었지만 전체 silhouette는 긴 판형 기호에 가깝다.

이 blocker가 보이는 local comparison이 존재하는데도 P5 review는 모두 `PASS`로
기록했다. 따라서 material-2는 canonical P4/P5의 원재료이지 visual acceptance의
positive reference가 아니다.

기술적 이식 위험:

- R23 runtime을 main의 `dev/tests`에 대입하면 `51 passed, 2 failed`다.
- `RegionClosureManifest v2`의 `excluded_regions`와 main schema/test가 불일치한다.
- completion manifest가 옛 checkout의 절대경로를 저장해 이동 후 검증에 실패한다.
- `accepted_residuals`와 adaptive exclusion은 현재 false-positive 환경에서 escape hatch가 될 수 있다.
- `workflow.py`는 약 83KB의 subject-specific 좌표 스크립트다.

따라서 R23 전체 복사, workflow 좌표 복사, 기존 review verdict 승계는 금지한다.

### 2.3 본체의 기존 비공식 P6 실패

주요 파일:

- `dev/dogfood/croquis-sniper-girl/02_run_record/identity_pass.json`
- `dev/dogfood/croquis-sniper-girl/02_run_record/DOGFOOD_REPORT.md`
- `dev/dogfood/croquis-sniper-girl/05_scripts/identity_full.py`
- `showcase/entries/croquis-sniper-girl-opus5-r22/croquis_final.png`

기존 run은 P5 뒤에 비공식 `P6_identity_finish`를 수행했다.

- identity strokes: 85
- confirmation strokes: 75

거의 모든 identity mark를 다시 긋는 confirmation pass는 selective restatement가
아니다. 세부 선은 늘었지만 oversized head, flat torso, angular joints, weak hair/face
separation을 복구하지 못했다. 이 기록은 P6가 필요 없다는 뜻이 아니라, **P6가
upstream correction을 대체할 수 없고 blanket darkening을 금지해야 한다**는 증거다.

## 3. 문제별 earliest responsible stage

| 시각 문제 | 가장 이른 책임 stage | 후속 stage 책임 | 금지되는 보상 |
|---|---|---|---|
| 큰 원형 머리 | P1 head direction, P3 skull/face volume | P4 hair seating, P5 silhouette | P6에서 눈·머리카락 선을 추가해 가리기 |
| hair/face 미분리 | P3 face wedge/jaw plane | P4 face opening/hair mass, P6 lock grouping | 머리 전체를 한 원으로 진하게 restate |
| 평면적인 옷 | P3 torso/pelvis/arm occupied volume | P4 anchor/hang/opening/fold structure | patch, seam, pocket만 추가 |
| 각진 관절 | P1 limb rhythm, P3 volume transition | P4 sleeve/footwear connection | P5에서 모서리만 진하게 선택 |
| rail-like legs | P2 axes, P3 asymmetric envelope | P5 final contour selection | stocking/boot detail로 시선 분산 |
| 임의적인 눈·코·입 | P1 head turn, P3 face wedge | P5 scaffold, P6 resolved feature relation | feature를 좌표 추정으로 얹기 |
| 옷주름 부재 | P4 structural fold event | P6 identity fold/restatement | broad value band 또는 micro-fold 난사 |
| 균일한 선 | stroke grammar/calibration | P6 selective accent | 전체 width/pressure 일괄 증가 |
| generic prop | P2 axis, P3 mass/topology | P4 major components, P5/P6 identity | 두 평행 rail과 작은 장식만 추가 |

## 4. 동결할 architecture contract

### 4.1 Authority

- 원본 `subject_reference`만 geometry truth다.
- matte, mask, segmentation, edge map, metric, landmark와 ROI proposal은 evidence다.
- `DrawingRun`만 lifecycle, history, checkpoint와 progression authority다.
- Agent/blind evaluator만 artistic and semantic decision authority다.
- metric 또는 runtime은 `ADVANCE`, likeness, beauty를 자동 결정하지 않는다.

### 4.2 Pipeline boundary

- 기본 pipeline은 계속 `P1→P5 clean block-in`이다.
- P1–P5는 structure와 selected line을 닫으며 finished illustration을 주장하지 않는다.
- identity/detail이 요구될 때만 선택형 P6를 사용한다.
- P6 preflight가 P1–P5 blocker를 발견하면 earliest responsible stage를 reopen한다.
- P6는 wrong structure를 유지한 채 detail로 덮는 경로가 될 수 없다.

### 4.3 Evidence and closure

- process review와 visual-fidelity review는 별도 artifact다.
- correction action은 edit provenance이며 개선 증거가 아니다.
- visual decision은 raw whole, subject beside drawing, same-coordinate overlay와 applicable high-risk crop을 사용한다.
- region finding은 `subject fact → drawing fact → mismatch → severity → action/decision` 순서로 기록한다.
- `accepted_residuals`는 현재 stage의 `owns` 책임을 위반하는 결함에 사용할 수 없다.
- excluded region은 frozen observation의 실제 부재/occlusion과 연결된 rationale이 있어야 한다.
- mechanical PASS와 visual PASS는 같은 drawing state, artifact hash, observation lock digest에 bind돼야 한다.

### 4.4 Stroke and material

- normal draw/review/replay/final/timelapse renderer owner는 기존 pencil-contact path다.
- per-point pressure는 action/history에 명시적으로 보존한다.
- renderer가 잘못된 geometry를 임의 smoothing하거나 자동 수정하지 않는다.
- construction/form/accent 구분은 role과 average weight를 모두 포함한다.
- broad graphite/value band와 blanket confirmation은 금지한다.
- calibration과 line hierarchy는 guidance/evidence이며 geometry truth가 아니다.

### 4.5 Persistence and portability

- committed manifest와 public JSON/MD에는 checkout-specific absolute path를 넣지 않는다.
- 새 schema는 checkpoint/session/review manifest round-trip과 migration test를 가진다.
- material source는 임시 조사 자료다. closure evidence로 채택할 파일은 canonical `dev/evidence/` 아래로 승격하고 source/hash를 기록한다.

## 5. 한 화면 시스템 스케치

```text
subject.png
    │ immutable geometry authority
    ▼
ObservationContract + optional assistive proposals
    │ Agent validates; proposals never become truth
    ▼
P1 gesture → P2 axes → P3 occupied volumes
    │ process PASS ∧ blind macro-fidelity PASS
    ▼
P4 real-form connections
    │ hair/garment/joint/prop region closure
    ▼
P5 clean block-in
    │ contour ownership + construction retirement + resolved scaffold
    ├─────────────── default deliverable
    ▼ when identity/detail is requested
P6 identity finish
    │ face relation + grouped hair + sparse folds + selective accent
    ▼
final visual review ∧ provenance verification
    │
    ▼
packaged fresh-worker dogfood → release closure
```

## 6. ACTIVE bottleneck card — S10 macro semantic residual closure

Status: `CLOSED`

### Objective

S01–S09 evidence infrastructure가 실제 sniper 계열 subject에서 false-positive
`ADVANCE`를 막고, P1/P2/P3의 macro structure를 independent blind review까지
동일 state/lock으로 닫는지 증명한다.

### Inputs

- 선행 S10 integration evidence와 residual gate
- material-1의 matte/critic failure
- material-2의 P3/P5 drawing과 local comparison
- 기존 sniper R22/P6 dogfood
- 원본 `subject.png`

### Execution order

1. material-1 final/critic/matte를 `metric-authority failure` negative fixture로 분류한다.
2. material-2 final/P5 local reviews를 `visual false-positive` negative fixture로 분류한다.
3. 기존 R22 P6 final/identity pass를 `detail-cannot-repair-structure`와 `blanket-restatement` fixture로 분류한다.
4. temp 경로에서 실제로 보존할 최소 evidence를 canonical `dev/evidence/`로 승격한다.
5. P1 head direction과 whole gesture를 원본에서 다시 검사한다.
6. P2 shoulder/pelvis turn, limb axes, prop axis를 다시 검사한다.
7. P3 skull/face wedge, torso/pelvis turn, arm exposure, leg envelope와 prop mass를 재구성한다.
8. P4 detail을 시작하기 전에 independent/blind macro review를 수행한다.
9. blocker가 남으면 P4/P5 polish가 아니라 P1/P2/P3를 다시 reopen한다.
10. 같은 state/lock의 mechanical and visual artifacts를 통합 report와 capsule에 기록한다.

### S10 Definition of Closed

- [x] oversized head, flat torso, thin near arm, weak pelvis turn, rail leg, generic prop 중 visual blocker가 남지 않는다.
- [x] `head_hair`, `torso_orientation`, `near_arm`, `far_arm`, `pelvis`, `leg_A`, `leg_B`, `attached_object` 각각에 fresh subject/drawing fact와 evidence가 있다.
- [x] evaluator는 worker의 이전 rationale, previous verdict와 advance claim을 보기 전에 finding을 작성한다.
- [x] P3 detail 없이 pose, occupied volume, near/far depth와 major prop mass가 읽힌다.
- [x] correction action이 개선 증거로 인용되지 않는다.
- [x] visual and mechanical record가 동일 drawing state/artifact/lock digest에 bind된다.
- [x] malformed, stale, missing, mismatched evidence test가 통과한다.
- [x] integration report, representative comparison board, smoke/test evidence가 작성된다.
- [x] `dev/planning/capsules/S10-*.md` context capsule이 작성된다.
- [x] direct inspection을 기록하고 후속 reopen 조건을 명시했다.

### S10 non-goals

- P4/P5 detail expansion
- P6 formalization
- renderer replacement 또는 spline/Bezier production 도입
- R23 전체 병합
- 자동 art-quality score
- release artifact 재생성

## 7. S11 — P4/P5 Resolved-form Fidelity

Status: `CLOSED`

S10 closure 후 material-2의 P4/P5 construction knowledge를 subject-independent grammar로
추출한다. 좌표, action ID, 기존 `PASS` verdict는 가져오지 않는다.

### Responsibilities

- P4 hair seating과 face-opening negative shape
- garment가 torso/arm/pelvis volume에 걸리는 anchor/hang/compression/opening
- elbow/knee/ankle의 organic transition과 convex/concave contour asymmetry
- subject-supported sparse structural fold event
- hand/foot/footwear connection
- general prop topology와 body contact
- P5 decisive contour, ownership handoff와 construction retirement
- P5 face/hair/garment scaffold와 line-role hierarchy

### Proposed region closure

P4:

- `head_hair_connection`
- `face_opening`
- `torso_garment_hang`
- `near_arm_joint_chain`
- `far_arm_joint_chain`
- `waist_leg_openings`
- `footwear_connection`
- `attached_object_structure`

P5:

- `face_feature_scaffold`
- `hair_silhouette_grouping`
- `garment_contour_and_folds`
- `joint_contour_continuity`
- `hands_and_footwear`
- `prop_final_topology`
- `contour_ownership`
- `construction_retirement_and_line_hierarchy`

### S11 Definition of Closed

- [x] hair outer mass, skull/face wedge와 face opening이 서로 구분된다.
- [x] hair가 하나의 closed balloon/helmet으로 읽히지 않는다.
- [x] jacket/sleeve/shorts가 underlying body와 anchor/hang/overlap 관계를 가진다.
- [x] visible bent joint가 unsupported 직각 또는 동일 각도의 parallel contour로 닫히지 않는다.
- [x] 각 applicable garment region에 subject-supported structural fold event가 있고 micro-fold나 broad band가 없다.
- [x] prop가 major width change, terminal mass와 body contact를 보존한다.
- [x] P5 retirement 후 P1 rhythm과 P3/P4 volume이 손실되지 않는다.
- [x] process PASS와 P4/P5 visual PASS가 별도 artifact로 존재한다.
- [x] material-2 workflow를 호출하거나 좌표를 import하지 않는 재현 가능한 canonical run이 있다.
- [x] independent comparison이 기존 material-2 final보다 head/hair, garment, joint, legs에서 우세한 개선 패스를 기록한다.
- [x] schema/tests/replay/resume/reference build와 context capsule이 작성된다.

## 8. S12 — Optional P6 Identity Finish + Line Expression

Status: `CLOSED`

기본 P1→P5 pipeline은 유지한다. 사용자가 특정 인물/캐릭터의 얼굴, 머리카락,
착장과 장비 식별성을 요구할 때만 선택형 P6를 실행한다. 기존 dogfood의
`P6_identity_finish` 이름과 evidence를 재사용하되 비공식 post-finish mutation을
두 번째 production path로 유지하지 않는다.

### P6 owns

- head turn을 보존한 eye/nose/mouth proportional relationship
- brow/eye/nose/mouth/chin interval과 near/far feature asymmetry
- hair parting, grouped locks, representative tips와 face occlusion
- identity-defining garment break, strap, pocket, patch와 sparse fold
- hand/foot/boot와 prop의 제한된 identifying topology
- construction/form/accent hierarchy와 selective restatement
- 필요한 경우 sparse form-following pencil hatching

### P6 forbids

- P1–P5 blocker를 detail로 숨기기
- 원본 pixel edge tracing
- 전체 contour accent
- 모든 identity mark의 confirmation duplicate
- broad charcoal/graphite band
- unlimited micro hair strand, wrinkle, stitching, screw와 texture
- feature relation을 확인하기 전 임의 눈·코·입 배치

### Calibration artifact

실제 output canvas에서 다음을 렌더한다.

- construction/form/accent 각 5개 pressure sample
- straight, C-curve, S-curve, joint turn과 short facial mark
- start/peak/end가 다른 per-point taper
- actual-size와 50% 축소 비교

Agent가 선택한 profile과 이유를 run metadata에 기록한다. material-1의 절대 수치를
복사하지 않고 본체의 `grade / pressure / width / opacity`로 번역한다.

### S12 Definition of Closed

- [x] P6가 optional registry/profile로 명시되고 default P1→P5 run은 깨지지 않는다.
- [x] P6 preflight가 upstream blocker를 발견하면 earliest responsible stage를 reopen한다.
- [x] face relation observation이 eye-line/head turn/jaw와 features를 함께 검증한다.
- [x] hair는 outer mass와 grouped internal locks가 구분되고 모든 strand를 그리지 않는다.
- [x] garment detail은 anchor/tension/compression을 설명하는 소수의 mark로 제한된다.
- [x] per-point pressure와 taper가 action/history/replay에 보존된다.
- [x] accent/restatement가 전체 linework를 지배하지 않는다.
- [x] 기존 85+75 identity/confirmation 방식보다 적은 중복을 사용한다.
- [x] P5 block-in과 P6 final을 별도 deliverable/evidence로 보존한다.
- [x] visual gate, tests, example, limitation 문서와 context capsule이 작성된다.

## 9. S13 — R23 Selective Integration and Compatibility Hardening

Status: `CLOSED`

R23 전체 tree나 wheel을 병합하지 않는다. 아래 기능을 각각 독립 patch로 평가한다.

1. fast non-authoritative preview
2. assistive ROI proposal + Agent validation provenance
3. subject-adaptive region exclusion
4. `accepted_residuals`
5. proportional review wording/P1 auxiliary flow cue

### Integration rules

- 기존 canonical module과 `DrawingRun` owner를 재사용한다.
- `foo_v2`, alternate runtime, parallel renderer를 만들지 않는다.
- 각 schema/API change에는 migration과 round-trip test가 있어야 한다.
- excluded region은 frozen observation rationale 없이는 생성할 수 없다.
- accepted residual은 현재 stage의 `owns` 또는 material mismatch를 무시할 수 없다.
- assistive ROI는 proposal provenance를 남기며 semantic authority가 아니다.
- preview는 review/final/replay/timelapse evidence로 제출할 수 없다.
- manifest path는 checkout-relative 또는 artifact-root-relative다.

### S13 Definition of Closed

- [x] 현재 확인된 R23의 2개 test failure가 migration tests로 해결된다.
- [x] main 전체 pytest가 통과한다.
- [x] schema validation과 legacy/current checkpoint round-trip이 통과한다.
- [x] moved-checkout manifest verification이 통과한다.
- [x] 기존 R22/main behavior가 호환 범위에서 유지된다.
- [x] 각 기능의 사용/비사용 결정과 limitation이 기록된다.
- [x] 임시 R23 wheel/build tree가 canonical source가 되지 않는다.
- [x] minimal CI가 test/schema/manifest consistency를 자동 검증한다.
- [x] context capsule이 작성된다.

## 10. S14 — Packaged Fresh-worker Generalization

Status: `CLOSED`

다른 subject에서 재현되지 않으면 material 추출은 완료가 아니다. 첫 일반화 run은
sniper와 failure regime이 다른 정면 또는 3/4, prop 없는 인물로 시작한다.

### Fresh-worker constraints

- worker 입력은 packaged release candidate, 새 subject와 user goal뿐이다.
- material 문서, sniper scripts, 좌표, action ID, correction history를 전달하지 않는다.
- calibration부터 fresh하게 수행한다.
- P1→P5와 요청 시 P6를 autonomous하게 완료한다.
- mechanical verifier는 files, hashes, replay, stage closure와 provenance만 검사한다.
- visual closure는 independent worker 또는 blind packet이 담당한다.

### S14 Definition of Closed

- [x] subject hash와 package identity가 기록된다.
- [x] prohibited development coordinates/action IDs가 run에 나타나지 않는다.
- [x] head/hair, torso/garment, joint, legs, face와 line hierarchy가 새 subject에서 독립 리뷰된다.
- [x] raw whole와 subject comparison evidence가 있다.
- [x] reopen 조건과 earliest responsible stage가 report에 기록된다.
- [x] mechanical PASS가 artistic PASS처럼 보고되지 않는다.
- [x] 한 subject가 닫힌 뒤에만 다음 failure regime subject를 시작한다.
- [x] fresh-worker report와 context capsule이 작성된다.

후속 subject queue는 한 번에 하나만 활성화한다.

1. 정면/3⁄4, prop 없는 인물
2. 강한 동세와 limb occlusion
3. non-human 또는 stylized character
4. 기존과 다른 large attached object

## 11. S15 — Release and CI Closure

Status: `CLOSED`

S10–S14가 닫힌 current source를 하나의 release identity로 패키징한다.

### S15 Definition of Closed

- [x] `_version.py`, README, changelog, package contents와 release manifest가 일치한다.
- [x] skill ZIP, wheel, tree, report와 SHA-256이 current revision으로 생성된다.
- [x] clean install/import와 packaged fresh-worker smoke가 통과한다.
- [x] CI가 pytest, schema, current release validator, package-boundary와 manifest portability를 검사한다.
- [x] image quality를 자동 숫자 하나로 판정하지 않는다.
- [x] stale R21/R22 canonical distributable reference가 canonical release가 아니다.
- [x] release evidence와 final context capsule이 작성된다.

## 12. 공통 hardening gate

모든 slice는 다음을 만족해야 닫을 수 있다.

- correctness와 malformed/stale/empty evidence
- real `DrawingRun` integration
- checkpoint save/resume/replay round-trip
- schema and digest binding
- relative/public path portability
- representative visual board와 independent review
- no duplicate production owner
- superseded path retirement 또는 보존 근거
- tests/smoke와 performance/size budget
- usage/limitation documentation
- resolvable evidence path를 가진 context capsule

테스트와 체크리스트를 모두 통과해도 direct inspection에서 target quality보다
낮으면 slice는 닫지 않는다.

## 13. 금지되는 구현 패턴

- material-2 `workflow.py`를 canonical P4/P5 implementation으로 복사
- R23 tree 또는 wheel을 source 위에 덮어쓰기
- 잘못된 P3 위에 P6를 먼저 확장
- critic/mask/metric을 likeness authority로 사용
- 새 자동 art-quality score로 manual visual review 대체
- renderer가 author geometry를 자동 smoothing하도록 변경
- 전체 line width/pressure 일괄 증가
- blanket confirmation/restatement
- old/new/final/v2 parallel production path 유지
- `run.py` line count만을 이유로 unrelated refactor
- 여러 subject dogfood를 동시에 production quality로 진행

## 14. Context capsule 규칙

각 slice가 `CLOSED`될 때 `dev/planning/capsules/` 아래에 capsule을 추가한다.

포함:

- slice identity와 responsibility
- public API/output
- authoritative input/output와 state owner
- invariants와 budgets
- evidence/test/demo path
- known limitation
- integration notes
- reopen conditions

제외:

- 전체 실행 chronology
- raw log 복사
- 이미 주소가 있는 대형 checkpoint 내용
- 폐기된 대안의 장황한 서술

## 15. 진행 상태 갱신 규칙

1. 현재는 S10만 `ACTIVE`다.
2. S10의 모든 gate와 direct inspection이 닫히면 capsule을 작성한다.
3. 선행 `img2drawing-bottleneck-implementation-plan.md`의 S10 상태도 같은 commit에서 갱신한다.
4. 그 다음 S11 하나만 `ACTIVE`로 전환한다.
5. CLOSED slice를 수정할 때는 reason, triggering evidence, affected contract, migration risk와 재closure gate를 가진 reopen record를 작성한다.
6. release/version bump는 시각 및 runtime contract가 닫힌 뒤 수행한다.
