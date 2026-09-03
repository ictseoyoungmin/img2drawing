# Public API and support matrix

Version: **0.6.0rc2** · public contract: **DrawingSession/0.6.0-vnext**

The dogfood baseline is frozen in `CONTRACT_FREEZE.json`; change its public or persisted
entries only with a version/schema update and responsible-slice/alignment review.

## Canonical package root

New work should begin at the package root with one orchestration model:

| Capability | Canonical root entry point |
|---|---|
| create and resume | `DrawingSession.create()`, `DrawingSession.resume()` |
| intent and authority | `DrawingIntent`, `ReferenceAuthority`, `ReferenceConstraint` |
| canonical output configuration | `RenderProfile` |
| observed construction facade | `PoseObservation`, `InitialConstruct`, `ConstructionMark`, construction helpers |

`img2drawing.__all__` is the authoritative **normal-user root** export list. It is intentionally
small; public capability does not imply package-root placement.

## Specialized public namespaces

Normal session methods own drawing, inspection lifecycle, correction, authoring lookup,
finish, render, and replay. When explicit helper objects are required, import them from the
namespace that owns them:

- `img2drawing.inspection` — ROI/guides/measurement and inspection primitives;
- `img2drawing.observation` — optional observation/material evidence helpers;
- `img2drawing.vnext` — advanced vNext records, guide objects, schemas, and derived authoring records;
- `img2drawing.core` — low-level stroke/history capability for framework/compatibility work.

These namespaces are capability libraries, not alternative orchestration surfaces.

## Pre-rc2 root compatibility

Names advertised at the package root before `0.6.0rc2` continue to resolve through deprecated
lazy shims so existing callers do not break abruptly. They are absent from `img2drawing.__all__`
and from normal root discovery. New code must import the owning namespace instead.

This compatibility window is separate from R23 compatibility and may be retired only through
a later explicit support decision.

## Legacy R23 compatibility

R23 checkpoint inspection, v1-v3 resume, and one-way migration remain supported only via
`img2drawing.legacy.r23`. Historical R23 root attribute shims are likewise absent from
`img2drawing.__all__`. See `MIGRATION.md`.

Unknown checkpoint schemas are refused. Physical R23 removal is not part of this alignment.
