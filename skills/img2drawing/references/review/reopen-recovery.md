# Reopen Recovery

A later stage may reveal that an earlier stage was wrong.

Do not compensate locally when the root cause belongs upstream.

## Policy

1. Identify the **earliest responsible stage**.
2. Record the downstream evidence that exposed the error.
3. Call `run.reopen_stage(...)`.
4. Runtime archives the invalidated target/downstream reviews.
5. Runtime rewinds authoritative drawing history to the target stage start.
6. Rebuild the target stage from the restored branch.
7. Re-review and close the target.
8. Rebuild every invalidated downstream stage from the corrected upstream state.

## Visual FAIL to REOPEN decision

The stage where a defect is noticed is not necessarily the stage that owns it.

- Keep the current stage at `REVISE` when the frozen observation and earlier axes/pose are
  correct but the current mass, taper, overlap or line ownership is wrong.
- `REOPEN` the earliest responsible stage when the mismatch contradicts that stage's
  `must_preserve` information, or when a current-stage patch would conceal the upstream
  error.
- If the same structural concern survives three fresh passes, stop local nudging, make a
  more informative whole/region overlay, re-observe and rewrite the stroke plan before
  deciding whether to reopen.

Visual FAIL is represented by `decision="revise"` plus concrete `remaining_concerns`; the
reopen itself is a separate `run.reopen_stage()` mutation with its own reason and findings.
Do not use a pass count, a plausible isolated crop or a process PASS to suppress a visual
FAIL.

Example:

```python
reopen = run.reopen_stage(
    "P2_primary_axes",
    reason="P3 pelvis mass is compensating for an incorrect P2 pelvis axis.",
    discovered_in_stage="P3_primary_masses",
    findings=[
        "subject pelvis tilt contradicts the active P2 axis",
        "patching P3 would preserve the upstream error",
    ],
)
```

## What reopen invalidates

For the target and every already-started downstream stage:
- active review records;
- prepared review artifacts;
- active local-review bindings;
- advanced-review state;
- drawing actions on the abandoned branch;
- pass-memory continuity from the abandoned branch.

Visual/review evidence is not destroyed. It is moved under:

`reopen_archive/reopen_XX/reviews/...`

A `reopens/reopen_XX.json` record stores:
- target stage;
- discovery stage;
- reason/findings;
- source/restored cursor and state hashes;
- invalidated stages;
- abandoned review digests;
- abandoned local-review IDs;
- abandoned action IDs;
- trigger review digest;
- archive directory.

## Fresh-worker restart states

The first active pass after reopen receives:

`pass_memory.state = reopen_restart`

The target stage receives:
`role = reopened_target`

Invalidated downstream stages receive:
`role = invalidated_downstream`

The worker packet contains a visible `REOPEN CONTEXT` section.

## Semantic authority

Runtime never chooses which stage is wrong. The Agent chooses the target stage and
writes the reason/findings.

Runtime only performs deterministic rewind, invalidation, archival and provenance.

## Anti-patterns

Do not:
- patch P3 mass to hide a P2 axis error;
- keep downstream reviews active after upstream structure changes;
- reuse archived local reviews as if they described the corrected branch;
- preserve downstream strokes and merely move them around after reopen;
- infer that reopen succeeded without fresh target/downstream reviews.
