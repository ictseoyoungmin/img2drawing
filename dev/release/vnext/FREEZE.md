# v1.0.2 stable contract freeze

Freeze ID: **v1.0.2-A10-2026-09-09**

`CONTRACT_FREEZE.json` is the immutable machine-readable release snapshot for v1.0.2. It records
package version `1.0.2`, public contract `DrawingSession/1.0.2-vnext`, release revision `A10`, and
the renderer/API/schema surface that was released on 2026-09-09.

v1.0.2 promoted the validated local-first exact timelapse backend while preserving whole-export
canonical fallback for unsupported histories. Persisted drawing/session schemas and the public
`export_timelapse()` method signature remained compatible with v1.0.1.

At the time of this freeze, R23 compatibility still existed and therefore appears in the frozen
snapshot. That is **historical release truth**, not current-main support truth. Post-release main has
physically retired the R23 runtime/legacy namespace and must not mutate this freeze to pretend those
later removals were part of v1.0.2.

Likewise, later finish/evidence and instruction-graph hardening belong to unreleased post-v1.0.2
main. A future release must create a new freeze/version rather than editing this record.

This freeze protects released public/persisted meanings and deterministic render/replay evidence; it
does not certify artistic quality.
