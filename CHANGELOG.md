# Changelog

All notable public changes to `img2drawing` are documented here. Internal development history and older dogfood notes remain in [`dev/CHANGELOG.md`](dev/CHANGELOG.md).

## Unreleased

### Changed

- `1.0.4rc1 / A15` opens the terminal-semantics bottleneck above the published v1.0.3 baseline. New candidate sessions select additive renderer `pillow-pencil-contact-v12 / 1`; explicit v9/1, v10/1, and v11/1 replay remains available.
- v12 consumes the already-persisted public `terminal_mode` semantic field. `contact` preserves v11 pixels exactly, while `gentle`, `flick`, and `residue` resolve distinct bounded physical terminal pressure/deposition behavior without moving authored geometry.
- Non-contact terminals are applied after deterministic trajectory resampling so a physical release span cannot be stretched across one sparse authored segment.
- The v1.0.3 stable verifier is anchored to the immutable v1.0.3 tag/candidate package tree instead of requiring mutable `HEAD` to remain identical to the published package.

### Validation

- T01 requires same-geometry terminal-mode pixel differentiation, v12-contact ↔ v11 exactness, suffix locality, v12 canonical-final ↔ fast-final exactness, explicit v11 replay preservation, and the full current/historical/package CI stack.

## v1.0.3 — Gesture + renderer quality

Released 2026-09-13.

### Changed

- `A14` promotes additive renderer `pillow-pencil-contact-v11 / 1` for new sessions while preserving explicit v9/1 and v10/1 replay. v11 fixes transitional broad-pencil square/butt continuity-core terminals with pressure/taper-resolved round contact and strengthens deterministic page-fixed broad graphite/tooth variation without changing mean authored value authority.
- Ordinary thin v11 strokes delegate byte-for-byte to v10; canonical final and fast timelapse consume the same registered v11 patch builder.
- `DrawingIntent(drawing_mode="gesture")` and `resolve_mode_guide("gesture")` are public runtime selections while pure-vs-constructive remains an instruction-graph finish-level decision rather than a workflow stage.
- Gesture guidance rejects smooth generic beans/ovals/capsules as well as hard geometric construction icons. Sparse masses must preserve observed profile/jaw/nape, shoulder/back/side asymmetry, taper, hip shelf, near/far exposure, and leg-attachment relations where visible; `rounded` alone is not a completion criterion.
- `DrawingSession.finish()` gained two preconditions and now raises `ValueError` where it previously returned a `FinishRecord`: the current drawing must contain authored strokes, and the final inspection must have a non-stale `record_evidence_read()` event.
- `DrawingSession.inspect()` renders through the session's persisted `RenderProfile`; only final and replay export honor `output_scale`.
- The v10 renderer normalized private compatibility `Stroke.stage` out of render seed identity. Historical v9 seed semantics remain frozen.
- Residual/correction guidance documents the `observation_id` provenance contract explicitly.
- Completion guidance makes clear that `accepted_limitations` does not bypass an open residual record.

### Removed

- Retired the installable `img2drawing.legacy.r23` compatibility namespace and hidden root fallback for R23-only names.
- Retired the remaining R23 orchestration/runtime cluster and orphaned canvas/reference/registration layers from current `src`.
- The immutable v1.0.2 release/freeze remains historical truth.

### Validation

- G01 gesture dogfood: **PASS/CLOSED** — `dev/dogfood/g01-gesture-rc2/README.md`.
- G02 broad-pencil visual/material dogfood: **PASS/CLOSED** — `dev/dogfood/g02-broad-pencil-v11/README.md`.
- v11 tests cover thin v10↔v11 exactness, broad terminal morphology, graphite/tooth variation, explicit v9/v10 replay, and canonical↔fast exactness.

See [`docs/releases/v1.0.3.md`](docs/releases/v1.0.3.md).

## v1.0.2 — Local-first exact timelapse backend

Released 2026-09-09.

### Changed

- `DrawingSession.export_timelapse()` uses the validated local-first fast backend for eligible stroke histories while preserving whole-export canonical fallback.
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
- Post-release exemplar benchmark: warm internal pipeline **0.231–0.246 s** across `every_n=4/2/1`.

See [`docs/releases/v1.0.2.md`](docs/releases/v1.0.2.md).

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
