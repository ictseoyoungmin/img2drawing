# img2drawing vNext status

Updated: 2026-08-31

```text
SYSTEM:   B00–B05 implementation evidence closed; universal contract refreshed
ACTIVE:   none
NEXT:     reopen B05 for canonical Pn guidance de-anchoring
SKELETON: B06 residual correction; B07 evidence cost control; B08–B18 platform/release
CLOSED:   B00, B01, B02+B03, B04, B05 original construction + arm correction
NEXT GATE: explicitly mark B05 REOPENED, then change only its documented reopen scope
```

## Why B05 is next again

HEAD `ff459e8` closes B05 construction and the near/right-arm correction with committed
subject-only visual evidence. That closure remains valid.

The universal drawing plan adds new evidence that the normal skill reading route still
contains substantial P1–P6 guidance. Before B06 or mode/style work begins, B05 must be
reopened for a narrow documentation/attention migration:

- remove Pn lifecycle guidance from the canonical path;
- extract useful drawing knowledge into stage-free references;
- retain one explicit legacy R23 compatibility entry;
- prove a new-task worker does not enter Pn documents by default.

The planned reopen record and gates are in [`slices/B05.md`](slices/B05.md). This
planning edit does not itself activate or implement that reopen.

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
- Current HEAD at planning inspection: `ff459e8`
- vNext code: `inspection/`, `vnext/session.py`, `vnext/construction.py`
- vNext tests: inspection, session, construction suites under `dev/tests/`
- B05 dogfood: `dev/dogfood/vnext-b05/`
- Representative visual evidence: `dev/evidence/vnext/b02-b03/` and
  `dev/evidence/vnext/b05/`
- Legacy stage runtime remains in `run.py`, `stages/`, `review/`, playbooks, and
  `references/stages/`; it is compatibility/reference material, not the vNext path.

## WIP guard

Until B05 is explicitly reopened and reclosed:

- do not activate B06;
- do not add `DrawingIntent`, mode/style registries, tonal/free-draw pipelines, or
  renderer families;
- do not physically remove R23 runtime or persistence;
- do not rewrite the accepted B05 drawing geometry unless new visual evidence triggers
  a separate construction-quality reopen.

## Next after B05 reclosure

B06 becomes the sole candidate for activation. It will add residual records and
responsible-stroke correction policy over the existing B04/B05 surface. See
[`ROADMAP.md`](ROADMAP.md) and [`slices/B06.md`](slices/B06.md).
