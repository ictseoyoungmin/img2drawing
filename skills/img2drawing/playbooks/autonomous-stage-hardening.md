# Autonomous stage hardening

This playbook exists so a fresh worker does not require interactive coaching.

## Worker behavior
1. Start from the current stage only.
2. Read its `StageSpec`, stage reference and `StageContract`.
3. Observe the subject at whole scale before local crops.
4. Draw only enough strokes to test the stage hypothesis.
5. Call `prepare_stage_review()`.
6. Open the generated `worker_packet.md` and read `references/review/self-visual-audit.md`.
7. Inspect the raw whole view, subject beside drawing, same-coordinate overlay and every
   mandatory/high-risk crop.
8. Write falsifiable subject/grammar/drawing assertions and mark each PASS, FAIL or
   UNCERTAIN before reading prior rationale or verdicts.
9. Treat one failed stage-purpose assertion, critical uncertainty or stale/missing view as
   visual FAIL (`decision="revise"`).
10. Separate subject fidelity from stage-grammar fidelity and state concrete visible
    mismatches.
11. Correct the highest-impact 1–3 issues locally, including `delete_stroke` or
    `soft_lift` when representation ownership transfers.
12. Prepare a fresh review after every mutation; an action is not proof of improvement.
13. Repeat until the stage's advance assertions pass and a fresh residual sweep finds no
    new mismatch.
14. If the defect contradicts an earlier stage's `must_preserve` data, stop local patching
    and call `run.reopen_stage()` for the earliest responsible stage.
15. Advance without asking the user for routine permission only after both process and
    visual findings pass.

## Anti-patterns
- passing a stage because required objects/lines merely exist;
- converting artistic judgement into hardcoded booleans;
- copying pose from an example image;
- asking the user to identify every mismatch;
- moving forward because the pipeline is complete while the current artifact is visibly weak;
- treating a process-complete packet or plausible crop as visual proof;
- writing a blind visual verdict from the worker's own rationale before inspecting the raw
  whole view and overlay;
- repeated local tweaks without changing observation strategy when the same error persists.

## Plateau rule
If the same concern survives three consecutive passes:
- stop editing;
- create a more informative crop/overlay;
- re-observe the subject and re-read the stage contract independently;
- rewrite the stroke plan;
- then resume.

Plateau is a signal to improve observation, not to ask the user by default.


## Pass continuity
Before pass 2+, read the generated `pass_memory.json` / worker-packet memory section
and start from its carried concerns. See "Worker Pass Memory" in `SKILL.md` and
`references/review/worker-pass-memory.md` for what that memory carries and what it
must not be used to infer.
