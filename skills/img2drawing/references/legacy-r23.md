# Legacy R23 compatibility route

Read this document only when continuing an existing `DrawingRun`. It is not the
canonical route for new work.

## Scope

R23 preserves:

- existing checkpoint/resume behavior using `DrawingRun` and the stage registry;
- P1–P6 stage contract, stage review, local review, pass memory
- provenance for legacy manifests and reopen records.

These assets exist for history, regression, and compatibility. Do not promote
them into a vNext drawing-quality PASS or default guidance for new work.

## Compatibility entry points

- runtime: `img2drawing.run.DrawingRun`
- stage guidance: [`stages/`](stages/) (directory marker identifies this as legacy)
- stage-oriented playbooks: [`../playbooks/`](../playbooks/) (directory marker identifies this as legacy)
- legacy review helpers: [`../src/img2drawing/review/`](../src/img2drawing/review/)
- stage-coupled documentation: [`review/`](review/) and
  [`worker/autonomous-worker-contract.md`](worker/autonomous-worker-contract.md)

Follow the paths above only when resuming an existing R23 checkpoint. For vNext
work, use the canonical route in [`../SKILL.md`](../SKILL.md) and
`img2drawing.DrawingSession`. Do not mix R23 guidance into the vNext API or reuse
Pn as the lifecycle of a new mode.

## Migration rule

When you need drawing knowledge from R23—gesture, masses, balance, limb curvature,
attached-object topology, contour selection, or face/hair relationships—read the
stage-free references first. Do not carry stage ownership, `advance`,
`reopen_stage`, or manifest closure beyond the compatibility boundary.
