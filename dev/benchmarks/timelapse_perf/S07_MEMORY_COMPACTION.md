# S07 — Memory-compacted exact incremental replay

State: **CLOSED AS A DEV PROTOTYPE**

S07 keeps the exact S02/S03 material masks, S05 forward history traversal, and S06 edit-aware dirty-region semantics, but removes two persistent-memory costs that are no longer necessary in a forward-only timelapse exporter. Production runtime behavior remains unchanged.

## Premise

S06 proved the full Lucy 546-action replay in about 21.45 s, but retained a 4-channel supersampled graphite canvas plus every historical stroke-version mask. On the 941×1672 / ss4 Lucy workload that meant roughly:

- 100,694,528 bytes for the persistent high-resolution RGBA canvas,
- 78,977,721 bytes for 541 historical material masks,
- 6,293,408 bytes for the native RGBA output canvas.

The graphite RGB is constant for one render profile. Only accumulated alpha changes. Also, after S05 history moves monotonically forward, a replaced/deleted material version is never needed again once its dirty region has been rebuilt.

## Accepted design

### 1. Exact 8-bit high-resolution alpha canvas

The persistent supersampled canvas changes from RGBA to `L`. Source-over alpha uses the exact Pillow rounding rule:

```text
out_alpha = src + round(dst * (255 - src) / 255)
```

The implementation was exhaustively checked over all 65,536 `(dst, src)` 8-bit alpha pairs against Pillow `Image.alpha_composite`. At snapshot time only the dirty alpha crop is reattached to the fixed graphite RGB, composited over the configured background, and Lanczos-resampled using the same S06 path.

### 2. Active-only material ownership

S06's content cache retained all 541 material versions. S07 instead lets the forward canvas own only the current active `CachedStrokeRaster`s. Replaced/deleted masks are held until the authoritative dirty rebuild finishes, then closed immediately. Unchanged active masks remain available for later edit recomposition.

Lucy therefore finishes with 45,729,402 bytes of active masks instead of 78,977,721 bytes of historical masks. 149 obsolete material versions are released during the replay.

## Exact Lucy evidence

Contract:

- 941×1672 output
- supersample 4
- 546 actions
- every_n=4
- 138 sampled frames

S07 produces **138/138 frame hashes exactly equal to S06** and retains the certified final hash:

`ef1baa6e78ceb0adf0ec44fbcde2fd96788e1ab05de56128fd2c14ab8fe54dd0`

Timing remains effectively neutral:

- S06 compute reference: 21.4456 s
- S07 compute: 22.0103 s
- `/usr/bin/time -v` wall: 24.10 s → 23.32 s

The slice is therefore a memory optimization, not a speed claim.

## Memory result

Estimated long-lived raster memory at final Lucy state:

```text
S06
  high-res RGBA canvas   100.69 MB
  historical masks       78.98 MB
  native RGBA output       6.29 MB
  --------------------------------
  total                  185.97 MB

S07
  high-res alpha canvas   25.17 MB
  active masks            45.73 MB
  native RGBA output       6.29 MB
  --------------------------------
  total                   77.20 MB
```

That is a **58.49% reduction** in the modeled long-lived raster footprint.

Observed process peak RSS under the same local Python/runtime path:

- S06: 493,032 KB
- S07: 408,052 KB
- reduction: **17.24%** (~83 MB)

The smaller RSS reduction than the persistent model shows that transient NumPy/materialization arrays are now a major peak-memory contributor.

## Tile-backing reopen

Sparse alpha tiles were evaluated from final Lucy contact bounds before adding more machinery. Estimated touched coverage:

- 128px hi-res tiles: 866 / 1590 tiles, 14.19 MB
- 256px: 231 / 405, 15.14 MB
- 512px: 68 / 112, 17.83 MB
- 1024px: 22 / 28, 23.07 MB

Compared with the already compact 25.17 MB flat alpha canvas, practical tile backing saves only about 7–11 MB at useful tile sizes on Lucy while making crop/rebuild/Lanczos-region assembly more complex. It would not attack the current ~408 MB process peak, which is now dominated by materialization temporaries. Sparse tile backing is therefore **deferred rather than adopted by default**.

## Regression

Combined local dev regression:

```text
S01 / S02 / S03 / S04 / S06 / S07
7 passed
```

S07 additionally checks all 65,536 alpha-composition pairs and replace/delete/opacity-content-change exact frame parity.

## Decision

Carry forward:

1. exact one-channel persistent graphite state;
2. active-only ownership of material masks for monotone replay;
3. immediate release of obsolete versions after dirty rebuild.

Do not yet carry forward:

- sparse high-resolution tiles,
- a large historical material cache,
- production runtime integration.

The next bottleneck is no longer the persistent canvas. The next slice should close explicit eraser / segment-edit semantics and then fold the proven S02–S07 path into a canonical streaming exporter with bounded manifest/frame handling.
