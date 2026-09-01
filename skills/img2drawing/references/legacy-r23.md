# Legacy R23 compatibility route

Read this document only when continuing or migrating an existing `DrawingRun`
checkpoint. It is not the canonical route for new work.

## Explicit namespace

R23 is opt-in and versioned:

```python
from img2drawing.legacy.r23 import (
    DrawingRun,
    inspect_checkpoint,
    migrate_checkpoint,
    resume_checkpoint,
)
```

Do not import `DrawingRun`, stage contracts, or review records from the root
package. Root legacy attributes remain temporary deprecated shims for existing
callers, are absent from `img2drawing.__all__`, and may be retired at R03.

Importing `img2drawing`, `img2drawing.vnext`, or using wildcard root imports does
not load the R23 runtime, stage registry, stage review, reopen behavior, or R23
persistence orchestration. Importing `img2drawing.legacy.r23` alone is also lazy;
the historical modules load only when a historical name or operation is used.

## Checkpoint support matrix

| Checkpoint | Explicit resume | One-way vNext migration |
|---|---:|---:|
| `img2drawing.run_checkpoint.v1` | supported | supported |
| `img2drawing.run_checkpoint.v2` | supported | supported |
| `img2drawing.run_checkpoint.v3` | supported | supported |
| `img2drawing.vnext.session.v2` | use `DrawingSession.resume()` | already canonical |
| unknown/missing schema | refused with guidance | refused with guidance |

Inspect without loading R23 orchestration:

```python
from img2drawing.legacy.r23 import inspect_checkpoint

info = inspect_checkpoint("old-run/session/checkpoint.json")
print(info.schema, info.can_resume, info.can_migrate, info.guidance)
```

Continue an R23 job in place only when the task explicitly requires its stage and
review semantics:

```python
from img2drawing.legacy.r23 import resume_checkpoint

run = resume_checkpoint("old-run")
```

Migrate shared drawing truth once when subsequent work should use vNext:

```python
from img2drawing.legacy.r23 import migrate_checkpoint

session = migrate_checkpoint(
    "old-run/session/checkpoint.json",
    output_dir="migrated-vnext-run",
    # reference="relocated-subject.png",  # required only if the old path moved
)
```

Migration reuses `DrawingRun.resume()` for R23 validation and reuses the same
`AgentDrawingSession`/`CanvasHistory` data. It preserves:

- subject name and SHA-256;
- session lineage;
- the exact shared action log and its digest;
- source state digest plus the canonical stage-free target state digest;
- inert stage labels as historical action provenance;
- explicit target renderer and `RenderProfile` provenance.

R23 checkpoints did not persist their renderer identity. Migration records that
fact as `not-persisted-by-r23-checkpoint`; it never invents a historical renderer
ID. The target vNext checkpoint binds the current canonical renderer/profile
explicitly.

Migration intentionally does not convert stage progress, stage reviews, reopen
state, or legacy finish claims into vNext authority. They remain in the source
checkpoint as historical evidence. Observation IDs referenced by preserved
actions become identity-only migration tokens and do not claim fresh vNext visual
evidence. Inspect the migrated current state and declare current intent before
making completion claims.

The migration target must not already contain `session.checkpoint.json`. Choose a
new output directory rather than overwriting an existing canonical session.

## Historical scope

R23 preserves the P1–P6 stage contract, stage/local review, pass memory, reopen
records, reference bundles, exemplar ablation, and registration comparison
records. Their only supported public boundary is `img2drawing.legacy.r23`.

When drawing knowledge is still useful—gesture, mass, balance, limb curvature,
attached-object topology, contour selection, or face/hair relationships—use the
stage-free references first. Do not carry `advance`, `reopen_stage`, manifest
closure, or Pn ownership into a new vNext task.
