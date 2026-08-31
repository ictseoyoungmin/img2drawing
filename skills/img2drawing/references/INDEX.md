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

## Legacy R23 compatibility (new work must not use)

- `legacy-r23.md`: 유일한 compatibility gateway
- `stages/`: P1–P6 stage guidance와 historical images
- `../playbooks/`: `DrawingRun` continuation playbooks
- `stages/stage-contracts.md`: legacy representation contracts
- stage-coupled review helpers such as `review/dual-reference-review.md`,
  `review/fresh-worker-defect-closure.md`, `review/local-review-api.md`,
  `review/reference-authority.md`, `review/reopen-recovery.md`,
  `review/self-visual-audit.md`, `review/when-to-advance.md`, and
  `review/worker-pass-memory.md`: 기존 R23 실행을 이어갈 때만 읽는다.
- `worker/autonomous-worker-contract.md`: legacy worker packet contract; new work uses
  this file's canonical route instead.

R23 자료는 history, regression, migration 근거다. 새 작업의 geometry authority,
visual PASS, mode lifecycle, 또는 canonical reading route가 아니다.
