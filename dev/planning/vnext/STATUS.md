# img2drawing vNext status

Updated: 2026-08-30

```text
SYSTEM:   architecture contract frozen / session foundation closed
ACTIVE:   none (B06 correction loop remains a skeleton)
SKELETON: B06 correction loop;
          B07–B18 remaining slices
CLOSED:   B00 Legacy R23 freeze + failure dossier; B01 vNext contract and architecture cut;
          B02+B03 Inspection Foundation; B04 stage-agnostic DrawingSession
NEXT GATE: separate manual activation decision for B06; keep B06 inactive
```

## B00 closure

- Frozen legacy baseline: `25ec454`
- Baseline verifier: `dev/planning/vnext/verify_baseline.py`
- Failure dossier: `failure-dossier/gemini.md`, `failure-dossier/claude.md`,
  `failure-dossier/r23-architecture.md`
- Context capsule: `capsules/B00.md`
- Archived card: `archive/B00.md`

## B01 closure

- Contract/audit capsule: `capsules/B01.md`
- Archived card and dependency audit: `archive/B01.md`
- No source, runtime, or review-schema implementation was introduced.

## B02+B03 closure after reopen

- Archived card: `archive/B02-B03.md`
- Context capsule: `capsules/B02-B03.md`
- Reopen R1–R6 closed: corrected non-identity raster registration, bound
  subject/drawing/state digests, narrowed stage-free normalization, and committed
  direct visual evidence.
- Full tests and all baseline/path gates pass; direct visual review is recorded under
  `dev/evidence/vnext/b02-b03/REVIEW.md`.
- B04 was REOPENED and is now CLOSED after artifact-level provenance hardening.
  The reopened scope covered immutable repeated inspection evidence, failed-
  checkpoint artifact rollback, observation-ID integrity, and custom checkpoint
  path metadata.
- B05 was manually activated after reviewing the corrected B04 capsule. Its
  construction phases were skill-side authoring vocabulary, not runtime stages.
- B06 and later correction/runtime lifecycle work remain inactive.

## B04 closure after reopen

- Archived card: `archive/B04.md` (includes the reopen record and resolution)
- Corrected context capsule: `capsules/B04.md`
- R1–R4 plus observation/checkpoint provenance regressions pass.
- B05 was closed once, then reopened after direct review found a mismatch between the
  canonical right-arm strokes and the requested broad foreground arm envelope. The
  near/right arm was corrected in an arm-only reopen, independently re-audited, and
  B05 is now CLOSED again. B06 remains inactive.

## B05 closure

- Archived card: `archive/B05.md`
- Context capsule: `capsules/B05.md`
- Subject-only dogfood: `dev/dogfood/vnext-b05/`
- Representative evidence and independent visual review:
  `dev/evidence/vnext/b05/REVIEW.md`
- Construction phase-order enforcement removed; authored mark order is preserved.
- Full repository tests: `90 passed, 5 warnings`.
- Independent native subagent visual audit: all macro criteria `PASS`; `ADVANCE: YES`.

B05's initial whole-figure boundary was reopened only for near/right arm alignment
and is now CLOSED again. No correction, correction memory, additional metadata
ceremony, or B06 runtime lifecycle is active.

R23 is reference-only for vNext. Its artifacts may support historical comparison,
regression, or provenance inspection, but none is vNext PASS evidence. B01 froze
the contract boundary; B02+B03 and B04 provide the closed inspection and session
foundations. No later correction slice is active.
