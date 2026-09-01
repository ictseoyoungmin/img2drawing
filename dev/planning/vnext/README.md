# img2drawing vNext planning

이 디렉터리는 img2drawing vNext의 현재 계획 권위다. 제품 방향은 범용 drawing
framework이며, 구현은 항상 **Production WIP Limit = 1**로 진행한다.

## 현재 한 줄 요약

```text
B00–B09 + B01-R1/B07-R1 hardening은 CLOSED.
B10–B18은 남은 product surface를 완성하는 implementation phase다.
새 fresh visual dogfood는 B18 freeze 이전에 시작하지 않는다.
B10 Intent-aware completion이 현재 production WIP다.
```

최근 dogfood는 이미 foundation 결함을 충분히 드러냈다. 특히 B07-R1의 value-region
compaction과 B01-R1의 subject-boundary observation hardening은 그 결과를 흡수한
closure다. 이제 같은 subject를 반복해서 사용하며 architecture를 흔드는 대신,
남은 제품 surface를 B09→B18 순서로 먼저 닫고 그 뒤 하나의 통합 dogfood campaign을
실행한다.

`temp/img2drawing_vnext_universal_drawing_plan.html`은 제품·설계 입력이지만 상태
권위가 아니다. 실제 HEAD, `STATUS.md`, active slice가 우선한다.

## 읽기 순서

1. [`STATUS.md`](STATUS.md) — 현재 WIP와 바로 다음 gate
2. [`CONTRACT.md`](CONTRACT.md) — architecture invariant와 구현/검증 경계
3. [`ROADMAP.md`](ROADMAP.md) — B00–B18 구현 순서와 이후 D/R phase
4. [`slices/`](slices/) — B09–B18 실행 카드
5. [`VALIDATION_RELEASE.md`](VALIDATION_RELEASE.md) — B18 이후 D01–D06 dogfood와 R01–R04 release
6. [`capsules/`](capsules/) — 닫힌 구현을 재사용하기 위한 압축 문맥
7. [`archive/`](archive/) — 과거 실행 카드와 재오픈 이력

필요할 때만 읽는다.

- [`BASELINE.md`](BASELINE.md): R23 read-only baseline
- [`failure-dossier/`](failure-dossier/): reset을 정당화한 실패 증거
- [`path-sanitization-GATES.md`](path-sanitization-GATES.md): 완료된 저장소 경로 위생 작업

## 권위 우선순위

충돌 시 다음 순서로 해석한다.

1. 현재 사용자 지시와 실제 HEAD
2. `STATUS.md`와 해당 `slices/Bxx.md`
3. `CONTRACT.md`
4. `ROADMAP.md` / `VALIDATION_RELEASE.md`
5. CLOSED capsule
6. archive, failure dossier, `temp/` 계획 산출물

과거 문서는 근거로 보존하지만 현재 상태를 덮어쓰지 않는다. CLOSED capsule을
수정해야 할 때는 먼저 해당 slice를 명시적으로 재오픈한다.

## 계획 구조 원칙

- B09→B18은 **기능 구현/계약 완성** phase다. fresh unseen-subject dogfood를 closure
  gate로 끼워 넣지 않는다.
- 각 implementation slice는 synthetic/deterministic fixture, unit/integration test,
  이미 보존된 evidence만으로 기술적 계약을 닫는다.
- B18은 "dogfood-ready system freeze"다. 이후 새 기능을 추가하지 않고 D01–D06에서
  발견한 defect는 responsible B-slice를 REOPEN해 고친다.
- `DrawingIntent`, `ModeGuide`, `FinishGuide`, `StyleGuide`는 plain-data authoring guidance이며
  lifecycle cursor나 renderer pipeline이 아니다.
- `StyleGuide`와 `RenderProfile`은 분리한다.
- 테스트나 schema가 시각 품질을 자동 판정하지 않는다.
- mode/style을 이유로 별도 session, history, renderer, inspection tree를 만들지 않는다.
- R23의 물리 삭제는 통합 dogfood와 regression을 통과한 뒤 R03에서만 수행한다.

## 제품 목표

하나의 `DrawingSession`, 명시적 action/stroke history, renderer, inspection,
residual correction, checkpoint/replay를 공유하면서 다음 intent를 처리한다.

- observed / imaginative / hybrid reference mode
- croquis / figure drawing / tonal study / line study / free-draw
- pose / subject / form-light / expressive finish intent
- preset / override / custom style guidance

공통 loop는 다음과 같다.

```text
observe or declare intent
→ draw
→ render
→ inspect
→ choose the highest-impact residual
→ correct explicit authored representation
→ inspect again
→ finish for the declared intent
```
