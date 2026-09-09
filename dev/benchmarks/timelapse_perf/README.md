# Timelapse performance baseline (S00–S01)

This benchmark freezes the current canonical `pillow-pencil-contact-v9` replay cost before cache work.
It is deliberately **outside runtime**: instrumentation observes the current renderer/exporter and must not change renderer output or persisted session state.

## S00 baseline contract

- fixed representative output resolution: `1024×1536` (1,572,864 px; essentially the same pixel count as the 941×1672 Lucy workload),
- canonical renderer family,
- supersample `4`,
- `every_n=4`, including action zero and final cursor,
- repeated representative runs,
- final standalone PNG must be pixel-identical to replay canonical final,
- repeat final PNG pixels must be identical.

The deterministic 48-stroke fixture generator is intentionally compact enough for repeated manual benchmarking; the large generated JSON does not need to be committed. Subject-specific sessions are **not** committed as product knowledge. A local existing vNext session can be analyzed without copying its geometry into the repository.

## S01 duplicate-work instrumentation

`analyze_duplicate_work.py` derives material-pass exposure from the authoritative historical states passed to the canonical renderer. The renderer performs one material pass for every active stroke in every full render call, so this measures repeated unchanged-stroke work without changing runtime behavior.

Representative fixture:

```bash
PYTHONPATH=src python dev/benchmarks/timelapse_perf/analyze_duplicate_work.py \
  --out /tmp/img2drawing-duplicate-work.json
```

Existing local session/checkpoint:

```bash
PYTHONPATH=src python dev/benchmarks/timelapse_perf/analyze_duplicate_work.py \
  --session /path/to/session.json \
  --every-n 4 \
  --out /tmp/session-duplicate-work.json
```

The session path must keep its referenced subject and inspection artifacts beside it so `DrawingSession.resume()` can validate provenance.

## Baseline render smoke

```bash
# Optional: materialize the deterministic JSON fixture for inspection.
python dev/benchmarks/timelapse_perf/make_fixture.py
PYTHONPATH=src python dev/benchmarks/timelapse_perf/run_baseline.py \
  --out /tmp/img2drawing-timelapse-baseline \
  --supersample 4 --every-n 4 --repeat 2
```

For a quick development smoke, use `--supersample 2 --repeat 1`.

Artifacts include:

- `baseline.json`
- `run_*/metrics.json`
- final PNG
- canonical timelapse GIF / replay manifest / frames

Fast regression:

```bash
PYTHONPATH=src pytest -q dev/benchmarks/timelapse_perf/test_duplicate_work.py
```

The expensive ss4 wall-time benchmark should remain a manual/performance job rather than a normal per-commit CI requirement.

S02 must not begin unless S00 parity is green and S01 confirms material duplicate work.

## S02 stroke-raster cache prototype

S02 keeps the production renderer untouched and prototypes deterministic reuse of the expensive
per-stroke `pillow-pencil-contact-v9` material result:

```bash
PYTHONPATH=src python dev/benchmarks/timelapse_perf/run_s02_cache.py \
  --out /tmp/img2drawing-s02 \
  --supersample 4 --every-n 4 --gif
```

For an exact compact A/B including every frame and the current independent-final render contract:

```bash
PYTHONPATH=src python dev/benchmarks/timelapse_perf/run_s02_cache.py \
  --out /tmp/img2drawing-s02-ss2 \
  --supersample 2 --every-n 4 --baseline --gif
```

The cache stores the final **8-bit paper/grain/contact alpha mask** for each distinct stroke content
and renderer/profile state, not a four-channel RGBA tile. Graphite RGB is reattached during
composition. This cut the representative ss4 cache footprint from about 57 MB for the naive RGBA
prototype to about 14 MB while preserving exact pixels.

S02 still rebuilds the high-resolution canvas for every sampled frame. That is deliberate: canvas
state reuse / dirty-region composition is S04+. The prototype therefore isolates the value of
avoiding repeated materialization from later compositor work.

Fast regression:

```bash
PYTHONPATH=src pytest -q dev/benchmarks/timelapse_perf/test_s02_cache.py
```

## S04 incremental dirty-region compositor prototype

S04 keeps S02's exact 8-bit material cache and adds a persistent supersampled graphite canvas. The
first version only reused that high-resolution canvas and still performed a full 4x→1x resize for
every frame; it showed essentially no speedup over S02. The reopened S04 therefore updates only the
native-resolution rectangle influenced by newly added high-resolution marks, with aligned Lanczos
halos to preserve exact pixels.

Representative ss4 A/B:

```bash
PYTHONPATH=src python dev/benchmarks/timelapse_perf/run_s04_incremental.py \
  --out /tmp/img2drawing-s04 \
  --supersample 4 --every-n 4 --s02-baseline --gif
```

Fast exact regression:

```bash
PYTHONPATH=src pytest -q dev/benchmarks/timelapse_perf/test_s04_incremental.py
```

S04 is add-only and fails closed when the requested IR is not an append-only extension. It does not
implement replace/delete/soft-lift invalidation and remains a dev prototype rather than production
runtime. The representative result is 8.0163 s including GIF encode versus 14.4970 s for S02 cached
full recomposition and 57.4621 s for the frozen S00 canonical baseline, with all 13 frame pixel
hashes identical. See `S04_INCREMENTAL_DIRTY_COMPOSITOR.md` for the real Lucy-prefix evidence and
remaining memory/materialization bottlenecks.

## S03 exact material-field kernel prototype

After S04, first-time grain/paper materialization became the largest measured add-only cost. S03
profiles that cost and narrows the original paper-tile-cache idea: a large persistent page-field
cache is workload-sensitive and memory-heavy, so the accepted prototype instead computes the same
deterministic value-noise fields from separable 1-D coordinate bases plus broadcasting.

Representative ss4 A/B:

```bash
PYTHONPATH=src python dev/benchmarks/timelapse_perf/run_s03_material_kernel.py \
  --out /tmp/img2drawing-s03 \
  --supersample 4 --every-n 4 --gif
```

Fast exact regression:

```bash
PYTHONPATH=src pytest -q dev/benchmarks/timelapse_perf/test_s03_material_kernel.py
```

The accepted S03 kernel adds no persistent page-field cache, preserves exact grain/paper equations,
and leaves all representative and Lucy-prefix pixels unchanged. On a fresh representative run it
reduced first-time materialization from 5.0122 s to 2.8430 s and total replay+GIF wall time from
7.4427 s to 5.3481 s. Lucy prefix 160 materialization dropped from 15.1189 s to 7.7700 s with all
41 frames pixel-identical to S04. See `S03_MATERIAL_FIELD_KERNEL.md` for the cache-hypothesis reopen,
final-active Lucy evidence, and the next bottleneck boundary.

## v1.0.2 production and post-release evidence

S00–S05 above are historical development prototypes. The production v1.0.2 implementation was
integrated independently through the local-first R8 path and is not defined by importing those
prototype modules.

The durable post-release measurement record is:

- [`V1_0_2_POST_RELEASE_EXEMPLAR.md`](V1_0_2_POST_RELEASE_EXEMPLAR.md) — repository exemplar,
  cold/warm `every_n=4/2/1`, render/pack vs GIF encode split, exactness hash, GitHub Actions
  provenance, FFmpeg prerequisite, and compatibility notes.

The large-session scale reference remains the 1,272-action `window-study`: 637 frames, warm
render+pack 4.168 s, GIF encode 2.163 s, internal pipeline 6.331 s, and an RGB pixel-exact final
against the bound RenderProfile.

Performance numbers in this directory are evidence tied to their recorded environment and workload;
they are not API latency guarantees.
