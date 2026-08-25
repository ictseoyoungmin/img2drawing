# S10 real subject A/B/C ablation comparison

> Historical record: the original C runner serialized modular cards as
> condition metadata but did not bind them to the `DrawingRun` action path.
> Therefore the C-over-B raster comparison below is descriptive only, not a
> test of the modular-card effect. The corrected strict-binding run is recorded
> in `blind_normalized_ablation_report.md` and
> `drawings/s10-ablation/C_modular_grammar_cards_bound_v2/`.

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

### Important confound

This first real-subject comparison is not a clean causal estimate of exemplar
versus modular-card policy. Condition A authored 82 identity-role actions across
331 total actions, while B and C authored only 22 identity-role actions across
121/122 total actions. The blind result proves that the B/C executions did not
make the requested identity bundle visibly legible; it does **not** prove that
the exemplar or card policy inherently caused the weaker result. A normalized-
detail-budget rerun is required before attributing the visual gap to the
condition itself.

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
- **C shows no visible improvement over B** in this historical single-subject
  trial; because C cards were not runtime-bound, this cannot be attributed to
  the card policy.

The condition result is therefore `REVISE` for A, B, and C. This is an
image-only sample result, not a statistical causal claim. Expected modular-card
transfer was not observable under the unequal identity-detail budgets, so the
condition effect remains unresolved.

## Earliest residuals

1. P1/P2: over-shoulder head direction, back-three-quarter torso orientation,
   near-arm exposure, rifle major axis.
2. P3: head/hair mass, near-arm width, torso/pelvis asymmetry, rifle topology.
3. P4/P5: face marks, bob bangs/locks, tactical straps/patch/pockets, shorts and
   thigh rig, rifle component transitions, and heavy boot construction.

Do not use B/C's mechanical `ADVANCE` as visual proof. First rerun B and C with
an A-equivalent identity-detail budget and the same final-detail inventory;
then start the correction pass at P1/P2 and preserve that bundle through P5.

## Evidence

- Blind report: `blind_ablation_report.md`
- Machine summary: `real_ablation_report.json`
- A: `drawings/s10-ablation/A_subject_contract/`
- B: `drawings/s10-ablation/B_full_body_exemplar/`
- C: `drawings/s10-ablation/C_modular_grammar_cards/`
