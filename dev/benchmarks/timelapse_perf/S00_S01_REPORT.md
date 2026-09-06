# S00–S01 — Timelapse baseline + duplicate-work instrumentation

## Verdict

- **S00 representative baseline harness: CLOSED**
- **S00 exact Lucy-546 workload characterization: CLOSED**
- **S00 exact Lucy-546 full ss4/every_n=4 wall-time run: intentionally not executed** because S01 now proves the exporter would perform 139 full renders and 35,116 stroke material passes; forcing that pathological pre-cache run adds little information beyond the already frozen representative timing.
- **S01 duplicate-work instrumentation: CLOSED**
- Runtime behavior is unchanged in this slice. All additions live under `dev/benchmarks/timelapse_perf/`.

The user-supplied `lucy-croquis-source(1).zip` contains the exact `941×1672`, 546-action canonical vNext session. Its subject-specific geometry is not copied into repository fixtures. The benchmark now accepts a local `--session` path and records aggregate performance structure only.

## S00 frozen representative baseline

Configuration:

- renderer: `pillow-pencil-contact-v9`
- output resolution: `1024×1536`
- supersample: `4`
- authored strokes/actions: `48`
- sampling: `every_n=4`
- sampled frames: `13` (`0,4,...,48`)
- exporter performs one extra independent final render after the final sampled frame

Two completed diagnostic runs from the same frozen renderer/fixture produced:

| run | timelapse wall time |
|---|---:|
| with explicit GC after frames | 57.9504 s |
| no explicit GC | 56.9738 s |
| mean | **57.4621 s** |
| spread / mean | **1.70%** |

A fresh standalone final render in the benchmark workspace took **6.9861 s**. Its file SHA-256 and pixel SHA-256 exactly match the completed replay canonical final:

- PNG SHA-256: `22a6b132a193f1b2b69f16488003e609024f70d68bf07af5520006f0d633def4`
- RGBA pixel SHA-256: `63f8cdee6023b0eeae5cff2ccfbb108cd41ae12cd61f29a1ac3a0bcbafb80c0f`

The completed replay's last sampled frame is byte-identical to its independently rendered `canonical_final.png`.

## Exact Lucy-546 local workload characterization

The supplied session was resumed with the current v1.0.1 runtime and analyzed at its stored canonical profile:

- output resolution: **941×1672**
- supersample: **4**
- authored actions: **546**
  - `stroke.add`: 397
  - `stroke.replace`: 144
  - `stroke.delete`: 5
- `every_n=4` sampled frames: **138**
- final active strokes: **392**
- unique stroke identities observed across replay: **397**
- sampled-frame material passes: **34,724**
- extra independent-final material passes: **392**
- total material passes: **35,116**
- duplicate passes beyond one pass per unique stroke: **34,719**
- average material-pass duplication factor: **88.4534×**
- actual full render calls: **139**
- manifest pixel-work: **3,473,961,216** supersampled pixels
- pixel-work including duplicate final: **3,499,134,848** supersampled pixels

The earliest four persistent strokes are each materialized **138 times**.

A single standalone canonical final render of the supplied Lucy session completed in **21.1629 s** and reproduced the supplied final PNG byte-for-byte:

- PNG SHA-256: `0f655cabd1bd72ce3d4fdfa8c736dc08e53f7ff0fff8ef54364aba2b176584d8`
- RGBA pixel SHA-256: `ef1baa6e78ceb0adf0ec44fbcde2fd96788e1ab05de56128fd2c14ab8fe54dd0`

This closes the exact-session identity/parity check without spending a long run repeatedly recomputing the already-proven redundant work before S02 exists.

## S01 duplicate-work proof

For the 48-action `every_n=4` representative workload:

- unique active stroke identities: **48**
- material passes in sampled frames: **312**
- extra final-render passes: **48**
- total material passes: **360**
- duplicate material passes beyond one pass/stroke: **312**
- average material-pass duplication factor: **7.5×**
- sampled frames: **13**
- actual full render calls: **14**

The first four strokes are each materialized **13 times**. This directly demonstrates that unchanged geometry repeatedly pays paper/grain/contact cost.

The regression test freezes the representative expectations:

```text
cursors                       0,4,...,48
sampled frames                13
sampled material passes       312
extra final passes            48
total material passes         360
duplication factor            7.5×
actual full render calls      14
```

## Pixel-work accounting discrepancy

Representative manifest calculation:

`13 × 1024 × 1536 × 4² = 327,155,712` supersampled pixels.

Actual full-render count includes the independent final render:

`14 × 1024 × 1536 × 4² = 352,321,536` supersampled pixels.

The exact Lucy session shows the same structural undercount: **3,473,961,216** in the manifest formula versus **3,499,134,848** when the extra final render is counted.

## Artifact-structure observation

The completed representative run produces one `.render.json` beside every frame PNG. S01 keeps this untouched because it is not the primary performance bottleneck; exporter cleanup remains a later slice.

## Validation after S01 cleanup

The previously reported `deposit_counts` stale-variable bug in `run_baseline.py` was removed. Validation performed after the fix:

- `analyze_duplicate_work.py` representative run: **PASS**, 360 total passes / 7.5× duplication
- `pytest -q dev/benchmarks/timelapse_perf/test_duplicate_work.py`: **PASS**
- `run_baseline.py --supersample 2 --every-n 4 --repeat 1`: **PASS**, final parity true, 14 renderer calls, 13 per-frame JSONs
- generated `__pycache__` / `.pyc` files removed from the deliverable

## Why S02 is now justified

S01 proves the central premise needed for `StrokeRasterCache` on both the compact fixture and the exact 546-action Lucy session: expensive unchanged strokes are repeatedly passed through the canonical material renderer. The next slice should therefore prototype caching **without changing renderer family, supersample, or final pixels**.

S02 acceptance must compare against the frozen hashes/timings above and fail closed on any frame/final parity regression.
