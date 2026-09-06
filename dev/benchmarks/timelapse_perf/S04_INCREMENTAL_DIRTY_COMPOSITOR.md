# S04 — Incremental dirty-region timelapse compositor

State: **CLOSED AS A DEV PROTOTYPE**

Production runtime remains unchanged. S04 extends the S02 mask cache with a persistent supersampled graphite canvas and a persistent native-resolution output canvas. Forward add-only replay composites only newly visible cached strokes, and each sampled frame recomputes only the native-resolution rectangle that can be influenced by those new high-resolution marks.

## Why S04 was reopened during implementation

The first persistent-canvas prototype still performed a full 4x→1x Lanczos resize for every frame. On the 48-action representative fixture it was effectively no faster than S02: the expensive per-stroke material work had already been removed, leaving full-canvas snapshot/downsample as the dominant residual.

S04 was therefore narrowed to the actual bottleneck: **dirty output resampling**, not merely persistent high-resolution composition.

## Exact dirty-resample contract

For every batch of newly composited strokes:

1. union the changed supersampled stroke bounds;
2. expand to the logical output pixels whose Lanczos support can intersect that change;
3. add an extra aligned sampling halo;
4. crop only that high-resolution source rectangle;
5. composite it over the canonical background;
6. downsample the aligned outer patch with the same Pillow Lanczos filter;
7. crop the inner dirty logical rectangle and paste it into a persistent native-resolution output canvas.

The implementation keeps two halos because the first expands the set of output pixels affected by a high-resolution change, while the second prevents the local resize from seeing an artificial crop boundary.

## Representative evidence

Same frozen S00/S02 workload:

- 1024×1536 output
- ss4
- 48 add-only actions
- every_n=4
- 13 frames

Results:

```text
S00 canonical full replay mean       57.4621 s
S02 cached full recomposition        14.4970 s
S04 incremental + dirty resize       8.0163 s  (includes GIF encode)

S04 vs S02                            2.108x
S04 vs frozen S00                     7.168x
```

All 13 frame RGBA pixel hashes are exactly identical to S02 cached full recomposition, including the final frame.

Dirty logical pixels resampled across the entire 13-frame replay:

```text
actual dirty output pixels          965,084
full output pixels if every frame   20,447,232
dirty fraction                      4.72%
```

So the representative replay avoids about **95.28%** of full-frame logical resampling work while preserving exact pixels.

The persistent ss4 graphite canvas itself is about **100.66 MB**. That memory cost is accepted only for prototype evidence and must be redesigned/bounded before production integration.

## Lucy add-only prefix evidence

The real Lucy-546 session is add-only through cursor 393; the first replacement occurs at action 394. This gives a large real prefix for S04 without inventing edit semantics.

At 941×1672 / ss4 / every_n=4:

### Prefix 80

```text
frames                  21
wall                     17.7615 s
materialize              14.2548 s
snapshot                  2.5601 s
dirty fraction            10.61%
```

### Prefix 160

```text
frames                  41
wall                     21.5743 s
materialize              15.1189 s
snapshot                  4.1439 s
dirty fraction            7.03%
spot parity                cursor 0/80/160 exact
```

The 160-action run shows the key post-S04 shift: dirty snapshot cost falls to about 4.14 s total while one-time materialization remains about 15.12 s. A bounded attempt to continue the full add-only prefix to cursor 393 exceeded 120 seconds and reached cursor 304. The remaining cost is no longer repeated full-frame resampling; it is dominated by first-time materialization of many real Lucy strokes plus artifact I/O.

## Decision

**S04 dirty-resample premise passes.** The original persistent-canvas-only variant did not. The reopened dirty-resample variant is exact and materially faster.

Carry forward:

- S02 content-addressed 8-bit stroke masks;
- persistent forward canvas state;
- aligned dirty output resampling;
- fail closed when history is not an append-only extension.

Do not integrate into production yet because:

- replace/delete/soft-lift invalidation is not implemented;
- the persistent ss4 RGBA canvas is ~100 MB at this resolution;
- real Lucy prefixes now show unique-stroke materialization as the larger residual.

### Next bottleneck

Revisit **S03 paper/material field caching** now that S04 has removed most repeated snapshot cost. After that, proceed to replace/delete dirty invalidation.
