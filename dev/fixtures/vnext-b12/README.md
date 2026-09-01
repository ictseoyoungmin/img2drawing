# B12 deterministic legacy-boundary fixture

This fixture creates a minimal R23 checkpoint, classifies it through the lazy
compatibility namespace, migrates its shared action/history truth into a vNext
checkpoint, and verifies that the migrated checkpoint resumes without loading R23.

```bash
PYTHONPATH=skills/img2drawing/src python3 dev/fixtures/vnext-b12/run.py --output /tmp/vnext-b12
```

The trace records checkpoint, subject, action, stage-free state, and renderer
provenance. It is mechanical compatibility evidence, not visual dogfood.
