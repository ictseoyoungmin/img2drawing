# When to advance

Advance only after inspecting the exact current artifact and making an explicit Agent
judgement. The harness verifies freshness and order, not artistic correctness.

Before `advance`, inspect all of:

- raw whole drawing;
- subject beside the drawing;
- same-coordinate subject/drawing overlay;
- every mandatory high-risk crop for the current stage.

Write falsifiable stage-purpose assertions and mark them `PASS`, `FAIL` or `UNCERTAIN`.
One `FAIL`, one critical `UNCERTAIN`, missing evidence, stale evidence or a newly found
residual mismatch means `decision="revise"`, not advance. A correction action or reduced
concern count is not proof of visual improvement.

If the failed structure belongs to an earlier stage's `must_preserve` information, reopen
the earliest responsible stage with `run.reopen_stage()` and rebuild downstream evidence.
See [self-visual-audit.md](self-visual-audit.md) for the blind self-review procedure.
