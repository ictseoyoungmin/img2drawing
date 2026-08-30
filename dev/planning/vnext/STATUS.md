# img2drawing vNext status

Updated: 2026-08-30

```text
SYSTEM:   architecture contract frozen / session provenance hardening
ACTIVE:   B04 REOPENED — inspection evidence + provenance hardening
SKELETON: B05 construction grammar; B06 correction loop;
          B07–B18 remaining slices
CLOSED:   B00 Legacy R23 freeze + failure dossier; B01 vNext contract and architecture cut;
          B02+B03 Inspection Foundation
NEXT GATE: close B04 R1–R4 plus observation/checkpoint provenance regressions;
           do not activate B05
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
- B04 was CLOSED, then REOPENED for artifact-level provenance hardening. The
  reopened scope is limited to immutable repeated inspection evidence, failed-
  checkpoint artifact rollback, observation-ID integrity, and custom checkpoint
  path metadata.
- B05 construction grammar and later correction/runtime lifecycle work remain inactive.

## B04 reopened

- Prior closed card: `archive/B04.md`
- Prior capsule remains the pre-reopen context; it is superseded only after
  re-closure.
- Active reopen record: `active/B04.md`
- B05 is not activated.

R23 is reference-only for vNext. Its artifacts may support historical comparison,
regression, or provenance inspection, but none is vNext PASS evidence. B01 froze
the contract boundary; B02+B03 remains closed while B04 is being hardened. No
later construction/correction slice is active.
