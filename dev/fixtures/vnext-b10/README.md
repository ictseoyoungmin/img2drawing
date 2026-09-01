# B10 deterministic completion fixture

This mechanical fixture uses synthetic input and the canonical `DrawingSession`. It
records a current finish, proves that a later mark makes it stale, rejects reuse of the
old inspection, records a new finish after fresh inspection, then proves that an intent
change also makes the decision stale. A separate session demonstrates that completion
before inspection is rejected.

```bash
PYTHONPATH=skills/img2drawing/src python3 dev/fixtures/vnext-b10/run.py --output /tmp/vnext-b10
```

The trace proves provenance and stale-state mechanics only. It makes no visual quality or
automatic artistic-completion claim.
