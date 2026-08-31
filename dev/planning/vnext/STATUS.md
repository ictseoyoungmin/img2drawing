# img2drawing vNext status

Updated: 2026-08-31

```text
SYSTEM:   B00–B05 closed; canonical stage-free reading route physically isolated
ACTIVE:   none
NEXT:     B06 residual correction (manual activation required)
SKELETON: B06 residual correction; B07 evidence cost control; B08–B18 platform/release
CLOSED:   B00, B01, B02+B03, B04, B05 construction + canonical route de-anchoring
NEXT GATE: explicitly activate B06; no B06 implementation is active yet
```

## B05 second reopen resolution — attention boundary

The B05 construction and near/right-arm correction closure remain valid. A review of the
first documentation migration found that the full R23 body was still embedded in the
same `SKILL.md` file under a collapsed `<details>` element. That is not an LLM attention
boundary, so B05 was reopened narrowly on 2026-08-31 and reclosed after the physical
separation and fresh-worker evidence gates passed.

Affected surface and risk:

- `skills/img2drawing/SKILL.md`: remove the embedded legacy body while preserving one
  short pointer to `references/legacy-r23.md`;
- `skills/img2drawing/references/INDEX.md`: stop enumerating legacy descendants in the
  canonical index and retain only the gateway;
- `dev/evidence/vnext/b05/canonical-route-fresh-worker.md`: record the actual fresh-route
  file set and explicit non-reads;
- risk addressed: compatibility remains discoverable through the gateway, and the
  fresh-worker result is recorded as a concrete trace artifact.

The accepted construction geometry, `DrawingSession`, inspection/checkpoint semantics,
stage-free references, and subject-only example remain frozen.

The reopen record and evidence are in [`slices/B05.md`](slices/B05.md),
[`capsules/B05.md`](capsules/B05.md), and
[`../evidence/vnext/b05/canonical-route-fresh-worker.md`](../../evidence/vnext/b05/canonical-route-fresh-worker.md).
B05 is closed; B06 is the sole candidate and remains inactive until explicitly activated.

## Closed foundation

| Slice | State | Authoritative context |
|---|---|---|
| B00 | CLOSED | [`capsules/B00.md`](capsules/B00.md) |
| B01 | CLOSED | [`capsules/B01.md`](capsules/B01.md) |
| B02+B03 | CLOSED | [`capsules/B02-B03.md`](capsules/B02-B03.md) |
| B04 | CLOSED | [`capsules/B04.md`](capsules/B04.md) |
| B05 construction + canonical route de-anchoring | CLOSED | [`capsules/B05.md`](capsules/B05.md) |

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
