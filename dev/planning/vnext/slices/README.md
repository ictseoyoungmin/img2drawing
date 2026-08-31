# vNext work slices

이 디렉터리에는 아직 수행할 production slice만 둔다. 모든 카드는 `SKELETON`
상태이며, 실제 작업을 시작할 때 `STATUS.md`와 해당 카드 하나만 `ACTIVE`로 바꾼다.

## Closed work

B00–B04는 중복 카드를 만들지 않는다. `../capsules/`에서 public contract와
evidence를 읽고, 실행 이력이 필요할 때만 `../archive/`를 연다. B05의 construction
closure와 canonical route de-anchoring 결과도 `../capsules/B05.md`에 보존한다.

## Pending cards

| Order | Card | Activation condition |
|---|---|---|
| 1 | [`B06.md`](B06.md) | B05 closed; explicit activation |
| 2 | [`B07.md`](B07.md) | B06 closed |
| 3 | [`B08.md`](B08.md) | B07 closed |
| 4 | [`B09.md`](B09.md) | B08 closed |
| 5 | [`B10.md`](B10.md) | B09 closed |
| 6 | [`B11.md`](B11.md) | B10 closed |
| 7 | [`B12.md`](B12.md) | B11 closed |
| 8 | [`B13.md`](B13.md) | B12 closed |
| 9 | [`B14.md`](B14.md) | B13 closed |
| 10 | [`B15.md`](B15.md) | B14 closed |
| 11 | [`B16.md`](B16.md) | B15 closed |
| 12 | [`B17.md`](B17.md) | B16 closed |
| 13 | [`B18.md`](B18.md) | B17 closed |

## Card lifecycle

```text
SKELETON → ACTIVE → CLOSED
CLOSED → REOPENED → CLOSED (예외적 재오픈)
```

한 번에 하나만 `ACTIVE` 또는 `REOPENED`일 수 있다. 각 closure에는 direct
quality inspection, tests, duplicate/orphan check, authoritative capsule이 필요하다.
