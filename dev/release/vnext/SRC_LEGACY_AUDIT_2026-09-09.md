# src legacy audit — 2026-09-09

This audit began after retirement of `skills/img2drawing/src/img2drawing/legacy/` and was completed by tracing the remaining R23 orchestration imports, active tests, package-root compatibility targets, current `DrawingSession` dependencies, and packaged data consumers. Historical release evidence is retained in Git/release records; retired implementation is not kept inside mutable `src` merely to satisfy old tests.

## A. Canonical/current — keep

These paths remain owned by the stage-free `DrawingSession` route or by a documented current specialized capability.

- `_version.py` — current `1.0.2 / A10` package, public-API, and default-session identity only. R23-only version constants were retired with `DrawingRun`.
- `core/` — authoritative action/history/IR implementation used directly by vNext. Historical `stage` fields that remain in persisted action/history compatibility are inert serialization compatibility, not an R23 runtime tree.
- `inspection/` — current explicit measurement/inspection authority. `Registration` here is a small stage-free coordinate mapping supplied by the Agent; it is distinct from the retired `img2drawing.registration` solver/comparison package.
- `render/` — current canonical renderer/material/tone implementation.
- `provenance/` — current replay/timelapse implementation, including the v1.0.2 local-first fast backend and canonical fallback.
- `vnext/` — canonical `DrawingSession` and current public capability layer.
- `data/pencil_presets.json`, `data/pencil_contact_profile.json`, `data/tone_scale.json` — current renderer/material/tone package data.
- `observation/palette.py` plus `observation/__init__.py` — current documented `MaterialSample` / `SubjectPalette` specialized API.

## B. R23 orchestration/runtime — retired from current src

The following compatibility-only cluster was physically removed in PR #30. Canonical `DrawingSession` did not import these roots; active historical tests were separated from current runtime contracts before deletion.

- `run.py` — historical `DrawingRun` Pn-stage orchestration.
- `stages/` — historical Pn stage registry/contracts/progress runtime.
- `exemplar/` — historical grammar-exemplar/ablation runtime.
- `review/` — historical stage-review, pass-memory, resolved-form, and adaptive-evidence runtime.
- `registration/` — historical structural registration graph/comparison runtime.

The old completion gates now verify the exact closed source/test blobs from the pre-retirement Git commit rather than requiring these files to remain importable forever.

## C. Orphans exposed by R23 cluster retirement — retired

Removing `DrawingRun` made the remaining ownership unambiguous:

- `canvas/` — its `CanvasRuntime` / `CanvasInspector` / `CanvasEditor` facade was consumed by the historical `DrawingRun`; vNext operates directly on current core history/IR and inspection/output surfaces.
- `reference/` — historical `ReferenceBundle` + stage-target model was a `DrawingRun` dependency; current reference semantics are owned by `vnext.reference_authority`.
- `observation/contract.py` — R23 `ObservationContract` / `ViewObservation` model.
- `observation/lock.py` — R23 frozen-observation/reopen records.
- `observation/evidence.py`, `observation/uncertainty.py`, `observation/views.py` — helpers tied to that historical observation contract/lock route.
- `data/registration_profile.json` — loaded by the retired `registration.compare.ComparisonProfile.packaged()` only. Current `inspection.Registration` does not read this profile.

`observation` was therefore narrowed rather than deleted: only the current palette API remains.

## D. Compatibility shims intentionally retained

Root `_ROOT_COMPAT_TARGETS` in `img2drawing/__init__.py` is not dead R23 implementation. It preserves deprecated pre-0.6.0rc2 import locations for capabilities whose owning modules remain current (`core`, `inspection`, `observation.palette`, `render.tone_scale`, `vnext`). Active tests still exercise some of these aliases, and B18 records the v1.0.2 root compatibility state.

They may be removed in a later explicit API/semver cleanup, but they are not unused legacy source trees and were intentionally excluded from this retirement.

## E. Historical authority

Historical R23 implementation and release truth remain recoverable from immutable evidence rather than copied runtime code:

- pre-retirement current-tree commit: `4074a2080ad739acdf179bb0784869a8831c5ef0`
- released v1.0.2 tag for the former `img2drawing.legacy.r23` blob
- `dev/release/r23/` frozen manifest/assets
- `dev/release/vnext/CONTRACT_FREEZE.json` as the factual v1.0.2 release snapshot
- `dev/legacy/r23_compat/README.md` and `dev/legacy/r23_runtime_cluster/README.md` as history pointers

## Final src classification after this cleanup

Expected installable top-level source surface:

- `__init__.py`
- `_version.py`
- `core/`
- `data/`
- `inspection/`
- `observation/` (palette only)
- `provenance/`
- `render/`
- `vnext/`

No installable `legacy`, `run`, `stages`, `exemplar`, `review`, `registration`, `canvas`, or historical `reference` runtime is expected to remain.

This closes the R23 physical-runtime cleanup. Any future removal of root deprecated aliases or inert compatibility fields should be treated as a separate public API/persistence decision, not folded into this source-tree retirement.
