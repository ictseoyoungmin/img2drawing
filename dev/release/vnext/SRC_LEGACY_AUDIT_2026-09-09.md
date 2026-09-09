# src legacy audit — 2026-09-09

This audit follows retirement of `skills/img2drawing/src/img2drawing/legacy/` from the installable post-v1.0.2 source tree. It classifies remaining top-level runtime paths by current `DrawingSession` dependency and explicit repository contracts. It does **not** authorize bulk deletion by name alone.

## A. Canonical/current — keep

These paths are used by the stage-free `DrawingSession` route or documented current specialized capabilities.

- `_version.py` — current package/version authority; retains historical R23 constants only because `run.py` still exists.
- `core/` — authoritative action/history/IR implementation used directly by `vnext.session`; the inert historical `stage` field is compatibility data, not evidence that `core` itself is legacy.
- `inspection/` — current measurement/inspection authority; `vnext.session` and `vnext.construction` import it directly.
- `render/` — current canonical renderer/material/tone implementation.
- `provenance/` — current replay/timelapse implementation, including the v1.0.2 fast backend and canonical replay helpers.
- `vnext/` — canonical stage-free session and current public capability layer.
- `data/` — runtime/package data; retain pending a file-level data inventory rather than deleting by age.
- `observation/palette.py` and its `MaterialSample` / `SubjectPalette` public access — still documented in `references/api/public-surface.md`.

## B. Confirmed compatibility-only R23 cluster — next removal candidates

The repository already names these roots as `LEGACY_RUNTIME_ROOTS` in `dev/tests/test_runtime_physical_isolation.py`, and their own package/module documentation describes them as R23 compatibility implementations. Canonical `DrawingSession` does not import them.

- `run.py` — historical `DrawingRun` Pn-stage orchestration.
- `stages/` — historical Pn stage registry/contracts/progress runtime.
- `exemplar/` — historical grammar-exemplar/ablation tooling; current deployable skill intentionally has no canonical exemplar workflow.
- `review/` — historical stage-review runtime, distinct from the current instruction-graph review guidance.
- `registration/` — historical structural registration contracts; current registration/measurement capability is owned by `inspection/`.

**Recommendation:** remove these together in a separate compatibility-breaking slice after checking tests/tools that still exercise historical R23 behavior. Do not delete one leaf while leaving `run.py` with broken imports.

## C. Likely compatibility-only, but mixed/dependency audit required before deletion

- `canvas/` — currently consumed by historical `run.py`; canonical `vnext.session` operates directly on shared history/IR and does not import this package. Verify no current dev/public consumer before removal.
- `reference/` — historical `ReferenceBundle` + stage-target model is consumed by `run.py`; current `DrawingSession` uses `vnext.reference_authority`. Verify no supported external specialized API remains before removal.
- most of `observation/` other than `palette.py` — `ObservationContract`, lock/reopen records, and related R23-era records are tied to historical orchestration, but the package is mixed because `SubjectPalette` remains a current documented specialized API. Split or narrow exports before deleting files.

## D. Compatibility shims that remain intentionally current

Root `_ROOT_COMPAT_TARGETS` in `img2drawing/__init__.py` is **not** the removed R23 namespace. It preserves pre-0.6.0rc2 import locations for capabilities whose owning modules still exist (`core`, `inspection`, `observation.palette`, `render.tone_scale`, `vnext`). Those deprecated aliases may be retired later under an explicit API/semver decision, but they are not dead implementation trees.

## Retirement decision from this slice

Removed now:

- `src/img2drawing/legacy/__init__.py`
- `src/img2drawing/legacy/r23.py`
- root fallback that dynamically resolved R23-only names through `img2drawing.legacy.r23`

Preserved as historical evidence:

- immutable v1.0.2 Git history/release commit
- `dev/release/vnext/CONTRACT_FREEZE.json` exactly as shipped
- `dev/legacy/r23_compat/README.md` pointer to the former source blobs

Not removed in this slice:

- `run.py`, `stages/`, `exemplar/`, `review/`, `registration/`
- `canvas/`, `reference/`, mixed `observation/`

This keeps the first cleanup vertical slice narrow: the explicitly named installable `legacy/` namespace disappears without pretending that the rest of the R23 cluster has already been safely retired.
