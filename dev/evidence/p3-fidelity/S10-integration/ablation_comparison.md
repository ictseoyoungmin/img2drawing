# S10 real subject A/B/C ablation comparison

## Conditions

- **A** — subject + frozen stage contract
- **B** — subject + frozen contract + existing full-body exemplar
- **C** — subject + frozen contract + scoped modular grammar cards

Each condition used the same subject and P1→P5 pipeline in an isolated
`drawings/s10-ablation/` folder. Each final pass was instructed to include the
identity bundle: eyes, nose, mouth, short bob, tactical jacket/shorts, socks,
boots, and rifle topology. Exemplar material never had pose/coordinate authority.

## Mechanical run comparison

| Condition | Actions | Identity-role actions | Stage review passes | Reopens | Timelapse |
|---|---:|---:|---|---:|---|
| A subject+contract | 331 | 82 | P1 2 / P2 2 / P3 3 / P4 3 / P5 2 | 0 | every_n=4, 84 frames |
| B full-body exemplar | 121 | 22 | P1 2 / P2 2 / P3 2 / P4 2 / P5 1 | 0 | GIF present |
| C modular cards | 122 | 22 | P1 2 / P2 2 / P3 2 / P4 2 / P5 1 | 0 | every_n=4, 32 frames |

These counts measure process effort and authored strokes, not likeness.

## Independent blind visual result

The image-only evaluator inspected only the subject and the three final rasters.

- **A is clearly strongest**, retaining the only visible bundle of bob/face
  marks, tactical clothing cues, boots, and a rifle silhouette. It is still too
  schematic for a professional likeness: head scale, torso turn, near-arm
  volume, and rifle topology remain weak.
- **B and C are near-duplicate generic figures.** Their action logs contain
  identity strokes, but the final raster does not make the bob, readable face,
  tactical garment topology, near-arm width, boots, or rifle components
  reliably visible.
- **C shows no visible improvement over B** in this single-subject trial.

The condition result is therefore `REVISE` for A, B, and C. This is a visual
sample result, not a statistical causal claim; it does establish that the
expected modular-card transfer was not observable in this run.

## Earliest residuals

1. P1/P2: over-shoulder head direction, back-three-quarter torso orientation,
   near-arm exposure, rifle major axis.
2. P3: head/hair mass, near-arm width, torso/pelvis asymmetry, rifle topology.
3. P4/P5: face marks, bob bangs/locks, tactical straps/patch/pockets, shorts and
   thigh rig, rifle component transitions, and heavy boot construction.

Do not use B/C's mechanical `ADVANCE` as visual proof. The next correction pass
must start at P1/P2 and preserve the identity bundle through P5.

## Evidence

- Blind report: `blind_ablation_report.md`
- Machine summary: `real_ablation_report.json`
- A: `drawings/s10-ablation/A_subject_contract/`
- B: `drawings/s10-ablation/B_full_body_exemplar/`
- C: `drawings/s10-ablation/C_modular_grammar_cards/`
