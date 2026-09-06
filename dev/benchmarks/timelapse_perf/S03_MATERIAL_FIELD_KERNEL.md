# S03 — Exact material-field kernel optimization

State: **CLOSED AS A DEV PROTOTYPE**

Production runtime behavior is unchanged. S03 reopens the original "paper-field cache" idea after profiling showed that a bounded page-tile cache can reduce paper recomputation but costs substantial memory and is workload-sensitive. The accepted prototype instead preserves the exact v9 material equations while replacing eager 2-D coordinate-grid construction with separable 1-D coordinate bases plus NumPy broadcasting.

## Why S03 reopened after S04

S04 removed most repeated full-canvas work. On the real Lucy add-only prefix, first-time stroke materialization became larger than dirty snapshots. Profiling the final active Lucy drawing at 941×1672 / ss4 showed:

- 392 active strokes,
- profiled first-time material stages: 17.3667 s,
- grain modulation: 5.6183 s,
- paper modulation: 10.0734 s,
- grain + paper: **90.35%** of profiled material time,
- `paper_field()` alone: 9.7572 s, or **96.86%** of paper-modulation time.

This made deterministic field generation the correct next bottleneck.

## Reopened cache hypothesis

A 512×512 float32 paper-field tile cache with a 96 MB cap was tested on Lucy prefix 160. It reduced repeated paper-field generation, but retained about 71.3 MB of page tiles. The stronger combined kernel+tile variant reached 4.96 s first-time materialization versus 13.46 s baseline, but the same tile strategy was slightly slower than kernel-only on the sparse representative workload and added ~81.8 MB there because generated tile area exceeded requested stroke area.

Therefore the page-tile cache is **not** carried forward as the default S03 implementation. It remains evidence that page-fixed fields are cacheable, but the memory/performance tradeoff is too workload-dependent for production integration at this point.

## Accepted prototype

`material_field_kernel.py` keeps canonical value-noise/hash math but exploits raster-grid separability:

```text
legacy
  np.indices(H, W)
  -> full 2-D x/y coordinate arrays
  -> value noise

S03
  1-D x coordinate basis
  1-D y coordinate basis
  -> broadcast only where 2-D hash/noise is required
```

The same approach is used for grain coarse/fine fields, paper coarse/mid/fine fields, and anisotropic paper fibre fields. No random source, seed, cell size, modulation equation, clipping rule, pressure rule, or renderer profile changes.

## Exactness

Standalone paper-field crops are `np.array_equal` to the canonical field.

The representative 48-action replay at 1024×1536 / ss4 / every_n=4 produced all 13 frame RGBA hashes exactly equal to the S04 path.

Lucy prefix 160 produced all **41/41** frames pixel-identical to the previously validated S04 frames.

A final-state material A/B over all 392 active Lucy strokes produced exact cached-mask hashes for every stroke.

## Representative timing

Fresh bounded run, same 1024×1536 / ss4 / 48-action / every_n=4 contract, GIF included:

```text
S04 material cache + dirty compositor
  wall             7.4427 s
  materialize      5.0122 s

S03 exact field kernel + S04 compositor
  wall             5.3481 s
  materialize      2.8430 s
```

Speedup:

- wall: **1.392×**
- first-time materialization: **1.763×**

The mask-cache footprint remains exactly 14,293,878 bytes; S03 kernel-only adds no long-lived page-field cache.

## Lucy evidence

### Prefix 160

Previous S04 evidence:

- wall: 21.5743 s
- materialize: 15.1189 s
- snapshots: 4.1439 s

S03 kernel:

- wall: 15.0073 s
- materialize: 7.7700 s
- snapshots: 4.0873 s
- all 41 frame pixels match S04

Speedup:

- wall: **1.438×**
- materialization: **1.946×**

### Final active material set

At cursor 546, 392 active strokes:

- canonical/S02 first-time materialization: 17.2058 s
- S03 kernel: 10.1257 s
- speedup: **1.699×**
- exact mask parity for all 392 strokes

### Long prefix boundary

A bounded cursor-393 run with S03 reached cursor 380 before the 120 s wall limit; the S04 attempt had reached cursor 304 in the same bounded class of experiment. This is directional evidence only, not a release claim. The remaining long-session cost now includes repeated `state_at()` reconstruction and frame artifact I/O in addition to first-time materialization.

## Decision

**S03 premise passes, with the cache-first hypothesis narrowed.**

Carry forward:

1. exact separable material-field kernels;
2. S02 content-addressed 8-bit stroke masks;
3. S04 incremental dirty-region output updates.

Do not yet carry forward:

- a large persistent paper-field tile cache,
- production runtime integration,
- edit invalidation changes.

The next bottleneck should be measured between historical-state reconstruction / replay cursor traversal, frame artifact I/O / GIF streaming, and replace/delete/soft-lift dirty invalidation.

Production integration should still wait until edit semantics and memory bounds are proven together.
