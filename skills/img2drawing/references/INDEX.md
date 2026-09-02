# Reference index

Start new work on the stage-free route below. The order in this document is a
knowledge taxonomy to consult as needed, not a runtime lifecycle.

## Canonical vNext references

- `observation/visual-observation.md`: whole → region → part → relation observation
  and the evidence boundary
- `observation/measuring-boundaries.md`: what a line separates, the material palette,
  and avoiding unobserved terminals
- `construction/gesture-and-masses.md`: pose, flow, head/ribcage/pelvis mass
- `construction/balance-and-limbs.md`: balance, joints, limbs, feet, occlusion
- `figure/limbs-joints.md`: body chains and garment-landmark traps
- `figure/attached-objects.md`: prop axis, volume, topology, body contact
- `resolution/contour-and-overlap.md`: contour ownership and explicit stroke retirement
- `finish/identity-and-value.md`: identity relation, value family, edge, accent
- `value/tone-and-fill.md`: region fill, calibrated tone scale, reserved lights
- `review/correction-loop.md`: the one-line residual loop
- `review/residual-correction.md`: inspect → prioritize → correct → re-inspect
- `review/completion.md`: bind the Agent's finish decision to current intent/state/evidence
- `output/render-profile-and-replay.md`: canonical PNG, cursor replay, GIF, parity, migration
- `review/stroke-retirement.md`: history-preserving soft-lift/delete semantics
- `review/authored-element-navigation.md`: derived current/superseded stroke/fill lookup,
  bounded context, and one canonical edit surface
- `pencil/graphite.md`: canvas-bound pencil material and selective accent
- `styles/authoring-styles.md`: preset, single-base override, structured custom style,
  precedence, and explicit mid-session edits
- `intent.md`: portable `DrawingIntent`, `ModeGuide`, `FinishGuide`, `StyleGuide`, provenance, and
  compatibility lookup
- `reference-authority.md`: observed, imaginative, and hybrid comparison authority;
  subjectless creation, drawing-only inspection, and explicit unavailable operations

## Drawing modes (guidance, not stages)

- `modes/croquis.md`
- `modes/figure-drawing.md`
- `modes/tonal-study.md`
- `modes/line-study.md`
- `modes/free-draw.md`

Each mode provides only a purpose, observation priorities, suggested grammar,
omissions, and completion questions. It does not create `phase_start`, `advance`,
`close`, or `reopen` state. `DrawingIntent`,
`ModeGuide` and `StyleGuide` began as B08 plain-data schemas and are completed by B14 and
B15 respectively; `FinishGuide` is the B09 plain-data authoring target. `RenderProfile`
is the B11 output/replay contract; style guidance never acts as a renderer filter.

## Legacy R23 compatibility

Existing R23 runs only: [`legacy-r23.md`](legacy-r23.md).

The gateway links to the preserved stage, playbook, and review compatibility material.
New work must not follow that route or use its Pn lifecycle as a mode or finish contract.
