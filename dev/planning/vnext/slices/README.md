# vNext work slices

이 디렉터리에는 실행 카드와 최근 closure record를 둔다. B05의 construction 및
canonical route de-anchoring, B06 residual correction, B07 evidence/cost control은
닫혀 있고, 나머지 카드는 `SKELETON`이다. 실제 작업을 시작할 때 `STATUS.md`와 해당 카드 하나만
`ACTIVE`/`REOPENED`로 바꾼다.

## Closed work

B00–B04는 중복 카드를 만들지 않는다. `../capsules/`에서 public contract와
evidence를 읽고, 실행 이력이 필요할 때만 `../archive/`를 연다. B05의 construction
closure와 canonical route de-anchoring 결과도 `../capsules/B05.md`에 보존한다. B06
residual/correction provenance와 B07 evidence/cost closure는 각각
`../capsules/B06.md`, `../capsules/B07.md`에 보존한다.

## Pending cards

| Order | Card | Activation condition |
|---|---|---|
| 1 | [`B07.md`](B07.md) | CLOSED — R1/R2 hardening reclosed |
| 2 | [`B08.md`](B08.md) | B07 closed; explicit activation |
| 3 | [`B09.md`](B09.md) | B08 closed |
| 4 | [`B10.md`](B10.md) | B09 closed |
| 5 | [`B11.md`](B11.md) | B10 closed |
| 6 | [`B12.md`](B12.md) | B11 closed |
| 7 | [`B13.md`](B13.md) | B12 closed |
| 8 | [`B14.md`](B14.md) | B13 closed |
| 9 | [`B15.md`](B15.md) | B14 closed |
| 10 | [`B16.md`](B16.md) | B15 closed |
| 11 | [`B17.md`](B17.md) | B16 closed |
| 12 | [`B18.md`](B18.md) | B17 closed |

## Card lifecycle

```text
SKELETON → ACTIVE → CLOSED
CLOSED → REOPENED → CLOSED (예외적 재오픈)
```

한 번에 하나만 `ACTIVE` 또는 `REOPENED`일 수 있다. 각 closure에는 direct
quality inspection, tests, duplicate/orphan check, authoritative capsule이 필요하다.
