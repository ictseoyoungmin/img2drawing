# B16 deterministic authoring/editing fixture

This fixture locates authored strokes and fills by responsibility/provenance, follows a
whole-stroke replacement, revises a stable fill, binds an explicit correction, rejects a
stale edit atomically, produces a bounded derived summary, and resumes the same history.

```bash
PYTHONPATH=skills/img2drawing/src python3 dev/fixtures/vnext-b16/run.py --output /tmp/vnext-b16
```

Generated fill contacts are excluded from authored-element counts. This is mechanical
navigation/edit evidence, not automatic edit planning or visual-quality certification.
