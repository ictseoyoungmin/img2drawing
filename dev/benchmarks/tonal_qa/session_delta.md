# Real-session tonal QA

This is developer-only diagnosis, not a new drawing backend or a release-quality judge.
It re-renders cursor 0, the selected before cursor, and the after cursor with the session's
persisted RenderProfile. It collects explicitly authored TonalAreaPlan metadata from one
current IR snapshot, verifies its digests, rejects conflicting live plans, and measures
paper-relative darkness inside the target and reserved highlight polygons. It reports
added/removed darkness, protected-area coverage, saturation, and interval-wide outside-area
change. The latter is not causal attribution: use an interval containing only the group
under review if investigating leakage. Current plans are not historical plan snapshots.
Target density/value are artistic intent, not calibrated luminance thresholds.

Run with the candidate package installed and the original reference available locally:

```sh
python dev/benchmarks/tonal_qa/session_delta.py \
  --session path/to/session.checkpoint.json --subject path/to/reference.png \
  --before 87 --after 192 --out path/to/diagnostic.json
```

Optional repeatable --area selects specific live plan IDs. The tool does not draw, trace,
modify history, auto-generate marks, or assign visual PASS. User references and subject-specific
authored coordinates stay outside the public repository. See the independent QA gates in
the release plan; these metrics can diagnose failures but cannot certify likeness.
