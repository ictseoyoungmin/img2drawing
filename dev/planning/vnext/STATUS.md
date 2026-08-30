# img2drawing vNext status

Updated: 2026-08-30

```text
SYSTEM:   architecture contract frozen / session foundation closed
ACTIVE:   none — B04 CLOSED; no next production slice activated
SKELETON: B05 construction grammar; B06 correction loop;
          B07–B18 remaining slices
CLOSED:   B00 Legacy R23 freeze + failure dossier; B01 vNext contract and architecture cut;
          B02+B03 Inspection Foundation; B04 stage-agnostic DrawingSession
NEXT GATE: manually activate B05 only after reviewing the corrected B04 capsule;
           do not activate B05 automatically
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
- B05 construction grammar and later correction/runtime lifecycle work remain inactive.

## B04 closure after reopen

- Archived card: `archive/B04.md` (includes the reopen record and resolution)
- Corrected context capsule: `capsules/B04.md`
- R1–R4 plus observation/checkpoint provenance regressions pass.
- B05 is not activated automatically.

R23 is reference-only for vNext. Its artifacts may support historical comparison,
regression, or provenance inspection, but none is vNext PASS evidence. B01 froze
the contract boundary; B02+B03 and B04 provide the closed inspection and session
foundations. No later construction/correction slice is active.
