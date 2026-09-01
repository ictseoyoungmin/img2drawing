# vNext work slices

This directory owns executable cards for current and upcoming work. Closed public
contracts and evidence belong in `../capsules/`; archived execution history belongs in
`../archive/`. Do not create duplicate cards for B00–B04.

Only `STATUS.md` and one card may be `ACTIVE` or `REOPENED` at a time.

## Card sequence

| Order | Card | Activation condition |
|---|---|---|
| 1 | [`B07.md`](B07.md) | CLOSED — R1/R2 hardening reclosed |
| 2 | [`B08.md`](B08.md) | CLOSED — narrow hardening reclosed 2026-08-31 |
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
CLOSED → REOPENED → CLOSED  (exceptional correction)
```

Every closure requires direct quality/contract review, relevant tests, a
duplicate/orphan check, synchronized status, an authoritative capsule, and its own
commit. A plan update alone never closes a card.
