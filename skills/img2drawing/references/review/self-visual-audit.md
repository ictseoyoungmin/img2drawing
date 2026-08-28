# Self visual audit and fail-closed review

The runtime can prove that a review artifact is fresh and bound to the current drawing.
It cannot prove that the drawing communicates the subject correctly. The Agent must make
that visual judgement from rendered evidence.

## Required evidence order

After every mutation, inspect the current raw render in this order:

1. **Whole view** — balance, proportion, dominant gesture, occupied envelope and overall
   read. Do not judge only an enlarged crop.
2. **Subject beside drawing** — confirm that the stage's purpose is present in the drawing,
   not merely that the strokes look plausible on white paper.
3. **Subject/drawing overlay** — check registration, width, turn, overlap and negative
   space at the same canvas coordinates. A crop that was resized for presentation is not
   proof of alignment.
4. **High-risk crops** — inspect the regions most likely to fail the current stage. The
   Agent chooses the boxes, but may not choose them only because they look good.

The raw drawing remains the material authority. Contrast-enhanced, recoloured or
automatically scored views may help locate evidence but cannot turn a mismatch into PASS.

## Assertion matrix

Write concrete, falsifiable assertions for the current stage before deciding. For each
assertion record:

- what the subject visibly does;
- what the drawing visibly does;
- the discrepancy, if any;
- the correction or reason it is accepted.

Use `PASS`, `FAIL` or `UNCERTAIN` per assertion in the review notes. These labels are an
Agent review convention; the public stage decision remains `revise | advance`.

Rules:

- One failed **stage-purpose** assertion is a visual FAIL and requires `decision="revise"`.
- An unresolved uncertainty in a critical region is not PASS. Keep `revise`, or use
  `accept-with-rationale` only for explicit occlusion/observation uncertainty permitted
  by the closure manifest.
- An edit, lower concern count or plausible isolated crop is not evidence that a concern
  was cleared. Re-render and inspect the changed region and the whole view again.
- A newly discovered mismatch in the residual sweep reopens the review loop even when all
  carried concerns were cleared.
- Process/contract PASS never overrides a visual FAIL.

## Blind self-review

When a second evaluator is unavailable, separate the worker and visual-evaluator roles:

1. Finish the drawing mutation and prepare the review artifacts.
2. Read only the subject, frozen observation projection, current drawing, stage contract
   and selected evidence. Do not read the worker's rationale, previous verdict or
   correction claim before writing the visual findings.
3. Judge whole view, overlay and high-risk crops using the assertion matrix.
4. Write the visual-fidelity record first. Then write the process review and reconcile the
   two records.

The blind packet is a context boundary, not proof of artistic truth. Do not give the same
evaluator's prior advance rationale back to itself as evidence, and do not use an evaluator
id to claim independence that did not occur.

## Fail versus reopen

Use the earliest responsible stage, not the stage where the error became visible.

- **Current-stage FAIL:** the subject is observed correctly, but the current stage's mass,
  axis, taper or overlap is wrong. Correct only that stage and prepare fresh evidence.
- **Upstream REOPEN:** the mismatch contradicts an earlier stage's `must_preserve` data,
  or fixing the current stage would hide/compensate for the earlier error. Call
  `run.reopen_stage()` for the earliest responsible stage and rebuild invalidated evidence.
- **Plateau:** the same structural mismatch survives three fresh passes. Stop local
  nudging, improve the observation/crop strategy, rewrite the stroke plan and consider
  reopening the stage that owns the failed structure.

Record the visual FAIL, the evidence that exposed it and the chosen reopen target in the
review findings. Never advance merely because the pipeline has reached a pass count.

