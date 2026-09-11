# img2drawing v1.0.2 maintainer release record

Released: 2026-09-09
Freeze: `v1.0.2-A10-2026-09-09`
Public contract: `DrawingSession/1.0.2-vnext`

v1.0.2 promotes the validated local-first incremental timelapse backend to the normal
`DrawingSession.export_timelapse()` path for eligible stroke histories while preserving whole-export
canonical fallback for unsupported semantics or unavailable prerequisites.

## Released changes

- persistent content-addressed stroke-patch reuse;
- edit-aware dirty-region recomposition and resampling;
- atomic lossless delta-frame staging instead of mandatory full PNG frame materialization;
- persistent GIF palette reuse;
- persisted `RenderProfile` paper/material parameters remain authoritative;
- canonical fallback remains whole-export and fail-closed;
- public `export_timelapse()` signature and persisted drawing/session schemas remain compatible with
  v1.0.1.

## Validation

Release CI completed with 253 passed / 3 skipped. The preserved real `window-study` and the
post-release repository exemplar demonstrated canonical/fast final-frame pixel exactness; detailed
numbers live in `docs/releases/v1.0.2.md` and the timelapse benchmark records.

## Compatibility boundary at release time

The v1.0.2 freeze still contained explicit R23 compatibility. `CONTRACT_FREEZE.json` records that
released state exactly and remains immutable.

Current main has since physically retired R23 implementation namespaces and hardened finish,
evidence, residual-provenance, CI, and instruction-graph behavior. Those changes are **not** part of
v1.0.2 and require a future version before publication.

## Human-facing release notes

See `../../../docs/releases/v1.0.2.md` and `../../../CHANGELOG.md`.
