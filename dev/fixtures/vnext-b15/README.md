# B15 deterministic style-authoring fixture

This fixture authors identical geometry under the three retained style identifiers and
proves that selection alone changes neither geometry nor `RenderProfile`. It also records
a mid-session style change followed by one explicit stroke replacement, and round-trips
one complete structured custom guide.

```bash
PYTHONPATH=skills/img2drawing/src python3 dev/fixtures/vnext-b15/run.py --output /tmp/vnext-b15
```

The fixture verifies authoring-policy mechanics and provenance only. It does not claim
that a preset has achieved broad visual style quality.
