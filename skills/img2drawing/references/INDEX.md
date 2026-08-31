# Reference index

새 작업은 아래 stage-free 경로에서 시작한다. 이 문서의 순서는 runtime lifecycle이
아니라 필요할 때 꺼내 읽는 지식 분류다.

## Canonical vNext references

- `observation/visual-observation.md`: whole → region → part → relation 관찰과
  evidence 경계
- `construction/gesture-and-masses.md`: pose, flow, head/ribcage/pelvis mass
- `construction/balance-and-limbs.md`: balance, joints, limbs, feet, occlusion
- `figure/limbs-joints.md`: body chain과 garment landmark 함정
- `figure/attached-objects.md`: prop axis, volume, topology, body contact
- `resolution/contour-and-overlap.md`: contour ownership과 explicit stroke retirement
- `finish/identity-and-value.md`: identity relation, value family, edge, accent
- `review/correction-loop.md`: 한 줄짜리 residual loop
- `review/residual-correction.md`: inspect → prioritize → correct → re-inspect
- `review/stroke-retirement.md`: history-preserving soft-lift/delete semantics
- `pencil/graphite.md`: canvas-bound pencil material and selective accent

## Drawing modes (guidance, not stages)

- `modes/croquis.md`
- `modes/figure-drawing.md`
- `modes/tonal-study.md`
- `modes/free-draw.md`

각 mode는 목적, 관찰 우선순위, 추천 grammar, 생략, completion 질문만 제공한다.
`phase_start`, `advance`, `close`, `reopen` state를 만들지 않는다. `DrawingIntent`,
StyleGuide, RenderProfile schema는 B08 이후에 동결한다.

## Legacy R23 compatibility

Existing R23 runs only: [`legacy-r23.md`](legacy-r23.md).

The gateway links to the preserved stage, playbook, and review compatibility material.
New work must not follow that route or use its Pn lifecycle as a mode or finish contract.
