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
