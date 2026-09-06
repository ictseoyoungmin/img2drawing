# S05 — Forward history traversal and frame-I/O profiling

State: **CLOSED AS A DEV PROTOTYPE / EVIDENCE SLICE**

Production runtime behavior is unchanged. S05 measures the two largest non-render costs that remained after S03/S04: repeated historical-state reconstruction and frame artifact I/O.

## Historical state traversal

The canonical exporter currently calls `history.state_at(cursor)` independently for every sampled frame. `state_at()` replays actions from zero and deep-copies the active strokes into a new `StrokeIR`, so an every-N timelapse repeats history work even after renderer material work has been cached.

S05 adds `ForwardHistoryReplay`, a forward-only dev cursor that mirrors `CanvasHistory.state_at()` semantics but applies each action once. Sampled `StrokeIR` views borrow immutable replay-state stroke objects; later edit actions replace/deep-copy objects rather than mutating older versions, so earlier sampled views remain stable.

Exact Lucy workload (`546` actions, `every_n=4`, `138` sampled cursors):

```text
repeated history.state_at()       12.3776 s
forward zero-copy snapshots        0.1276 s
speedup                            97.02x
sampled-state parity               138 / 138 exact
```

A separate copied-snapshot prototype measured 3.87 s, confirming that deep-copying the full active drawing at every sampled cursor is itself substantial even after replay traversal is made incremental.

## Frame artifact I/O

S05 also profiles 41 real Lucy prefix-160 frames at the same 941x1672 output resolution produced by the S03 path.

```text
PNG bytes total                   9,408,776
PNG save/compression              2.3989 s
pixel SHA-256 (decode + RGBA)     1.1106 s
byte SHA-256                      0.0071 s
per-frame JSON writes             0.0018 s
GIF encode                        3.8257 s
measured artifact work total      7.3440 s
```

The result sharpens the earlier conclusion: per-frame JSON is undesirable artifact structure but is not a performance bottleneck. PNG compression, GIF encoding, and pixel hashing dominate artifact-side cost.

A simple linear projection from 41 to 138 frames would be roughly 24.7 s of artifact work at this content/compressibility. That projection is directional only; GIF palette behavior and later-frame complexity are not perfectly linear.

## Decision

Carry forward:

1. a forward-only authoritative history iterator for export/replay;
2. zero-copy sampled `StrokeIR` views when the consumer is read-only;
3. existing exact S02/S03/S04 renderer/cache/compositor semantics.

Do not optimize:

- per-frame JSON for speed; clean it later for artifact hygiene;
- byte hashing; it is negligible.

Next performance work should target frame delivery rather than more history math: avoid reopening PNGs for pixel hashes, avoid retaining/re-reading all PNG frames solely for GIF assembly, and provide a streaming/optional-frame-spool export path. Edit invalidation remains required before S04-style incremental composition can cover Lucy actions 394–546.

## Validation

- `test_s05_forward_history.py`: add / replace / soft-lift / delete parity against `CanvasHistory.state_at()`.
- real Lucy: all 138 sampled `StrokeIR.to_dict()` values exactly match canonical `state_at()`.
- backward seek fails closed by design in the dev cursor.
