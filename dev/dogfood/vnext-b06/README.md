# B06 residual correction dogfood

This fixture reuses the accepted B05 subject-only construction and exercises the
stage-free correction loop through the real `DrawingSession` and `InspectionSheet`
boundary. It seeds one deliberately over-vertical near-arm premise, records that
current residual, restores the bent foreground premise, and then performs a bounded
cross-contour segment repair. The Agent's `keep` decisions are persisted and resumed;
there is no stage transition or automatic visual score.

Run from the repository root:

```bash
PYTHONPATH=skills/img2drawing/src python3 dev/dogfood/vnext-b06/run.py --output /tmp/img2drawing-b06
```

The output contains four immutable inspection directories and
`b06_correction_trace.json`, which records the residual IDs, before/after inspection
digests, action provenance, and resumed correction memory. Compare the `000002` and
`000003` inspection sheets directly: the over-vertical arm premise is removed and the
bent near-arm overlap returns. `000004` is the follow-up local contour inspection.

The fixture is intentionally an evidence harness, not a final drawing. B06 acceptance
is the explicit inspect → residual → edit → inspect provenance and the Agent's visual
decision, not edit count or a runtime quality metric.
