# Changelog

All notable public changes to `img2drawing` are documented here. Internal development history and older dogfood notes remain in [`dev/CHANGELOG.md`](dev/CHANGELOG.md).

## Unreleased

### Removed

- Retired the installable `img2drawing.legacy.r23` compatibility namespace from post-v1.0.2 `main` and removed the hidden root fallback for R23-only names such as `DrawingRun` and `StageContract`.
- The immutable v1.0.2 release/freeze remains historical truth and still records the legacy namespace that shipped in that release. Exact retired source remains recoverable from Git history; `dev/legacy/r23_compat/README.md` records the release commit and blob identities.

### Internal cleanup audit

- `run.py`, `stages/`, `exemplar/`, `review/`, and `registration/` are confirmed compatibility-only R23 runtime roots and are candidates for a separate coordinated removal slice.
- `canvas/` and `reference/` are likely historical but require one more consumer audit; `observation/` is mixed because `SubjectPalette` remains a documented current specialized capability.
- See [`dev/release/vnext/SRC_LEGACY_AUDIT_2026-09-09.md`](dev/release/vnext/SRC_LEGACY_AUDIT_2026-09-09.md).

This is a compatibility-breaking change for callers that explicitly imported the historical R23 namespace. No new release/version is declared by this cleanup branch.

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
