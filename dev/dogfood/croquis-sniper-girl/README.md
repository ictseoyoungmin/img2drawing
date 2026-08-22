# Sniper Girl — Full-body Croquis Run Archive

This directory is the canonical dogfood run archive promoted from
`temp/croquis_sniper_girl`. The curated showcase copy is available at
`showcase/entries/croquis-sniper-girl-opus5-r22/`.

Using the `img2drawing 0.5.2` skill and a single reference photo in subject-only mode,
the agent completed the five-stage pipeline:
`P1 gesture → P2 primary axes → P3 primary masses → P4 structural connections → P5 clean block-in`.
This is not image generation; it is a drawing made from 464 explicitly positioned strokes.

## 01_output — Final outputs

| File | Description |
|---|---|
| `croquis_final.png` | **Final image** (512×768), including face, hair, and outfit details |
| `croquis_timelapse.gif` | **Timelapse**, 117 frames from the first line to the final result |
| `stage_progression.png` | Six-frame progression sheet covering P1–P5 and the finishing pass |
| `reference_vs_final.png` | Side-by-side comparison of the reference photo and final image |
| `subject_vs_final_board.png` | Runtime-generated comparison board |
| `subject_reference.png` | Input reference photo |

## 02_run_record — Execution record

`DOGFOOD_REPORT.md` documents the observations, per-stage outcomes, reasons and measurements
for three reopens, self-detected contract violations, silhouette ownership, retirement
policy, and the finishing pass that intentionally exceeded the P5 ceiling.
`mechanical_audit.json` contains the result of the bundled `tools/audit_fresh_worker.py`
check and passed with zero warnings.

`checkpoint.json` contains more than 43,000 lines, so it must not be provided to a future
agent as a whole. Query only the stage/action/reopen ranges that are relevant to the next
edit. The starting point for continued work is the parent directory's
[`CONTEXT_CAPSULE.md`](CONTEXT_CAPSULE.md).

## 03_stage_reviews — Stage review evidence

This directory contains the current artifact for each stage, structured review records,
worker packets, pass memory, frozen stage contracts, and subject-to-drawing comparison
boards. Overlay/difference boards and local review crop images were omitted for size;
their manifests are included, while the complete originals remain in the session directory.

## 04_abandoned_branches — Abandoned branches

These are JSON/MD review records from earlier branches invalidated by reopens. They are not
the current source of truth; they document why a previous branch was rolled back.

## 05_scripts — Execution scripts

These Python scripts drew the individual stages. They preserve all coordinates and their
observation evidence (`source_observation`) for reproducibility.

## Note

The final image **intentionally exceeds** the P5 clean block-in detail ceiling because the
task required the person to be identifiable, not merely recognizable by form and pose.
This pass is recorded separately in `identity_pass.json` and distinguished from the audited
five-stage croquis.
