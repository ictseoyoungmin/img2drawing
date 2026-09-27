Status: **PREPARED / USER-ACCEPTED WITHOUT COMPLETED RUNS**

# S03 simple-subject campaign

Date: 2026-09-26
Decision: current user-directed validation scope after the human-figure pilot remained too difficult.

The prior Gojo batch and the 2026-09-25 generated-figure campaign are retained as historical/pilot
runs. They do not count toward this release verdict. Current inputs are four original, deliberately
simple still-life targets. `image_gen` was attempted for these targets but the service returned a
usage-limit error (reported reset: 2026-09-28 13:30:56 UTC); to keep the user-approved scope moving, the
reference-only targets were authored as small original SVG compositions and rendered to PNG. Their
SVG source files are retained beside the PNGs. No generated or hand-built image may be used as a
final drawing; workers must author through the current public img2drawing runtime.

## Boundaries

- Each isolated `gpt-6-luna` worker receives only the current deployable skill/runtime, one pinned
  reference, and its ordinary drawing request. Do not share other workers' references, sessions,
  outputs, reviews, or feedback.
- Use `PYTHONPATH=skills/img2drawing/src` so the run imports this worktree's `1.1.0.dev0` source.
- No tracing, image paste, hand-authored raster drawing, SVG/canvas drawing, or raster repair for
  the final output. Use the public `DrawingSession` runtime.
- Preserve canonical action 0 through latest, final PNG, runtime-exported GIF, replay manifest,
  comparison board, residual review, and KEEP/SOFTEN/RETIRE audit.
- The claim is limited to these four simple still-life subjects. It does not establish broad figure,
  hand, foreshortening, hair, or real-reference generalization.

## Fixed reference inputs

| Class | Reference | SHA-256 | Target |
| --- | --- | --- | --- |
| S03.1 | `references/apple.png` | `c960d945e30be1618cbff39171bf42937e5869ad7fab671baef98edc0b16c11c` | Apple, leaf, tabletop shadow |
| S03.2 | `references/mug.png` | `bdbefc3375c31b326ab4f69fbba58c955e306974c78f1358e003c9ebccd87e44` | Ceramic mug and single handle |
| S03.3 | `references/umbrella.png` | `de87a334ac1b180e3b48326bb3630f3659491b13956158fd25b20b0b0f838df5` | Closed umbrella, plain wall and floor |
| S03.4 | `references/plant.png` | `98d376c8fdb5037c9e15d45b7e7c10c2360d0de4dc11b3bbb8015062975f2a5a` | Potted plant with four broad leaves |

The earlier image_gen figure pilot was retained locally as a superseded experiment. Its large generated references and run outputs are excluded from Git. On 2026-09-27, the user accepted the S03 dogfood gate without a completed still-life run; see `USER_ACCEPTANCE_2026-09-27.md`.
