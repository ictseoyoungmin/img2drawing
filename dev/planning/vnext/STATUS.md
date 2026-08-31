# img2drawing vNext status

Updated: 2026-08-31

```text
SYSTEM:   B00–B07 closed; canonical stage-free reading route physically isolated
ACTIVE:   none
NEXT:     activate B08 DrawingIntent scaffolding
SKELETON: B08 DrawingIntent + mode/style; B09–B18 platform/release
CLOSED:   B00, B01, B02+B03, B04, B05 construction + canonical route de-anchoring, B06, B07
NEXT GATE: B08 activation: intent/mode/style scaffolding contract and dogfood
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

The post-reclosure CI follow-up also updated `dev/release/validate_r23_release.py` so the
R23 release gate verifies identity and preserved compatibility assets instead of requiring
Pn doctrine in canonical `SKILL.md`. The fix is covered by
`dev/tests/test_r23_release_validator.py`; no drawing or canonical route content changed.

The reopen record and evidence are in [`slices/B05.md`](slices/B05.md),
[`capsules/B05.md`](capsules/B05.md), and
[`../evidence/vnext/b05/canonical-route-fresh-worker.md`](../../evidence/vnext/b05/canonical-route-fresh-worker.md).
B05 is closed. B06 was explicitly activated as the sole production WIP and is now closed;
B07 was then activated and closed under the same WIP rule.

## B06 closure — residual-driven correction

Activated: 2026-08-31 after B05 reclosure and the R23 release-gate compatibility fix.
The slice is deliberately narrow: add Agent-authored residual/correction provenance on
the existing `DrawingSession` and inspection boundary, prove premise/global and local
repairs against the B05 subject, and preserve checkpoint/resume integrity. No stage
runtime, renderer, inspection implementation, mode registry, or automatic visual score
is in scope.

Activation risks:

- stale before/after inspection evidence could be accepted after a later mutation;
- correction actions could become detached from the observation that motivated them;
- residual memory could accidentally become a lifecycle gate or duplicate history.

The B06 contract addressed these with immutable inspection digests, explicit action and
observation references, `keep`/`revise` decisions, and atomic checkpoint writes. The
closure evidence is [`../evidence/vnext/b06/REVIEW.md`](../../evidence/vnext/b06/REVIEW.md),
the executable fixture is [`../dogfood/vnext-b06/README.md`](../../dogfood/vnext-b06/README.md),
and the public API is compressed in [`capsules/B06.md`](capsules/B06.md).

## Closed foundation

| Slice | State | Authoritative context |
|---|---|---|
| B00 | CLOSED | [`capsules/B00.md`](capsules/B00.md) |
| B01 | CLOSED | [`capsules/B01.md`](capsules/B01.md) |
| B02+B03 | CLOSED | [`capsules/B02-B03.md`](capsules/B02-B03.md) |
| B04 | CLOSED | [`capsules/B04.md`](capsules/B04.md) |
| B05 construction + canonical route de-anchoring | CLOSED | [`capsules/B05.md`](capsules/B05.md) |
| B06 residual-driven correction | CLOSED | [`capsules/B06.md`](capsules/B06.md) |
| B07 evidence / cost control | CLOSED | [`capsules/B07.md`](capsules/B07.md) |

## Current repository truth

- Frozen R23 baseline: `25ec4544e86fe37fc28d64575df145a1b711d63a`
- Current HEAD: this branch's latest closure commit (use `git log` for the exact SHA)
- vNext code: `inspection/`, `vnext/session.py`, `vnext/construction.py`, `vnext/evidence.py`
- vNext tests: inspection, session, construction, correction, and evidence suites under `dev/tests/`
- B05 dogfood: `dev/dogfood/vnext-b05/`
- B06 correction dogfood: `dev/dogfood/vnext-b06/`
- Representative visual evidence: `dev/evidence/vnext/b02-b03/`, `dev/evidence/vnext/b05/`,
  `dev/evidence/vnext/b06/`, and `dev/evidence/vnext/b07/`
- Legacy stage runtime remains in `run.py`, `stages/`, `review/`, playbooks, and
  `references/stages/`; it is compatibility/reference material, not the vNext path.

## WIP guard

With B07 closed and before B08 activation:

- do not implement B08 or later slices until B08 has an activation record;
- do not reopen B05 unless new construction-quality evidence requires it;
- do not add `DrawingIntent`, mode/style registries, tonal/free-draw pipelines, or
  renderer families;
- do not physically remove R23 runtime or persistence;
- do not rewrite the accepted B05 drawing geometry unless new visual evidence triggers a
  separate construction-quality reopen.

## B07 closure — evidence and cost control

Activated and closed: **2026-08-31**. The existing `InspectionSheet` now carries an
Agent-authored quick/focused/deep evidence policy, with a maximum of three prioritized
ROIs and a reasoned deep escalation. `DrawingSession` persists immutable telemetry for
inspection calls, review turns, generated/visual artifacts, elapsed work, and explicit
artifact reads; stale snapshots are visible and unreadable evidence fails explicitly.

The B05 representative correction used two review turns, four image reads, eight visual
artifacts, and twelve generated artifacts, compared with the preserved R23 fixture's five
review ceremonies, twelve visual files, and sixty stage-review files. Direct sheets,
tests, and the capsule are committed under the B07 evidence paths.

## Next after B07 closure

B08 may be activated after this B07 closure evidence, capsule, and full repository gates
are committed and green. See [`ROADMAP.md`](ROADMAP.md) and [`slices/B08.md`](slices/B08.md).
