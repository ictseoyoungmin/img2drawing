# S02 — Deterministic StrokeRasterCache prototype

State: **CLOSED AS A DEV PROTOTYPE**

Production runtime behavior is unchanged. The prototype lives entirely under
`dev/benchmarks/timelapse_perf/` and imports the exact private material functions used by
`pillow-pencil-contact-v9` so parity can be tested before any runtime integration decision.

## Question

Can one expensive stroke materialization be reused across historical timelapse frames without
changing the canonical renderer family, supersample, authored geometry, or final pixels?

## Prototype contract

Cache key includes:

- complete authored `Stroke` content (geometry, pressure, material/tool state, layer, stable id),
- renderer id/version,
- supersampled factor and high-resolution canvas size,
- paper tooth / scale / seed,
- graphite RGB,
- pencil grade and contact-profile identity.

Cache value is a cropped **8-bit final contact alpha mask** plus its global high-resolution bounds.
The mask is the result after the exact canonical sequence:

```text
prepare grade
→ smooth hand dynamics
→ continuous contact mask
→ continuity floor
→ graphite grain
→ paper modulation
→ final continuity merge
```

Composition recreates the constant graphite RGBA tile from that mask and uses the same Pillow
`alpha_composite` order as the canonical renderer. Delete history requires no special operation
because a deleted stroke is absent from the requested IR. A replacement with stable stroke identity
but changed content generates a different key. Ordered eraser strokes remain uncached/destructive;
the S02 regression and supplied Lucy workload contain no active eraser strokes.

S02 deliberately does **not** retain/reuse the accumulated full canvas between frames. That is the
next compositor slice.

## Representative 48-action evidence

Workload remains the S00 contract:

- 1024×1536 logical output
- supersample 4 for canonical-quality evidence
- 48 strokes
- every_n=4
- 13 sampled frames
- one independent final render after the sampled final frame

### Exact parity

At ss2, all 13 sampled frames were rendered by both paths in one A/B run and every RGBA pixel hash
matched. The independent cached final also matched its last cached frame.

At ss4, parity was independently checked at cursors 0, 16, 32, and 48; every cached PNG matched the
canonical PNG exactly. The cached independent final is also byte-for-byte identical to the frozen
S00 final:

- PNG SHA-256: `22a6b132a193f1b2b69f16488003e609024f70d68bf07af5520006f0d633def4`
- RGBA pixel SHA-256: `63f8cdee6023b0eeae5cff2ccfbb108cd41ae12cd61f29a1ac3a0bcbafb80c0f`

### Materialization reduction

For the current 14-render-call exporter shape:

```text
material passes requested      360
cache misses / materializations 48
cache hits                      312
hit rate                        86.67%
```

The cache therefore reduces expensive materialization from 360 passes to one pass per distinct
stroke content while leaving frame composition untouched.

### Same-resolution timing

Frozen S00 ss4/every_n=4 canonical exporter mean: **57.4621 s** (two runs, 1.70% spread).

S02 ss4/every_n=4 cached path, including 13 frames, the independent-final render, and GIF encoding:

```text
sampled-frame render total     13.7051 s
independent final               0.6463 s
GIF encode                      1.2160 s
wall time                      15.9345 s
```

Against the frozen S00 workload this is approximately **3.61× wall-time speedup** without changing
output resolution or supersample. The purpose of this number is to validate the cache premise; it
is not yet a production performance claim because the prototype remains outside runtime.

### Memory representation

A naive first prototype retained cropped RGBA stroke tiles:

- representative ss4 cache: about **57.2 MB**.

S02 was tightened to cache only the 8-bit final material mask:

- representative ss4 cache: **14.29 MB**,
- same pixels,
- same cache hits/misses.

This is the representation carried forward from S02.

## Exact Lucy-546 projection and partial parity

The supplied Lucy session has:

- 941×1672 output,
- ss4,
- 546 actions,
- 138 sampled frames at every_n=4,
- 392 final active strokes,
- 35,116 stroke material passes under the current exporter shape.

Content-key analysis across all sampled states plus the independent final yields:

```text
distinct cacheable stroke versions   541
cache hits                         34,575
cache misses                          541
projected hit rate                  98.46%
material-pass / cache-entry ratio   64.91×
projected mask cache footprint      78.98 MB
naive RGBA equivalent              315.91 MB
```

The 541 entries exceed the 397 stable stroke identities because replacement history can expose
multiple distinct versions of one identity. This validates content-addressing rather than using
`stroke_id` alone as the cache key.

Exact Lucy parity was spot-checked with real ss4 canonical renders while warming one persistent
cache: cursor 20 and cursor 40 both matched pixel-for-pixel. At cursor 40, after the first 20 strokes
were already cached, the cached render was materially faster than rerunning canonical material for
all 40 strokes.

A full 138-frame Lucy cache-only replay was intentionally **not** accepted as S02 closure: even after
material reuse, repeatedly rebuilding/downsampling the complete ss4 canvas remains expensive. A
trial did not finish within the bounded benchmark window. That is evidence for S04 incremental
canvas/dirty-region composition, not a failure of stroke-raster reuse.

## Decision

**S02 premise passes.** The cache is visually exact and substantially reduces repeated material
work on the representative workload. The real Lucy history projects to a 98%+ cache-hit rate with a
reasonable mask-only working set, but also demonstrates that stroke caching alone is insufficient
for long ss4 timelapses because full-canvas recomposition remains.

Therefore:

1. keep `StrokeRasterCache` as a proven prototype/evidence boundary;
2. do not replace the canonical renderer or reduce supersample;
3. do not merge this private-function prototype directly into public runtime yet;
4. **next bottleneck: S04 incremental add-only compositor**, then edit invalidation;
5. defer S03 paper-field cache until after S04 profiling — cached masks already avoid paper-field
   recomputation on hits, so paper caching may have less incremental value than originally assumed.
