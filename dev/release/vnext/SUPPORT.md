# Public API and support matrix

Version: **1.0.0** · public contract: **DrawingSession/1.0.0-vnext**

`CONTRACT_FREEZE.json` is the machine-readable stable baseline. The v1.0.0 release changes
package/release identity and documentation only; it does not add a second runtime, a new drawing
stage, or a new persisted schema.

## Canonical package root

New work should begin at the package root with one orchestration model:

| Capability | Canonical root entry point |
|---|---|
| create and resume | `DrawingSession.create()`, `DrawingSession.resume()` |
| intent and authority | `DrawingIntent`, `ReferenceAuthority`, `ReferenceConstraint` |
| canonical output configuration | `RenderProfile` |
| observed construction facade | `PoseObservation`, `InitialConstruct`, `ConstructionMark`, construction helpers |

`img2drawing.__all__` is the authoritative normal-user root export list. Specialized public
capability remains in explicit owning namespaces rather than widening the root.

## Specialized public namespaces

- `img2drawing.inspection` — ROI/guides/measurement and inspection primitives;
- `img2drawing.observation` — optional observation/material evidence helpers;
- `img2drawing.vnext` — advanced records, guide objects, schemas, and derived authoring records;
- `img2drawing.core` — low-level stroke/history capability for framework/compatibility work.

These namespaces are capability libraries, not alternative orchestration surfaces.

## Compatibility

Names advertised at the package root before `0.6.0rc2` continue to resolve through deprecated
lazy shims so existing callers do not break abruptly. They remain absent from normal discovery.
This compatibility window is separate from R23 compatibility.

R23 checkpoint inspection, v1-v3 resume, and one-way migration remain supported only via
`img2drawing.legacy.r23`. See `MIGRATION.md`. Physical R23 retirement remains a later explicit
support decision.

## v1.0.0 claim boundary

The stable release is backed by deterministic package/API/replay verification and one curated
high-capability observed-croquis demonstration. It does **not** claim that the formal D01-D06
cross-subject/cross-agent validation campaign has completed. Those broader claims remain future
evidence work.
