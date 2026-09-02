# B14 deterministic drawing-mode fixture

This fixture resolves and exercises `croquis`, `figure_drawing`, `tonal_study`,
`line_study`, and `free_draw` through the same `DrawingSession`, history, inspection,
render, checkpoint, and resume implementation. It also runs free-draw under observed,
imaginative, and hybrid reference authority.

```bash
PYTHONPATH=skills/img2drawing/src python3 dev/fixtures/vnext-b14/run.py --output /tmp/vnext-b14
```

Tonal study authors one `fill_region` value decision. The trace checks mechanical mode
resolution and shared-core continuity only; it makes no visual-quality claim.
