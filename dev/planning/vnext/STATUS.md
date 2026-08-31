# img2drawing vNext status

Updated: 2026-08-31

```text
SYSTEM:   B00–B05 closed; canonical stage-free reading route established
ACTIVE:   none
NEXT:     B06 residual correction (manual activation required)
SKELETON: B06 residual correction; B07 evidence cost control; B08–B18 platform/release
CLOSED:   B00, B01, B02+B03, B04, B05 construction + canonical route de-anchoring
NEXT GATE: explicitly activate B06; no B06 implementation is active yet
```

## B05 reopen resolution

The B05 construction and near/right-arm correction closure remained valid. On 2026-08-31
B05 was reopened for a narrow documentation/attention migration and reclosed after the
canonical route audit and example/test gates passed.

The completed migration:

- rewrote the canonical `SKILL.md` route around observe → draw → inspect → correct →
  finish;
- moved reusable gesture, mass, balance, contour, identity, mode, and residual guidance
  into stage-free references;
- retained legacy stage/runtime material behind the explicit `legacy-r23.md` gateway and
  marker READMEs;
- rewrote the bundled full-body example to use `DrawingSession` and no target/answer image.

The reopen record and final evidence are in [`slices/B05.md`](slices/B05.md) and
[`capsules/B05.md`](capsules/B05.md). B05 is closed; B06 is the sole candidate and remains
inactive until explicitly activated.

## Closed foundation

| Slice | State | Authoritative context |
|---|---|---|
| B00 | CLOSED | [`capsules/B00.md`](capsules/B00.md) |
| B01 | CLOSED | [`capsules/B01.md`](capsules/B01.md) |
| B02+B03 | CLOSED | [`capsules/B02-B03.md`](capsules/B02-B03.md) |
| B04 | CLOSED | [`capsules/B04.md`](capsules/B04.md) |
| B05 original | CLOSED | [`capsules/B05.md`](capsules/B05.md) |

## Current repository truth

- Frozen R23 baseline: `25ec4544e86fe37fc28d64575df145a1b711d63a`
- Current HEAD: this branch's latest closure commit (use `git log` for the exact SHA)
- vNext code: `inspection/`, `vnext/session.py`, `vnext/construction.py`
- vNext tests: inspection, session, construction suites under `dev/tests/`
- B05 dogfood: `dev/dogfood/vnext-b05/`
- Representative visual evidence: `dev/evidence/vnext/b02-b03/` and
  `dev/evidence/vnext/b05/`
- Legacy stage runtime remains in `run.py`, `stages/`, `review/`, playbooks, and
  `references/stages/`; it is compatibility/reference material, not the vNext path.

## WIP guard

While B06 is not explicitly activated:

- do not implement B06 or later slices;
- do not add `DrawingIntent`, mode/style registries, tonal/free-draw pipelines, or
  renderer families;
- do not physically remove R23 runtime or persistence;
- do not rewrite the accepted B05 drawing geometry unless new visual evidence triggers a
  separate construction-quality reopen.

## Next after B05 reclosure

B06 becomes the sole candidate for activation. It will add residual records and
responsible-stroke correction policy over the existing B04/B05 surface. See
[`ROADMAP.md`](ROADMAP.md) and [`slices/B06.md`](slices/B06.md).
