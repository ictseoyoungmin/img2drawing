# Public API and support matrix

Released stable: **1.0.2** · public contract: **DrawingSession/1.0.2-vnext**
Current main: **post-v1.0.2 unreleased hardening**

`CONTRACT_FREEZE.json` records the immutable v1.0.2 release surface. Current main may differ and
must not be published as v1.0.2.

## Canonical current entry point

New work begins with one orchestration model:

| Capability | Canonical entry point |
|---|---|
| create and resume current sessions | `DrawingSession.create()`, `DrawingSession.resume()` |
| intent and authority | `DrawingIntent`, `ReferenceAuthority`, `ReferenceConstraint` |
| canonical output configuration | `RenderProfile` |
| inspection/correction/output | methods on the same `DrawingSession` |

`img2drawing.__all__` remains the normal package-root discovery surface. Specialized capability
lives in explicit owning namespaces rather than creating alternative session models.

## Current namespaces

Current installable top-level implementation is limited to `core`, `data`, `inspection`,
`observation` (palette only), `provenance`, `render`, and `vnext`, plus package metadata files.

The R23 runtime/legacy namespace, old stage/review/run orchestration, historical registration,
canvas/reference layers, and non-palette R23 observation modules are no longer installed on current
main.

## Compatibility

Deprecated package-root names advertised before `0.6.0rc2` may still resolve through lazy shims.
They remain a separate compatibility surface and should only be removed by an explicit versioned
compatibility decision.

R23 compatibility is different: it existed in the v1.0.2 release freeze but has been physically
retired from current main. Current users must not be directed to `img2drawing.legacy.r23`.
Historical v1.0.2 callers needing that boundary must use the immutable v1.0.2 release/tag or recover
historical source/evidence from Git and `dev/release/r23/`.

## Claim boundary

Mechanical CI verifies package/API/persistence/replay/instruction-graph contracts. It does not
certify visual quality or cross-agent generality. Broader quality claims require fresh evidence
matching the requested claim.
