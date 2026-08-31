# Legacy R23 compatibility route

이 문서는 기존 `DrawingRun` 작업을 이어갈 때만 읽는다. 새 작업의 canonical
경로가 아니다.

## Scope

R23은 다음을 보존한다.

- `DrawingRun`과 stage registry를 사용하는 기존 checkpoint/resume
- P1–P6 stage contract, stage review, local review, pass memory
- legacy manifest와 reopen 기록의 provenance

이 자산은 역사·회귀·호환성용이다. vNext의 drawing quality PASS나 새 작업의
기본 지침으로 승격하지 않는다.

## Compatibility entry points

- runtime: `img2drawing.run.DrawingRun`
- stage guidance: [`stages/`](stages/) (directory marker identifies this as legacy)
- stage-oriented playbooks: [`../playbooks/`](../playbooks/) (directory marker identifies this as legacy)
- legacy review helpers: [`../src/img2drawing/review/`](../src/img2drawing/review/)
- stage-coupled documentation: [`review/`](review/) and
  [`worker/autonomous-worker-contract.md`](worker/autonomous-worker-contract.md)

기존 R23 checkpoint를 재개할 때만 위 경로를 따라가며, vNext 작업에서는
[`../SKILL.md`](../SKILL.md)의 canonical route와 `img2drawing.DrawingSession`을
사용한다. R23 지침을 vNext API에 섞거나 Pn을 새 mode의 lifecycle로 재사용하지 않는다.

## Migration rule

R23 지식에서 gesture, masses, balance, limb curvature, attached-object topology,
contour selection, face/hair relation 같은 drawing knowledge가 필요하면 먼저
stage-free references를 읽는다. stage ownership, `advance`, `reopen_stage`,
manifest closure는 호환성 경계 밖으로 가져오지 않는다.
