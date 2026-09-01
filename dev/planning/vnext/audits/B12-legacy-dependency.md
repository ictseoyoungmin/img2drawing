# B12 legacy dependency and ownership audit

Date: 2026-09-01

## Finding

The canonical implementation was already operationally stage-free, but the root
package still advertised every R23 runtime, stage, review, reference, ablation,
and registration symbol through `__all__`. `from img2drawing import *` therefore
loaded legacy orchestration, and `_version.PUBLIC_API` still named `DrawingRun`.
The root package also owned the entire historical lazy-export mapping.

## Consolidated boundary

| Area | Canonical authority | R23 compatibility authority |
|---|---|---|
| package surface | `img2drawing` / `DrawingSession` | `img2drawing.legacy.r23` |
| orchestration | `vnext.session.DrawingSession` | `run.DrawingRun` loaded lazily |
| persistence | `img2drawing.vnext.session.v2` | run checkpoint v1–v3 adapter |
| stroke/action/history | existing `core/` | same existing `core/` |
| renderer/tools | existing `render/` and `core/` | same existing modules |
| stage/review/reopen | absent | existing R23 modules, opt-in only |
| export mapping | canonical root `__all__` | sole `LEGACY_EXPORTS` table |

No `core_v2`, alternate renderer, copied checkpoint parser, or second history was
introduced. The explicit adapter calls the existing `DrawingRun.resume()` validator
before cloning shared action/history data into one canonical vNext checkpoint.

## Persistence decision

- R23 run checkpoints v1–v3 may resume or migrate only through the explicit adapter.
- vNext checkpoints are rejected by the R23 adapter with `DrawingSession.resume()`
  guidance.
- Unknown schemas are rejected with the supported schema list and an export-first
  migration instruction.
- Migration preserves subject/action/source-state lineage and binds the target
  renderer/profile.
- Because R23 checkpoints never stored renderer identity, the source renderer is
  honestly recorded as unknown rather than inferred.
- Stage progress, reviews, reopens, and legacy finish claims stay historical and do
  not become vNext authority.

## Dependency evidence

Subprocess tests cover `import img2drawing`, `import img2drawing.vnext`, root wildcard
imports, explicit namespace import, and explicit historical-name resolution. Only the
last operation loads `run`, `stages`, and `review`. Existing R23 regression tests remain
available. Physical R23 deletion remains deferred to post-dogfood R03.

## Package and documentation decision

The project description was already stage-free. The root `PUBLIC_API` identifier is now
`DrawingSession`; R23 receives distinct historical identifiers. Canonical skill guidance
uses only the stage-free route, while one compatibility document owns the resume and
migration directions. The B17 package audit will verify the same boundary in built and
clean-installed artifacts.
