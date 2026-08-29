# img2drawing R23 evidence–execution truth hardening 계획

- 방법: Bottleneck, Production WIP Limit = 1
- 작성 기준일: 2026-08-29
- 기준 revision: `e6f85d0`
- 선행 계획: `img2drawing-material-integration-visual-quality-plan.md`
- 재개 사유: R23의 일부 closure evidence가 실제 action/artifact/worker provenance가
  아니라 caller가 제출한 manifest 주장만 검증한다.

```text
SYSTEM: P1→P5 + optional P6 architecture 유지 / authority contract 보강
COMPLETED: T1 R23 evidence–execution truth hardening
ACTIVE: T2 strict packaged fresh-worker contract/evaluator handoff
SKELETON: T3 release truth + docs cleanup
CLOSED: S01–S09, S11, S13; 기존 S14 scripted fixture는 smoke로만 유지
NOT FINAL-CLOSED: S10, S12, S14 strict, S15, G6 independent visual inspection
NEXT GATE: 실제 새 subject의 fresh worker 실행 + 별도 evaluator 반환 증거
```

이 문서는 기존 R23 계획의 `S10–S15 CLOSED` 선언을 그대로 승계하지 않는다.
기존 artifact는 삭제 전까지 조사 자료로 남길 수 있지만, 아래 재closure gate를
통과하기 전에는 R23 최종 승인 근거가 아니다.

## 1. 판정

현재 최상위 병목은 기능 부족이 아니라 **proof integrity**다.

- P6 positive fixture가 P5의 hair/face ownership 결함을 P6에서 삭제해 고쳤다.
- calibration은 비교용 PNG를 렌더하지 않으면서 비교했다고 기록한다.
- P6 stroke budget과 construction retirement는 runtime 관측값이 아니라 caller 주장이다.
- P6 manifest의 drawing artifact digest가 실제 prepared review PNG에 bind되지 않는다.
- `stage_start()` 없이 draw/review/advance 가능한 경로가 남아 있다.
- S14는 새 agent 실행이 아니라 좌표와 review 문장을 포함한 scripted fixture다.
- G6는 외부 독립 시각 승인을 받은 것으로 볼 수 없다.

그러므로 새 기능, renderer 교체, 추가 subject 확장은 중지한다. 먼저 runtime과
canonical evidence 사이의 진실성 간극을 닫고, 그 뒤 strict fresh-worker와 release를
직렬로 진행한다.

## 2. 한 화면 시스템 스케치

```text
subject + frozen observation
        │
        ▼
stage_start(stage) ── mandatory lifecycle boundary
        │
        ▼
DrawingRun history ── sole action/provenance truth
        │              ├─ P5 retirement derived/validated here
        │              └─ P6 role/count budgets derived here
        ▼
prepared review PNG ── sole reviewed raster for the pass
        │
        ├─ artifact SHA binding
        ├─ rendered calibration JSON + PNG + 50% PNG binding
        └─ independent semantic review
        ▼
canonical S10 fixture (P5 defect → P5 reopen → fresh P5 review → P6)
        ▼
strict packaged fresh worker (new session) + separate blind evaluator
        ▼
rebuilt R23 ZIP/wheel/tree + CI + docs + independent visual approval
```

## 3. 동결할 contract

기존 product architecture는 유지한다. 다음 진실성 규칙만 freeze한다.

### 3.1 Lifecycle

- current stage의 `started_cursor`가 없으면 draw, batch draw, review preparation,
  review submission, manifest submission과 ADVANCE가 모두 fail closed한다.
- `stage_start()`는 stage당 한 authoritative 시작점이며 resume/reopen 뒤에도 같은
  규칙을 적용한다.
- P6에서 P1–P5 소유 stroke를 delete/replace/soft-lift하는 것은 금지한다. 그런
  결함은 earliest responsible stage로 reopen한다.

### 3.2 Action provenance

- `DrawingRun` history와 stage-start cursor가 stroke count와 retirement의 유일한
  mechanical authority다.
- P6 manifest는 count를 임의 입력받아 신뢰하지 않는다. serialized count는
  runtime-derived observation이어야 한다.
- identity, confirmation/restatement, accent와 fold 분류는 P6 stage-start 이후의
  active action slice와 action role/kind에서 계산한다.
- P5 retired ID는 실제 P5 action slice에서 존재하던 stroke에 delete 또는 soft-lift가
  수행된 사실과 일치해야 한다.
- retained ghost와 contour owner는 bound cursor의 current IR에 실제 존재해야 하며,
  contour owner는 P5가 소유한 active stroke여야 한다.

### 3.3 Artifact and calibration binding

- P6 `drawing_artifact_sha256`는 현재 P6 pass의 `prepare_stage_review()`가 만든 PNG
  SHA-256과 정확히 일치해야 한다.
- calibration은 `pencil-contact-v9` production material path로 actual canvas scale의
  straight, C, S, taper-in/out sample을 렌더한다.
- canonical output은 최소한 아래 세 파일을 포함한다.

```text
identity/calibration_sheet.json
identity/calibration_sheet.png
identity/calibration_sheet_50pct.png
```

- JSON은 두 PNG의 digest, dimensions, sample/profile selection과 evaluator rationale을
  bind한다. PNG가 없거나 hash/size가 다르면 P6는 advance하지 못한다.
- rationale은 실제 artifact inspection 뒤에 caller/evaluator가 작성한다.
  `default()`가 보지 않은 비교를 했다고 자동 주장하지 않는다.

### 3.4 Worker and evaluator separation

- scripted coordinates fixture는 API/generalization smoke일 뿐 fresh-worker evidence가 아니다.
- strict fresh-worker의 허용 입력은 exact packaged ZIP, 새 subject, user goal과 실행
  envelope뿐이다.
- drawing worker와 최종 visual evaluator는 서로 다른 fresh session이어야 한다.
- verifier는 semantic quality를 자동 승인하지 않고 input allowlist, package hash,
  run mechanics, artifact binding과 forbidden provenance만 검사한다.

### 3.5 Compatibility

- checkpoint/session/schema 변경은 versioned migration과 round-trip test를 가진다.
- 기존 v1 evidence는 읽을 수 있더라도 새 R23 closure authority로 자동 승격하지 않는다.
- release identity는 최종 rebuild 전까지 `0.5.2.dev23 / R23 candidate`로 취급한다.

## 4. REOPEN record — T1 R23 evidence–execution truth hardening

Status: `CLOSED after truth-hardening implementation and regression evidence`

### Reason

S10 positive fixture와 S12 P6 evidence contract가 실제 artifact/action truth보다
manifest self-report를 더 강하게 신뢰한다.

### Triggering evidence

- `build_material_quality_run.py`가 P6에서 P5 hair contour/mass 네 개를 삭제한다.
- `CalibrationSheet.default()`가 PNG 없이 actual/50% 비교 완료 rationale을 만든다.
- `IdentityFinishManifest`의 count는 caller가 입력한다.
- `submit_identity_finish_manifest()`가 prepared P6 PNG hash를 확인하지 않는다.
- test가 state hash와 존재하지 않는 retirement IDs로 통과한다.
- canonical S10 script가 P6 `stage_start()`를 호출하지 않는다.

### Affected contract surface

- `DrawingRun` stage lifecycle and review submission
- P5 `ConstructionRetirementRecord`
- P6 `CalibrationSheet`, `IdentityFinishManifest`, schemas and checkpoint persistence
- canonical S10 builder/evidence/verifier

### Migration / regression risk

- manifest/schema version change가 기존 checkpoint resume를 깨뜨릴 수 있다.
- stage-start enforcement가 lifecycle을 우회하던 fixture/test를 드러낼 수 있다.
- runtime-derived counts의 role mapping을 잘못 정하면 valid P6 run을 거부할 수 있다.
- S10 artifact 재생성으로 release hashes가 모두 바뀐다.

### What remains authoritative

- 원본 subject와 frozen observation만 geometry truth다.
- `DrawingRun`/StrokeIR/history가 state와 action provenance owner다.
- P1→P5 default, optional P6 boundary와 기존 renderer owner는 유지한다.
- S11 resolved-form grammar와 S13 adaptive evidence contract는 유지한다.

## 5. T1 실행 순서

이 순서는 T1 내부의 한 production slice다. 중간 상태를 별도 CLOSED slice로 선언하지
않는다.

1. **Authority/status truth reset**
   - `GATES.md`에서 G2를 REOPEN, G4를 scripted smoke CLOSED + strict S14b OPEN,
     G5를 mechanical artifact validation only, G6를 OPEN으로 바로잡는다.
   - G1의 residual binding 자체는 유지하되 canonical S10 whole-run closure는 T1 완료
     전까지 REOPENED로 기록한다.
2. **Fail-first characterization**
   - fake P6 PNG digest, fake count, nonexistent retirement ID, non-retired ID,
     nonexistent contour owner와 missing `stage_start`가 현재 통과하는 최소 test를 만든다.
   - P6가 upstream-owned stroke를 수정하는 경우도 실패 조건으로 고정한다.
3. **Stage lifecycle hardening**
   - current stage start를 요구하는 공통 guard를 추가하고 draw/review/advance/manifest
     경계에 적용한다.
   - reopen/resume/legacy migration test를 함께 닫는다.
4. **History-derived provenance**
   - P5 stage slice에서 retirement 사실과 current IR ownership을 계산·검증한다.
   - P6 stage slice에서 role/kind별 count와 accent fraction을 계산한다.
   - caller 입력 count는 제거하거나 runtime-derived 값과 불일치 시 거부하는 migration
     shim으로 한정한다.
5. **Rendered calibration**
   - actual-size calibration PNG와 deterministic 50% preview를 생성한다.
   - JSON에 두 artifact hash/size와 selected profile을 bind한다.
   - missing, blank, stale, tampered artifact tests를 추가한다.
6. **P6 review artifact binding**
   - current prepared P6 review PNG가 없거나 digest/cursor/state가 다르면 manifest를
     제출할 수 없게 한다.
7. **Canonical S10 재생성**
   - P6 preflight/inspection에서 hair-face ownership defect를 발견하면 P5를 reopen한다.
   - P5에서 hair/face ownership을 수정하고 fresh resolved-form review로 ADVANCE한다.
   - P6를 명시적으로 start한 뒤 facial relation, grouped locks, sparse folds와 selective
     accent만 추가한다. P6 action slice에는 upstream stroke mutation이 없어야 한다.
   - final, review, calibration, report와 fixed hashes를 다시 생성한다.
8. **Contract/document closure**
   - schemas, skill reference, tests, verifier와 S10/S12 capsules를 새 authority에 맞춘다.
   - superseded false-positive evidence는 archive/negative fixture로 명명하거나 canonical
     authority에서 제거한다.

## 6. T1 Definition of Closed

- [x] missing `stage_start`에서 draw, prepare/submit review, manifest와 ADVANCE가 실패한다.
- [x] P6는 P1–P5-owned stroke를 직접 수정할 수 없고 reopen 경로만 허용한다.
- [x] fake/non-current `drawing_artifact_sha256`가 거부된다.
- [x] P6 budget 값이 P6 stage action history에서 재현 가능하며 caller가 위조할 수 없다.
- [x] retirement/ghost/contour IDs가 실제 history와 current IR에 대해 검증된다.
- [x] 실제 calibration PNG와 50% PNG가 nonblank이며 JSON digest/size와 일치한다.
- [x] calibration rationale은 자동 허위 비교 문구를 포함하지 않는다.
- [x] S10 기록에 `P6 발견 → P5 REOPEN → 수정 → fresh P5 review → P6`가 남는다.
- [x] regenerated P6 action slice에 upstream hair/face delete/replace/soft-lift가 없다.
- [x] malformed/stale/tampered, checkpoint resume/replay와 schema migration test가 통과한다.
- [x] 전체 `dev/tests`와 S10/S11-S12 verifier가 통과한다.
- [x] canonical S10 final/compare/calibration을 직접 확대 검사하고 결과를 기록한다.
- [x] public contract, limitation, evidence locations와 reopen conditions가 capsule에 남는다.
- [x] 중복 production owner와 orphaned false-positive authority가 없다.

### T1 next gate

검토자가 제시한 허점을 각각 재현하는 negative test가 수정 전 실패하고, 현재
수정 후에는 모두 차단되는 것을 확인했다.

## 7. Forward queue

T1은 닫혔다. T2 strict fresh-worker 증거를 먼저 닫은 뒤 T3 release/doc slice를
순차적으로 진행한다.

### T2 — S14b strict packaged fresh-worker E2E

Status: `ACTIVE — contract/verifier ready; external worker and evaluator pending`

1. 기존 `run_fresh_worker_generalization.py`와 evidence를
   `scripted_generalization_fixture`로 rename/reclassify한다.
2. GATE는 “scripted API portability smoke”로 낮추고 CLOSED 유지한다.
3. rebuilt candidate ZIP, 이전에 쓰지 않은 subject와 user goal만 포함한 input
   allowlist/envelope를 만든다.
4. repository history, material, dogfood reports/actions/coordinates를 보지 못하는 새
   semantic worker/session에서 unpacked package만 사용해 P1→P5/P6 E2E를 수행한다.
5. 별도 fresh evaluator/session이 rationale-free subject/current-drawing packet을 보고
   visual verdict를 작성한다.
6. `audit_fresh_worker.py`를 actual registry(P1→P5 또는 P1→P6), current schema,
   package identity와 artifact binding에 맞게 강화한다.
7. `verify_bottleneck_completion.py --check s14b`는 input allowlist, package SHA,
   worker/evaluator session separation, mechanical audit와 returned artifact hashes를
   검증한다.

#### T2 progress ledger

- [x] strict input/report/visual-review schemas are versioned and schema-validated.
- [x] candidate input preparation excludes packaged examples/dogfood artifacts.
- [x] mechanical audit accepts the current P1→P5/P6 registry and remains non-visual.
- [x] verifier refuses to promote the existing scripted fixture.
- [x] contract tests pass with the full test suite (65 tests).
- [ ] external fresh worker executes the prepared package in a new session.
- [ ] independent evaluator returns a rationale-free visual `advance` record.

See `dev/planning/capsules/T2-strict-fresh-worker-contract.md` for the handoff
contract and exact returned-evidence layout.

T2 closure에는 worker input envelope, package SHA, returned checkpoint/history,
mechanical audit, independent visual review, raw whole/comparison board와 limitation이
모두 필요하다. 새 worker였다는 사실을 report boolean 하나로 대체하지 않는다.

### T3 — R23 release truth and documentation closure

Status: `SKELETON`

1. README 대표 R22 showcase는 R22로 정확히 표기하거나 실제 승인된 R23 asset으로
   교체한다.
2. `dev/PACKAGE_CONTENTS.md`의 canonical R21 문구를 현재 release authority와 맞춘다.
3. Requirements에서 자동 설치되지 않는 `svgwrite`를 제거하고
   `pip install "skills/img2drawing[dev]"`를 사용한다.
4. GATES의 interim reopen 상태를 최종 evidence와 일치시키되, G6는 실제 독립 검사
   전까지 OPEN으로 둔다.
5. T1/T2가 닫힌 source로 R23 ZIP, wheel, tree와 manifests/checksums를 전부 재생성한다.
6. clean install/import, full tests, S10/S11-S12/S14b/S15 verifier와 CI를 통과시킨다.
7. 새 final/comparison/calibration PNG를 독립적으로 확대 비교해 G6 verdict를 기록한다.
8. release/capsules/handoff가 같은 version, revision, hash와 limitation을 가리킬 때만
   R23을 최종 CLOSED로 선언한다.

## 8. 전체 종료 조건

```text
T1 CLOSED: runtime evidence == actual actions/artifacts
    ↓
T2 CLOSED: strict new worker + separate evaluator evidence
    ↓
T3 CLOSED: rebuilt release + truthful docs + independent visual approval
    ↓
R23 FINAL CLOSED
```

체크리스트와 CI가 모두 통과해도 대표 PNG의 독립 시각 검토가 없거나 artifact 자체가
목표 품질보다 낮으면 R23은 닫지 않는다.
