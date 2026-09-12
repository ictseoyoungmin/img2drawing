# Changelog

All notable public changes to `img2drawing` are documented here. Internal development history and older dogfood notes remain in [`dev/CHANGELOG.md`](dev/CHANGELOG.md).

## Unreleased

### Changed

- `1.0.3rc2 / A12` aligns the user-facing gesture mode with the public runtime: `DrawingIntent(drawing_mode="gesture")` and `resolve_mode_guide("gesture")` are now supported selections while pure-vs-constructive remains an instruction-graph finish-level decision rather than a workflow stage.
- Gesture guidance now rejects the opposite failure of smooth generic beans/ovals/capsules as well as hard geometric construction icons. Sparse masses must preserve observed profile/jaw/nape, shoulder/back/side asymmetry, taper, hip shelf, near/far exposure, and leg-attachment relations where visible; `rounded` alone is not a completion criterion.
- `DrawingSession.finish()` gained two preconditions and now raises `ValueError` where it previously returned a `FinishRecord`:
  - the current drawing must contain authored strokes — a session that was never drawn on, or whose marks were all erased again, can no longer be finished;
  - the final inspection must have a non-stale `record_evidence_read()` event. Generating an inspection is no longer accepted as evidence that the Agent read it.
- `DrawingSession.inspect()` now renders through the session's persisted `RenderProfile` (paper tooth/scale/seed, background, graphite) instead of renderer defaults, so a customized profile is inspected under the same material it will export under. The inspection sheet stays pinned to 1x canvas space because registration/ROI/measurement geometry is defined in canvas pixels; only final and replay export honor `output_scale`.
- The v10 renderer now normalizes the private compatibility `Stroke.stage` field out of render seed identity. `inspect()`, canonical replay/final rendering, and the fast timelapse path therefore see the same v10 hand/material seed for identical authored geometry. Historical v9 seed semantics remain frozen for saved v1.0.2 replay, and profile-less legacy timelapse calls continue to select v9 explicitly.
- Residual/correction guidance now documents the `observation_id` provenance contract explicitly: a repairing mutation for a current residual should carry the residual's observation id, followed by a fresh after-inspection before `resolve_residual()`.
- Completion guidance now makes clear that `accepted_limitations` records acknowledged non-blocking weaknesses; it does not bypass an open residual record.

The `finish()` preconditions and retired R23 namespaces are compatibility changes from v1.0.2. The current package is an unpublished 1.0.3 release candidate; v1.0.2 remains the latest published stable release until an explicit stable manifest is created.

### Removed

- Retired the installable `img2drawing.legacy.r23` compatibility namespace and removed the hidden root fallback for R23-only names such as `DrawingRun` and `StageContract`.
- Retired the remaining R23 orchestration/runtime cluster from current `src`: `run.py`, `stages/`, `exemplar/`, `review/`, and the historical `registration/` package.
- Removed layers and data that became orphaned with that cluster: `canvas/`, the historical `reference/` package, non-palette R23 observation contract/lock/evidence modules, and `data/registration_profile.json`.
- The immutable v1.0.2 release/freeze remains historical truth. Exact retired source remains recoverable from Git history and the pointers under `dev/legacy/`.

### Internal cleanup

- Current installable top-level source is narrowed to `core/`, `data/`, `inspection/`, `observation/` (palette only), `provenance/`, `render/`, and `vnext/`, plus package metadata files.
- Added `dev/tools/build_skill_zip.py` and release-zip contract tests so local bytecode/cache/build residue cannot silently leak into the distributable skill archive.
- Historical closure checks use frozen Git/release evidence instead of requiring retired runtime files to remain in mutable `src`.
- See [`dev/release/vnext/SRC_LEGACY_AUDIT_2026-09-09.md`](dev/release/vnext/SRC_LEGACY_AUDIT_2026-09-09.md).

## v1.0.2 — Local-first exact timelapse backend

Released 2026-09-09.

### Changed

- `DrawingSession.export_timelapse()` now uses the validated local-first fast backend for eligible stroke histories while preserving whole-export canonical fallback.
- Added persistent content-addressed stroke-patch reuse, edit-aware dirty-region recomposition, dirty-region Lanczos resampling, atomic lossless delta-frame staging, and persistent palette reuse.
- Full PNG frame materialization is no longer required by the default fast path.
- RenderProfile paper/material parameters remain authoritative for the fast renderer.
- Post-v1.0.1 resumable streaming code was retired from active production/CI and retained only as legacy evidence.

### Compatibility

- Public `DrawingSession.export_timelapse()` signature is unchanged from v1.0.1.
- Persisted drawing/session schemas are unchanged.
- Unsupported action semantics, raw ordered spatial erasers, unavailable FFmpeg, or other fast-path prerequisites fail closed to the canonical exporter for the entire export.

### Validation

- Release CI: **253 passed / 3 skipped**.
- Real `window-study`: 1,272 actions / 637 frames, warm render+pack **4.168 s**, GIF encode **2.163 s**, internal pipeline **6.331 s**, canonical final RGB pixel-exact.
- Post-release exemplar benchmark on `dev/exemplar-sources/p2_axes_v2.json`: warm internal pipeline **0.231–0.246 s** across `every_n=4/2/1`; persistent cache produced roughly **4.8–5.35×** pipeline speedup over cold runs.
- Post-release fast/canonical final RGB SHA-256: `7528508869ed45ff4ce03569af5ccfea606ac79c3a37dd01e1050f5221c4b282` on both paths (`pixel_exact=true`).

See [`docs/releases/v1.0.2.md`](docs/releases/v1.0.2.md) and [`dev/benchmarks/timelapse_perf/V1_0_2_POST_RELEASE_EXEMPLAR.md`](dev/benchmarks/timelapse_perf/V1_0_2_POST_RELEASE_EXEMPLAR.md).

## v1.0.1 — Astra-derived authoring ergonomics

Released 2026-09-05.

- Added `retune_stroke()` for material-only stroke corrections while preserving geometry.
- Added deterministic shared Catmull-Rom sampling.
- Added `continuous_pencil` for low-taper continuous boundaries.
- Refined geometry-vs-material residual guidance and topology-aware curve handling.
- No persisted action/schema changes and no new drawing lifecycle.

See [`docs/releases/v1.0.1.md`](docs/releases/v1.0.1.md).

## v1.0.0 — First stable release

Released 2026-09-05.

- Established the stable Agent Skill/runtime release surface.
- Preserved explicit authored strokes, replayable provenance, canonical rendering, and correction-oriented observation workflow.
- Published the first curated showcase demonstration.

See [`docs/releases/v1.0.0.md`](docs/releases/v1.0.0.md).
