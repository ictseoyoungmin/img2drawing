# img2drawing vNext status

Updated: 2026-08-30

```text
SYSTEM:   architecture sketched / B01 contract cut in progress
ACTIVE:   B01 vNext contract and architecture cut
SKELETON: B01 contract cut; B02+B03 inspection foundation; B04 session;
          B05 construction grammar; B06 correction loop; B07–B18 remaining slices
CLOSED:   B00 Legacy R23 freeze + failure dossier
NEXT GATE: complete B01 dependency audit and freeze the stage-free contract
```

## B00 closure

- Frozen legacy baseline: `25ec454`
- Baseline verifier: `dev/planning/vnext/verify_baseline.py`
- Failure dossier: `failure-dossier/gemini.md`, `failure-dossier/claude.md`,
  `failure-dossier/r23-architecture.md`
- Context capsule: `capsules/B00.md`
- Archived card: `archive/B00.md`

R23 is reference-only for vNext. Its artifacts may support historical comparison,
regression, or provenance inspection, but none is vNext PASS evidence. B01 is the
only active production slice; no Inspection Foundation, DrawingSession, or runtime
implementation work is included in this activation.
