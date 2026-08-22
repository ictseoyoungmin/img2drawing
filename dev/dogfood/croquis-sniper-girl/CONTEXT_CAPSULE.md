# Croquis Sniper Girl — Context Capsule

This document helps a future agent resume the work without reading the original checkpoint
of more than 43,000 lines wholesale.

## Canonical paths

- Execution record: `02_run_record/`
- Final output: `01_output/croquis_final.png`
- Timelapse: `01_output/croquis_timelapse.gif`
- Stage evidence: `03_stage_reviews/`
- Abandoned branches: `04_abandoned_branches/`
- Actual execution scripts: `05_scripts/`

## Run identity

- Work: Sniper Girl — Full-body Croquis
- Skill: `img2drawing 0.5.2`, release slice `R22`
- Model: Claude Opus 5
- Start mode: single initial prompt
- Core pipeline: `P1_gesture` → `P2_primary_axes` →
  `P3_primary_masses` → `P4_structural_connections` → `P5_clean_blockin`
- A separate identity finishing pass was performed afterward
- Three reopens occurred during the run; previous branches are preserved in
  `04_abandoned_branches/`

## Reading policy

`02_run_record/checkpoint.json` contains 43,794 lines. Future work should follow this
sequence:

1. Read this capsule and `02_run_record/DOGFOOD_REPORT.md` first.
2. Selectively query only the top-level state and the required stage/reopen summaries from
   `checkpoint.json`.
3. Extract only the `action_id`, `history_cursor`, and `stage` ranges relevant to the edit.
4. Never put the full checkpoint or full action log into an agent prompt.

Example:

```bash
jq '{schema, version, progress, reopens, reopen_contexts}' \
  02_run_record/checkpoint.json

jq '[.action_memory_events[]
    | select(.stage == "P5_clean_blockin")
    | {action_id, history_cursor, kind, part, target_stroke_id}]' \
  02_run_record/checkpoint.json
```

Before making edits, treat the current `checkpoint.json` and `session.json` as the
authoritative state. Do not use showcase images or rendered images in `03_stage_reviews/`
as a substitute for that state.

## Known limitation

The P5 clean block-in detail ceiling was intentionally exceeded to satisfy the identity
requirement. The identity pass is recorded separately in
`02_run_record/identity_pass.json`.
