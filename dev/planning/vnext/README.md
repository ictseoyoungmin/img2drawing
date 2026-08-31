# img2drawing vNext planning

이 디렉터리는 img2drawing vNext의 현재 계획 권위다. 제품 방향은 범용
drawing framework이지만, 구현은 Production WIP Limit = 1로 진행한다.

## 현재 한 줄 요약

```text
B00–B07의 구현/증거는 닫혀 있다.
B05 두 번째 재오픈에서 embedded R23 attention leak을 물리적으로 제거했고,
B06에서 residual-driven correction과 resume-safe provenance를 닫고,
B07에서 evidence budget과 cost telemetry를 닫았다.
다음 작업은 B08 DrawingIntent scaffolding이다.
```

`temp/img2drawing_vnext_universal_drawing_plan.html`은 이번 재구성의 제품·설계
입력이다. 저장소 상태와 충돌하는 HTML의 `B05 ACTIVE` 표기는 HEAD와 사용자
지시를 기준으로 B05를 두 차례 재오픈해 canonical Pn de-anchoring을 완료한 뒤
`CLOSED`로 보정했다. HTML은 상태 권위가 아니다.

## 읽기 순서

1. [`STATUS.md`](STATUS.md) — 현재 WIP와 바로 다음 gate
2. [`CONTRACT.md`](CONTRACT.md) — 이미 닫힌 core 계약과 향후 확장 불변식
3. [`ROADMAP.md`](ROADMAP.md) — B00–B18 전체 순서와 상태
4. [`slices/`](slices/) — 앞으로 실행할 B08–B18 작업 카드와 최근 closure record
5. [`capsules/`](capsules/) — 닫힌 구현을 재사용하기 위한 압축 문맥
6. [`archive/`](archive/) — 과거 실행 카드와 재오픈 이력

필요할 때만 읽는다.

- [`BASELINE.md`](BASELINE.md): R23 read-only baseline
- [`failure-dossier/`](failure-dossier/): reset을 정당화한 실패 증거
- [`path-sanitization-GATES.md`](path-sanitization-GATES.md): 이미 끝난 저장소 경로 위생 작업

## 권위 우선순위

충돌 시 다음 순서로 해석한다.

1. 현재 사용자 지시와 실제 HEAD
2. `STATUS.md`와 해당 `slices/Bxx.md`
3. `CONTRACT.md`
4. CLOSED capsule
5. archive와 failure dossier
6. 루트의 과거 roadmap 및 `temp/` 계획 산출물

과거 문서는 근거로 보존하지만 현재 상태를 덮어쓰지 않는다. CLOSED capsule을
수정해야 할 때는 먼저 해당 slice를 명시적으로 재오픈한다.

## 계획 구조 원칙

- `slices/`에는 실행 카드와 최근 closure record를 둔다.
- B00–B04는 새 카드를 복제하지 않고 기존 capsule/archive를 가리킨다.
- B05의 기존 closure는 유효한 역사다. 새 문서 정리 scope만 별도 재오픈한다.
- B06 closure는 `capsules/B06.md`에 public correction contract와 evidence를 보존하고,
  B07 closure는 `capsules/B07.md`에 evidence budget/telemetry contract를 보존한다.
- `DrawingIntent`, mode, style은 설계된 skeleton이며 현재 public API가 아니다.
- 테스트나 schema가 시각 품질을 자동 판정하지 않는다.
- mode/style을 이유로 별도 session이나 stage machine을 만들지 않는다.

## 제품 목표

하나의 `DrawingSession`, 명시적 stroke history, renderer, inspection, correction,
checkpoint/replay를 공유하면서 다음 intent를 처리한다.

- observed / imaginative / hybrid reference mode
- croquis / figure drawing / tonal study / free-draw
- pose / subject / form-light / expressive finish intent
- preset / override / custom style guidance

공통 loop는 다음과 같다.

```text
observe or declare intent
→ draw
→ render
→ inspect
→ choose the highest-impact residual
→ correct explicit strokes
→ inspect again
→ finish for the declared intent
```
