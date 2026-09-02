# Migration from R23

New sessions should use `DrawingSession`. Do not translate Pn progress, reviews, reopen
state, or historical PASS claims into vNext authority.

Inspect or migrate an old checkpoint through the explicit boundary:

```python
from img2drawing.legacy.r23 import inspect_checkpoint, migrate_checkpoint

info = inspect_checkpoint("old-run/session/checkpoint.json")
session = migrate_checkpoint(
    "old-run/session/checkpoint.json",
    output_dir="migrated-vnext-run",
)
```

The migration preserves shared action/history truth and provenance while leaving stage
lifecycle facts historical. Inspect the migrated current drawing, declare current intent,
and establish fresh completion evidence. Full compatibility details are in
`references/legacy-r23.md`.
