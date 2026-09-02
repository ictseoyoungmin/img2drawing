# Evidence package

Keep the smallest reproducible package that supports direct review:

```text
evidence/
  sealed_input.json
  input.sha256
  session/session.checkpoint.json
  inspections/initial/...
  inspections/representative-before-after/...
  output/canonical_final.png
  output/replay_manifest.json
  output/timelapse.gif
  decision-log.md
  cost-inventory.json
  independent-review.json
```

The decision log records concise observation and residual choices; it is produced during
the run and is never fed into another fresh worker. Preserve representative evidence, not
every scratch render. Keep evaluator conclusions out of the worker input. Record known
limitations and rejected claims explicitly.
