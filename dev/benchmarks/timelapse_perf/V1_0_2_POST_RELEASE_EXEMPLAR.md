# v1.0.2 post-release exemplar benchmark

This report records a post-release performance and exactness check of the **published v1.0.2 code path** using repository-owned exemplar data. It complements the larger `window-study` evidence used during R8; it does not replace that large-session reference.

## Scope

- package/runtime: `img2drawing 1.0.2`
- release/main commit: `6b4a99431bdb402345fd3779cb16ba7ad1648cb7`
- exemplar: `dev/exemplar-sources/p2_axes_v2.json`
- exemplar schema: `img2drawing.grammar_exemplar_source.v1`
- exemplar size: 11,597 bytes
- canvas: 289 × 1086
- actions: 12 `draw_stroke` actions
- runner: GitHub-hosted Ubuntu 24.04.5
- Python: 3.10.21
- FFmpeg: 6.1.1
- fps: 12
- supersample: 4
- frame PNG materialization: disabled

## Input hydration

`p2_axes_v2.json` is an exemplar-source action document, not a serialized vNext session checkpoint. The benchmark therefore creates a fresh v1.0.2 `DrawingSession` and replays each exemplar action through the public drawing path, preserving its points, stroke identity, role, part, confidence, layer, tool, pressure, width, and opacity payload.

The benchmark intentionally does **not** treat `dev/p1_reference_run/run/session/checkpoint.json` as a vNext session. That file identifies itself as `img2drawing.run_checkpoint.v3` and is not a valid `DrawingSession.resume()` input.

## Results

| every_n | frames | cache | render + pack | GIF encode | pipeline | wall |
| ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 4 | 4 | cold | 0.998 s | 0.256 s | 1.254 s | 1.355 s |
| 4 | 4 | warm avg | 0.156 s | 0.078 s | 0.234 s | 0.329 s |
| 2 | 7 | cold | 1.023 s | 0.140 s | 1.162 s | 1.259 s |
| 2 | 7 | warm avg | 0.149 s | 0.082 s | 0.231 s | 0.326 s |
| 1 | 13 | cold | 1.030 s | 0.151 s | 1.180 s | 1.277 s |
| 1 | 13 | warm avg | 0.159 s | 0.087 s | 0.246 s | 0.341 s |

Warm repeats were stable:

- `every_n=4`: pipeline 0.2325 s, 0.2364 s
- `every_n=2`: pipeline 0.2308 s, 0.2314 s
- `every_n=1`: pipeline 0.2460 s, 0.2455 s

## Interpretation

- warm pipeline speedup over cold: approximately **5.35×** (`every_n=4`), **5.03×** (`every_n=2`), and **4.80×** (`every_n=1`)
- render + pack alone improved by roughly **6.4–6.9×** after persistent patch reuse
- output frame count grew from 4 to 13 when moving `every_n=4 → 1` (**3.25×**), while warm internal pipeline time increased only from about 0.234 s to 0.246 s (about **4.8%**)
- on this small 12-action workload, cold stroke-patch generation and first palette creation dominate more than sampled frame count
- warm GIF encoding stabilized around **78–87 ms** after palette reuse

These timings are runner- and workload-specific performance evidence, not API guarantees.

## Exactness gate

Independent canonical and fast final RGB hashes were identical:

```text
canonical  7528508869ed45ff4ce03569af5ccfea606ac79c3a37dd01e1050f5221c4b282
fast       7528508869ed45ff4ce03569af5ccfea606ac79c3a37dd01e1050f5221c4b282
```

Result: **`pixel_exact = true`**.

The independent exactness render cost was approximately 0.969 s and is intentionally excluded from the speed matrix above.

## Repository regression

Before the benchmark step, the repository suite completed with:

```text
253 passed / 3 skipped
```

The benchmark itself completed successfully after FFmpeg was installed on the GitHub-hosted runner.

## Runtime prerequisite note

The GitHub-hosted runner image used for this experiment did not provide FFmpeg by default. v1.0.2's normal session exporter is designed to fail closed to the canonical whole-export path when the fast GIF prerequisite is unavailable. The post-release benchmark installed FFmpeg 6.1.1 explicitly so it could measure the fast encoder path rather than the fallback path.

## Provenance and cleanup

- successful GitHub Actions run: `34327951665`
- temporary benchmark branch used during measurement: `perf/v1.0.2-example-json-bench`
- temporary benchmark commit used by the successful run: `befd6a753ae2920edfda913f3ea3468094f33cc1`
- after measurement, that branch was reset to the v1.0.2 release/main commit so the benchmark harness itself did not become production code

The workflow log is evidence; this report is the durable repository record of the measurements.

## Relationship to the large-session reference

R8's `window-study` remains the large real-session reference:

- 1,272 actions
- 637 frames
- warm patch hit 1227/1227
- render + pack 4.168 s
- GIF encode 2.163 s
- internal pipeline 6.331 s
- bound RenderProfile canonical final RGB pixel-exact

The small exemplar report above is specifically useful for cold/warm cache behavior and `every_n=4/2/1` sampling scaling after release.
