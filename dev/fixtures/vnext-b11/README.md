# B11 deterministic render/replay fixture

This synthetic fixture authors strokes and one broad value region in a single vNext
history, then exports cursor 0 through latest as PNG frames, an independently rendered
canonical final PNG, and a GIF using one persisted `RenderProfile`.

```bash
PYTHONPATH=skills/img2drawing/src python3 dev/fixtures/vnext-b11/run.py --output /tmp/vnext-b11
```

The manifest records exact PNG parity, documented GIF color tolerance, cursor/timing
semantics, action count, profile digest, and pixel-work cost. It is mechanical evidence,
not visual dogfood.
