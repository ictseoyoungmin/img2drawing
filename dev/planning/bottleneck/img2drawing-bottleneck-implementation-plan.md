# img2drawing P3 fidelity bottleneck 구현 계획

- 방법: Bottleneck, Production WIP Limit = 1
- 저장소 기준선: `0.5.2.dev22 / R22`
- 상위 논의: `dev/planning/img2drawing-p3-visual-fidelity-and-exemplar-planning.md`
- 계획 상태 소유자: 이 문서
- 범위: P3 Region Closure + Blind Visual Fidelity Review + Exemplar Mandatory-Path Cleanup

```text
SYSTEM: sketched / cross-slice contract frozen
ACTIVE: S05 Torso Orientation Closure (구현 중)
SKELETON: S06 Pelvis and Legs Closure부터 S09 Exemplar Ablation까지
CLOSED: S01 Pre-draw Observation Lock; S02 Region Envelope Evidence; S03 Blind Visual Fidelity Review + P3 dual gate; S04 Exemplar Mandatory-Path Cleanup
NEXT GATE: S05 orientation evidence, arm exposure fixture, provenance/stale test
```

이 계획에서 `ACTIVE`는 구현 우선권을 뜻한다. S01이 Definition of Closed를 모두 통과하고 context capsule을 만들기 전에는 S02 이하를 production quality로 구현하지 않는다.

## 1. 목표와 현재 병목

최종 목표는 P3가 “StageContract상 허용된 mass”인지만 확인하지 않고, subject의 view, 부위별 occupied volume, visibility, silhouette topology를 실제로 보존했는지 독립적으로 닫는 것이다.

현재 false-positive `ADVANCE`는 다음 세 층이 모두 약하기 때문에 발생한다.

1. `ObservationContract`가 public type으로 존재하지만 `DrawingRun` lifecycle과 checkpoint에 연결되지 않아 pre-draw 관찰이 authoritative state가 아니다.
2. registration은 landmark와 axis 중심이며 arm/head/leg의 양쪽 contour와 다중 단면 너비를 비교하지 않는다.
3. `StageReviewRecord` 하나가 process finding과 subject-fidelity 주장을 함께 담고 즉시 stage를 advance한다.

이를 한 번에 모두 얕게 구현하지 않는다. 관찰 state → region geometry evidence → blind visual review/barrier 순서로 하나씩 닫는다.

## 2. 현재 저장소 조사 결과

### 재사용할 canonical path

| 책임 | 현재 owner | 계획 |
|---|---|---|
| Run lifecycle, checkpoint, stage progression | `src/img2drawing/run.py::DrawingRun` | 그대로 canonical owner로 유지 |
| Semantic subject observation | `observation/contract.py::ObservationContract` | 폐기하지 않고 frozen lifecycle을 추가 |
| Point/axis registration | `registration/model.py`, `human.py`, `compare.py` | region geometry의 기반으로 재사용 |
| Process review | `review/record.py::StageReviewRecord` | process review로 역할을 좁혀 유지 |
| Review preparation/worker packet | `review/reference_review.py`, `worker_protocol.py` | blind packet 경로를 기존 준비 흐름에 연결 |
| Reopen/invalidation | `DrawingRun.reopen_stage()` | observation correction과 visual reopen에 재사용 |
| Runtime persistence | `DrawingRun._checkpoint_payload()` / `resume()` | 새 authoritative records를 포함하도록 schema migration |

### 확인된 공백

- `ObservationContract`는 runtime에서 생성·동결·저장·resume되지 않는다.
- `schemas/registration.schema.json`은 현재 generic object 수준이라 실제 registration contract를 검증하지 못한다.
- 부위별 silhouette/width profiler가 없다.
- `visual_fidelity_review.json`과 `region_closure.json` model/schema가 없다.
- P3 `advance`는 별도 visual PASS를 요구하지 않는다.
- project-local pytest suite가 없고 benchmark smoke만 있다.
- top-level exemplar와 packaged exemplar가 동일 내용으로 중복되어 있다. 현재 hash는 같지만 canonical authoring owner와 sync check가 명시되지 않았다.

### 건드리지 않을 인접 영역

- renderer와 StrokeIR authoring
- P6 identity formalization
- spline/Bezier
- timelapse
- 전체 stage registry 재설계
- unrelated legacy renderer compatibility

## 3. 한 화면 시스템 스케치

```text
subject reference
    │
    ▼
ObservationContract ──lock──> FrozenObservationRecord
    │                            │ digest + subject hash
    │                            ▼
    └──────────────────────> DrawingRun checkpoint/session
                                  │
                                  ▼
                         P1 → P2 → P3 drawing
                                  │
                                  ▼
                         prepare_stage_review()
                                  │
                ┌─────────────────┴──────────────────┐
                ▼                                    ▼
       process evidence                    registration / region evidence
       StageContract scope                 subject↔drawing independent bind
                │                                    │
                │                                    ▼
                │                           blind fidelity packet
                │                                    │
                ▼                                    ▼
       StageReviewRecord                 VisualFidelityReviewRecord
                │                                    │
                └─────────────────┬──────────────────┘
                                  ▼
                       process PASS ∧ visual PASS
                                  │
                                  ▼
                         StageProgress.advance(P3)
```

Grammar exemplar는 geometry authority가 아니다. audit PASS인 경우에만 representation grammar 보조 입력이며, audit FAIL이면 mandatory comparison에서 제외하고 negative/reference warning으로만 남긴다.

## 4. 동결할 cross-slice architecture contract

이 항목은 private helper가 아니라 이후 slice를 다시 만들지 않게 하는 경계 계약이다.

### 4.1 State ownership

- `DrawingRun`만 run lifecycle, stage progress, checkpoint의 authoritative owner다.
- `ObservationContract`는 subject에 대한 agent-authored semantic content다.
- `FrozenObservationRecord`는 observation content, subject artifact hash, observation digest, lock/reopen provenance의 authoritative owner다.
- `RegionGeometryComparison`은 수치·기하 evidence만 소유하며 artistic PASS를 결정하지 않는다.
- `RegionClosureManifest`는 region별 finding, evidence reference, `closed/revise/accept-with-rationale`, blocker를 소유한다.
- `VisualFidelityReviewRecord`는 manifest digest와 전체 visual decision을 소유한다.
- `StageReviewRecord`는 StageContract/process closure를 소유한다. visual finding의 authoritative owner가 아니다.
- 같은 사실을 checkpoint, review, manifest에 값으로 복제하지 않고 digest/reference로 연결한다.

### 4.2 Frozen lifecycle

새 run의 기본 흐름은 다음으로 고정한다.

```text
create
→ observe subject
→ lock_observation
→ stage_start/draw
→ prepare_stage_review
→ prepare blind visual packet
→ submit_visual_fidelity_review
→ submit_stage_review
→ conjunction gate
→ advance or revise/reopen
```

- 최초 drawing action이나 P1 `stage_start` 전에 observation lock이 있어야 한다.
- lock 이후 content는 in-place mutation할 수 없다.
- drawing 시작 전 correction도 명시적인 replacement record를 남긴다.
- drawing 시작 후 observation correction은 `reopen_stage("P1_gesture")`와 동일한 downstream invalidation을 요구한다.
- P3의 `submit_stage_review(decision="advance")`는 같은 drawing artifact에 bind된 visual PASS가 없으면 fail-closed한다.
- P1/P2/P4/P5의 progression semantics는 해당 stage에 visual gate가 정식 도입되기 전까지 현재 동작을 유지한다.

### 4.3 Coordinate and measurement conventions

- landmark와 contour point의 저장 좌표는 source canvas normalized `[0,1]`이다.
- 거리 계산은 normalized `u/v`를 그대로 Euclidean distance로 섞지 않고 source pixel space에서 계산한다.
- cross-region 크기 비교는 subject bounds height로, limb 단면은 local axis length로 정규화한 값을 함께 저장한다.
- region axis station은 `[0,1]`의 `t`로 표현한다.
- reference와 drawing observation은 서로 다른 artifact hash와 observation id를 가진다.
- reference coordinate를 drawing record로 복사한 provenance는 validation error 또는 명시적 integrity warning이 된다.

### 4.4 P3 required regions and decisions

P3 required region set은 다음으로 동결한다.

```text
head_hair
torso_orientation
near_arm
far_arm
pelvis
leg_A
leg_B
attached_object
```

각 region은 다음을 반드시 가진다.

1. fresh subject finding
2. independent geometry evidence reference
3. fresh drawing finding
4. `closed / revise / accept-with-rationale`
5. blocker 목록

필수 region이 누락되거나 하나라도 blocker/`revise`이면 visual decision은 PASS일 수 없다. `accept-with-rationale`는 observation에 기록된 occlusion/uncertainty와 연결될 때만 허용한다.

### 4.5 Blind review boundary

blind evaluator 입력:

- subject
- frozen pre-draw observation
- StageContract
- current drawing
- registration/region geometry evidence

blind evaluator에서 숨길 정보:

- 이전 worker correction rationale
- pass memory
- worker의 `ADVANCE` 주장
- 이전 visual verdict
- exemplar audit verdict와 “복사하지 않았다” 주장

evaluator 실행 주체는 별도 agent, 별도 process, 동일 worker의 fresh turn 중 하나일 수 있다. transport는 동결하지 않으며 packet content와 provenance만 동결한다.

### 4.6 Artifact and schema contract

계획된 authoritative artifacts:

```text
output/
├── observation/
│   ├── pre_draw_observation.json
│   └── observation_reopens.json
├── reviews/P3_primary_masses/pass_NN/
│   ├── review.json
│   ├── visual_fidelity_review.json
│   ├── region_closure.json
│   ├── blind_visual_packet.json
│   ├── registration/
│   └── fidelity_evidence/
└── session/checkpoint.json
```

계획된 schemas:

- `observation_lock.schema.json`
- `observation_reopen.schema.json`
- `region_envelope.schema.json`
- 실제 model을 검증하는 `registration.schema.json`
- `region_closure.schema.json`
- `visual_fidelity_review.schema.json`

모든 review/evidence record는 drawing state hash, rendered artifact hash, history cursor, observation lock digest에 bind한다.

### 4.7 Error, versioning, and dependency rules

- missing/stale/malformed evidence는 warning 후 통과가 아니라 명시적 error 또는 `revise`다.
- numeric discrepancy는 review hint이며 자동 artistic score가 아니다.
- checkpoint/review manifest schema는 새 필드를 조용히 v1에 끼워 넣지 않고 version을 올린다.
- legacy checkpoint는 읽을 수 있어야 하지만 observation lock 없는 진행 중 run을 새 gate에 자동 승격하지 않는다. 계속 작업하려면 명시적 P1 reopen과 observation lock이 필요하다.
- S01/S02에는 새 CV/network dependency를 추가하지 않는다. Pillow/numpy와 agent-authored observations만 사용한다.
- performance budget은 이미지 inference가 아니라 JSON validation과 선형 station comparison을 기준으로 잡는다.

## 5. 후보 slice 우선순위

점수는 방향성 비교이며 dependency override가 우선한다.

| Slice 후보 | Impact | Uncertainty | Reusability | Score | 선택 판단 |
|---|---:|---:|---:|---:|---|
| Pre-draw Observation Lock | 5 | 4 | 5 | 100 | **ACTIVE** — 모든 near/far·visibility evidence의 의미와 provenance를 선행 고정 |
| Region Envelope Evidence: near arm | 5 | 5 | 5 | 125 | 점수는 최고지만 observation lifecycle에 의존하므로 S02 |
| Blind Visual Review + P3 dual gate | 5 | 4 | 5 | 100 | observation/evidence contract에 의존하므로 S03 |
| FAIL exemplar mandatory cleanup | 4 | 2 | 4 | 32 | 중요하지만 core fidelity 판단보다 불확실성이 낮아 S04 |
| Torso orientation evidence | 5 | 4 | 4 | 80 | S05 |
| Pelvis/legs evidence | 5 | 4 | 4 | 80 | S06 |
| Head/hair evidence | 5 | 4 | 4 | 80 | S07 |
| Generic prop topology | 4 | 4 | 5 | 80 | S08 |
| Modular cards + A/B/C/P4 tracking | 4 | 4 | 5 | 80 | 평가 gate가 닫힌 뒤 S09 |

## 6. ACTIVE bottleneck card — S01 Pre-draw Observation Lock

Status: `CLOSED` (implementation, verification, and capsule complete)

### Responsibility

기존 `ObservationContract`를 subject hash와 함께 한 번 동결하고, `DrawingRun`의 create/start/draw/checkpoint/resume/reopen lifecycle 전체에서 동일한 authoritative observation을 보장한다.

### Why this slice now

- view, near/far side, arm visibility가 틀리면 이후 region measurement와 blind evaluator 모두 일관되게 잘못될 수 있다.
- 현재 type은 있지만 runtime 연결이 없어 새 subsystem을 만들 필요 없이 기존 자산을 닫을 수 있다.
- 모든 후속 region/evaluator가 observation digest를 참조하므로 hard dependency다.

### Planned public surface

```python
record = run.lock_observation(observation)
record = run.observation_lock
reopen = run.reopen_observation(reason=..., replacement=...)
```

정확한 private helper와 파일 내부 배치는 동결하지 않는다. public behavior와 serialized schema만 동결한다.

### Inputs

- `ObservationContract`
- subject reference SHA-256
- typed view/orientation fields
- evidence refs와 uncertainty

최소 view fields:

- body view와 torso turn
- near/far side role
- left/right arm visibility와 occlusion
- major prop의 body overlap order
- ambiguity/uncertainty

### Outputs

- `FrozenObservationRecord`
- `observation/pre_draw_observation.json`
- checkpoint에 저장된 observation digest/reference
- blind packet용 rationale-free projection
- observation correction/reopen provenance

### Explicit non-goals

- arm width measurement
- contour extraction/segmentation
- region closure decision
- visual evaluator orchestration
- exemplar policy 변경
- P3 gate 활성화

### Definition of Closed

- [x] `ObservationContract`를 대체하는 parallel type을 만들지 않고 frozen lifecycle wrapper로 재사용한다.
- [x] lock은 subject artifact hash, observation id, schema version, digest를 검증한다.
- [x] P1 `stage_start`/최초 draw 전에 lock이 없으면 새 run은 fail-closed한다.
- [x] lock content는 외부 dict mutation이나 resume 과정에서 바뀌지 않는다.
- [x] drawing 시작 전 replacement도 audit record를 남긴다.
- [x] drawing 시작 후 replacement는 P1부터 drawing/review evidence를 rewind/invalidate한다.
- [x] checkpoint 저장·resume 후 observation digest와 content가 동일하다.
- [x] legacy checkpoint migration 동작과 제한이 명시되고 테스트된다.
- [x] malformed view role, 누락 visibility, subject hash mismatch, duplicate lock, stale replacement를 테스트한다.
- [x] 기존 subject-only benchmark가 observation lock을 사용하는 새 public path로 smoke 통과한다.
- [x] `skills/img2drawing/tests/test_observation_lock.py`에 unit/integration tests가 존재한다.
- [x] observation JSON은 일반 full-body case에서 64 KiB 이하이며 network/CV inference를 수행하지 않는다.
- [x] `SKILL.md`, observation reference, schema에 사용법과 reopen 조건이 기록된다.
- [x] 동일 책임의 `observation_v2/new/final` 경로가 없다.
- [x] S01 closure evidence와 context capsule이 작성된다.

### Evidence locations on closure

```text
skills/img2drawing/tests/test_observation_lock.py
skills/img2drawing/benchmarks/stage_reconstruction/full_body_croquis_subject_only/run_smoke.py
dev/evidence/p3-fidelity/S01-observation-lock/
dev/planning/capsules/S01-pre-draw-observation-lock.md
```

### Next gate

S01의 `FrozenObservationRecord` schema, replacement/invalidation semantics, legacy checkpoint migration은 closure evidence로 고정되었다. 다음 production slice는 이 capsule을 입력으로 삼는 S02 Region Envelope Evidence이며, 그 전까지 S03 이하의 production code는 활성화하지 않는다.

## 7. 후속 SKELETON queue

각 slice는 앞 slice가 `CLOSED`된 뒤에만 `ACTIVE`가 된다. 아래 순서는 현재 계약 기준이며, architecture-invalidating evidence가 생기면 명시적 reorder/reopen 기록을 남긴다.

### S02 — Region Envelope Evidence: near-arm vertical slice

Status: `CLOSED` (implementation, verification, fixture, and capsule complete)

책임:

- generic `RegionEnvelopeObservation`과 `RegionGeometryComparison`을 정의한다.
- agent가 subject/drawing에서 독립 선택한 axis, station contour pair, visible fraction, occlusion을 비교한다.
- sniper-girl의 얇아진 오른팔을 첫 production fixture로 닫는다.

핵심 closure:

- shoulder→elbow axis가 유사해도 upper/mid/lower width와 visible fraction 차이가 evidence로 발생한다.
- geometry utility는 `PASS/FAIL`을 만들지 않는다.
- reference/drawing artifact provenance clone과 stale drawing을 거부한다.
- unit fixture와 dogfood visual board가 있다.
- 최대 16 stations/region의 comparison은 선형이며 100 ms budget 안에서 동작한다.

### S02 public surface and Definition of Closed

```python
station = EnvelopeStation(t=0.5, contour_a=(...), contour_b=(...))
profile = RegionEnvelopeObservation(..., stations=(...))
comparison = compare_region_envelopes(
    reference_profile,
    drawing_profile,
    current_drawing_state_sha256=current_state,
)
```

- [x] normalized axis와 2~16개의 strictly increasing station contour pair를 검증한다.
- [x] near/far/unknown side, visible fraction, occlusion, uncertainty를 보존한다.
- [x] local-axis 및 선택적 subject-height 기준 width evidence와 visible-fraction drift를 산출한다.
- [x] reference/drawing observation id, artifact hash, frozen observation digest를 독립적으로 검증한다.
- [x] 현재 drawing-state digest가 stale하면 비교를 거부한다.
- [x] 비교 결과는 evidence-only authority를 유지하고 artistic `PASS/FAIL`을 만들지 않는다.
- [x] near-arm upper/mid/lower fixture가 얇아진 drawing을 수치로 드러낸다.
- [x] schema, unit/integration test, dogfood visual board와 context capsule이 작성된다.
- [x] 16 station comparison이 100 ms budget 안에서 동작하고 S01 lock digest를 소비한다.

Evidence locations:

```text
skills/img2drawing/tests/test_region_envelope.py
skills/img2drawing/schemas/region_envelope.schema.json
dev/evidence/p3-fidelity/S02-region-envelope/
dev/planning/capsules/S02-region-envelope-evidence.md
```

활성화 전 disposable spike:

- 수동 paired contour sampling과 단순 edge-assisted sampling 두 방식을 임시 경로에서 비교한다.
- semantic contour 오검출이 잦으면 수동 sampling을 production contract로 선택하고 spike를 삭제한다.

### S03 — Blind Visual Fidelity Review + P3 dual gate

Status: `CLOSED` (implementation, verification, and capsule complete)

책임:

- `RegionClosureManifest`, `VisualFidelityReviewRecord`, blind packet을 구현한다.
- P3에 `process PASS ∧ visual PASS` barrier를 연결한다.
- 여덟 required region을 모두 명시적으로 닫는다.

핵심 closure:

- blind packet에 frozen observation은 있고 worker rationale/exemplar verdict는 없다.
- visual review와 process review는 같은 drawing/observation digest에 bind된다.
- 누락 region, blocker, stale evidence, `revise`가 하나라도 있으면 `ADVANCE`가 불가능하다.
- `accept-with-rationale`는 uncertainty/occlusion evidence 없이는 validation error다.
- S05~S08 전에는 나머지 region도 독립 관측한 registration/local contour evidence를 반드시 제출한다. 후속 slice는 이 수동 evidence를 없애는 것이 아니라 더 강한 전용 측정으로 harden한다.
- 기존 sniper-girl P3는 독립 review에서 그대로 advance하지 못한다.
- non-P3 stage의 기존 progression을 깨지 않는다.

### S03 public surface and Definition of Closed

```python
manifest = run.submit_region_closure_manifest(region_manifest)
visual = run.submit_visual_fidelity_review(
    evaluator_id="independent-evaluator",
    findings=(...),
    decision="advance",
    rationale="...",
)
run.submit_stage_review(..., decision="advance", advance_rationale="...")
```

- [x] blind packet에 frozen observation, stage contract, current drawing, region refs만 남고 worker rationale/exemplar verdict는 노출되지 않는다.
- [x] eight required region에 subject finding, drawing finding, independent evidence ref, closure decision이 모두 있다.
- [x] blocker, `revise`, 누락 region, stale state/artifact, lock mismatch가 있으면 visual advance와 P3 advance가 모두 거부된다.
- [x] `accept-with-rationale`는 uncertainty/occlusion 근거 없이는 생성되지 않는다.
- [x] mechanical/process review와 visual review가 동일한 drawing/observation digest에 bind된다.
- [x] checkpoint/resume와 review manifest에 visual records가 보존된다.
- [x] P3 dual gate가 통합 테스트되고 non-P3 stage progression은 유지된다.
- [x] S03 closure evidence와 context capsule이 작성된다.

Evidence locations:

```text
skills/img2drawing/tests/test_fidelity.py
skills/img2drawing/schemas/region_closure.schema.json
skills/img2drawing/schemas/visual_fidelity_review.schema.json
skills/img2drawing/schemas/blind_visual_packet.schema.json
dev/evidence/p3-fidelity/S03-blind-visual-fidelity/
dev/planning/capsules/S03-blind-visual-fidelity.md
```

### S04 — Exemplar mandatory-path cleanup

Status: `CLOSED` (implementation, verification, and capsule complete)

책임:

- P1/P4/P5 FAIL exemplar를 mandatory `grammar_vs_drawing` path에서 제외한다.
- FAIL exemplar는 negative/reference warning으로만 제공한다.
- top-level exemplar를 authoring owner로 정하고 packaged copy는 derived artifact로 hash 검증한다.

핵심 closure:

- FAIL exemplar가 없어도 worker packet 생성과 subject-first review가 정상 동작한다.
- P2 PASS exemplar는 positive control로 유지된다.
- P3는 `unproven` 상태를 worker packet과 audit에 표현한다.
- 두 exemplar tree의 drift를 CI/smoke가 검출한다.

### S04 Definition of Closed

- [x] FAIL exemplar는 mandatory `grammar_vs_drawing`에서 제외되고 negative/reference warning만 남는다.
- [x] P2 PASS exemplar는 positive control로 유지된다.
- [x] P3 exemplar는 `unproven_until_ablation`으로 worker packet과 audit에 표시된다.
- [x] top-level exemplar를 authoring owner로 선언하고 packaged copy hash drift를 검출한다.
- [x] FAIL exemplar 없이 worker packet과 subject-first review가 생성된다.
- [x] S04 closure evidence와 context capsule이 작성된다.

Evidence locations:

```text
skills/img2drawing/tests/test_exemplar_policy.py
skills/img2drawing/tests/test_exemplar_sync.py
dev/evidence/p3-fidelity/S04-exemplar-policy/
dev/planning/capsules/S04-exemplar-mandatory-path-cleanup.md
```

### S05 — Torso orientation closure

Status: `ACTIVE` (S04 capsule consumed; implementation in progress)

책임:

- frozen body view/near-far observation과 shoulder/torso envelope를 연결한다.
- side vs 3/4 오독, torso flattening, arm dominance를 검출할 evidence를 닫는다.

핵심 closure:

- torso 폭이 맞아도 회전/near-side exposure가 틀린 fixture가 blocker evidence를 만든다.
- `torso_orientation`, `near_arm`, `far_arm`의 contour ownership이 중복되지 않는다.

### S05 Definition of Closed

- [ ] subject/drawing orientation labels, shoulder envelope, torso bounds, near/far arm exposure를 독립 기록한다.
- [ ] side/3-quarter mismatch와 arm dominance drift가 evidence로 산출된다.
- [ ] 동일 lock digest, distinct artifact/observation id, stale drawing state를 검증한다.
- [ ] evidence utility는 artistic PASS/FAIL을 만들지 않는다.
- [ ] torso 폭이 비슷하지만 orientation/near-arm exposure가 틀린 fixture가 수치로 드러난다.
- [ ] schema, tests, visual board와 capsule이 작성된다.

### S06 — Pelvis and legs closure

책임:

- pelvis breadth/turn, 두 다리의 다중 width profile, inter-leg negative space, support/counterbalance를 하나의 lower-body chain으로 닫는다.

핵심 closure:

- parallel rails fixture를 검출한다.
- leg_A/leg_B의 side role과 width evidence가 뒤바뀌지 않는다.
- P4로 진행한 뒤에도 P3 taper/negative-space 개선이 유지되는 regression이 있다.

### S07 — Head and hair closure

책임:

- head top/chin, 좌우 cranial/jaw contour, hair envelope를 분리해 과대 구형 head와 helmet hair를 검출한다.

핵심 closure:

- face feature detail 없이도 head/hair primary mass fidelity를 판정할 수 있다.
- hair occlusion과 anatomical head uncertainty가 명시된다.

### S08 — Generic prop topology

책임:

- rifle 전용 명칭 대신 `major_axis`, `width_change_points`, `terminal_masses`, `body_overlap_points`, `visible_interruptions`, `occlusion_order`를 구현한다.

핵심 closure:

- rifle fixture와 비총기 fixture 하나가 같은 schema/API를 사용한다.
- gross axis만 맞고 폭 변화/overlap이 틀린 prop은 closed되지 않는다.
- 기존 P5 attached-object 규칙과 중복 owner를 만들지 않는다.

### S09 — Modular grammar cards + A/B/C ablation

책임:

- P3 full-body exemplar의 실효성을 A/B/C로 검증한다.
- positive/negative modular grammar cards와 concrete transfer mapping을 도입한다.

조건:

```text
A = subject + contract
B = subject + contract + current full-body exemplar
C = subject + contract + modular grammar cards
```

핵심 closure:

- region blocker 수, residual discrepancy 수, reopen 수를 비교한다.
- P3에서 끝내지 않고 P4까지 structural error를 추적한다.
- B가 A보다 낫지 않으면 current P3 exemplar를 mandatory path에서 제거한다.
- C가 P3 개선을 만들고 P4에서도 유지할 때만 채택한다.

## 8. Hardening and integration gates

모든 production slice에 공통 적용한다.

- correctness와 malformed/stale/empty evidence test
- checkpoint save/resume round trip
- real `DrawingRun` boundary integration smoke
- schema validation과 digest binding
- current dogfood regression 또는 독립 fixture
- performance/size budget 기록
- public API와 limitation 문서화
- 같은 책임의 두 번째 production implementation 부재 확인
- superseded adapter/orphan artifact의 제거 또는 명시적 보존 사유
- closure evidence와 context capsule

`looks better`만으로 closure하지 않는다. visual slice는 subject/drawing comparison board와 independent review record를 evidence로 남긴다.

## 9. Duplicate and experiment policy

- `foo_v2`, `foo_new`, `foo_final`을 만들지 않는다.
- 기존 `ObservationContract`, `RegistrationGraph`, `StageReviewRecord`, `DrawingRun`을 우회하는 alternate runtime을 만들지 않는다.
- contour extraction spike는 `/tmp` 또는 명시적 dev experiment 경로에만 두고 production import에서 접근하지 않는다.
- spike 종료 시 winner를 기존 canonical module로 이동하고 loser를 삭제한다.
- exemplar 두 tree는 S04 전까지 현 상태를 보존하되 임의로 한쪽만 수정하지 않는다.
- renderer/P6/spline은 전체 queue가 닫히기 전 production expansion 금지다.

## 10. Close and compress protocol

각 slice closure 시 다음 순서를 지킨다.

1. predeclared gates의 evidence path를 채운다.
2. duplicate/orphan check를 실행한다.
3. slice 상태를 `CLOSED`로 변경한다.
4. `dev/planning/capsules/SNN-<slice>.md`를 작성한다.
5. capsule에는 public API, inputs/outputs, invariants, budgets, limitations, evidence locations, reopen conditions만 남긴다.
6. 다음 slice 하나만 `ACTIVE`로 바꾼다.

Capsule이 없는 slice는 `CLOSED`로 선언할 수 없다.

## 11. Reopen conditions

CLOSED slice는 다음 증거가 생길 때만 `REOPENED`한다.

- subject/drawing provenance가 동일 좌표 복사를 통과시킨다.
- observation correction이 downstream evidence를 무효화하지 않는다.
- envelope measurement가 명백한 폭 축소/과장을 evidence로 만들지 못한다.
- blind packet에 worker rationale이나 prior verdict가 유출된다.
- process PASS만으로 P3가 advance한다.
- 새 subject class에서 frozen schema가 표현 불가능한 visibility/topology를 요구한다.

reopen record에는 reason, triggering evidence, affected contract, migration risk, 재closure gates를 기록하며 해당 slice가 단일 `ACTIVE` slot을 점유한다.

## 12. 구현 착수 시 첫 작업

S01 외의 production 코드를 만들지 않고 다음 순서로 시작한다.

1. `FrozenObservationRecord`와 observation reopen schema를 테스트로 먼저 작성한다.
2. `DrawingRun.lock_observation()` lifecycle precondition을 구현한다.
3. checkpoint/resume와 P1 reopen invalidation을 연결한다.
4. subject-only benchmark를 새 public path로 갱신한다.
5. error/legacy/round-trip test를 모두 통과시킨다.
6. S01 capsule을 작성하고 `CLOSED`한 뒤에만 S02를 활성화한다.
