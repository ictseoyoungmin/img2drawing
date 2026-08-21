# Autonomous stage hardening

This playbook exists so a fresh worker does not require interactive coaching.

## Worker behavior
1. Start from the current stage only.
2. Read its `StageSpec` and stage reference.
3. Observe the subject at whole scale before local crops.
4. Draw only enough strokes to test the stage hypothesis.
5. Call `prepare_stage_review()`.
6. Open the generated `worker_packet.md`.
7. Inspect every mandatory comparison plus stage-relevant crops.
8. Separate subject fidelity from exemplar/stage fidelity.
9. State concrete visible mismatches.
10. Correct the highest-impact 1–3 issues locally.
11. Prepare a fresh review after every mutation.
12. Repeat until the stage's `advance_when` guidance is satisfied.
13. Advance without asking the user for routine permission.
14. Reopen an earlier stage if later evidence proves its foundation wrong.

## Anti-patterns
- passing a stage because required objects/lines merely exist;
- converting artistic judgement into hardcoded booleans;
- copying pose from an exemplar;
- asking the user to identify every mismatch;
- moving forward because the pipeline is complete while the current artifact is visibly weak;
- repeated local tweaks without changing observation strategy when the same error persists.

## Plateau rule
If the same concern survives three consecutive passes:
- stop editing;
- create a more informative crop/overlay;
- re-observe the subject and exemplar independently;
- rewrite the stroke plan;
- then resume.

Plateau is a signal to improve observation, not to ask the user by default.


## Pass continuity
Before pass 2+, read the generated `pass_memory.json` / worker-packet memory section.

Start by re-checking carried concerns. Inspect the effect of inter-pass correction
actions on fresh artifacts. Do not repeat a failed edit merely because the previous
pass used it, and do not assume an edit succeeded because the action completed.

The review should reduce, retain, or reframe concerns only through explicit Agent
judgement from fresh evidence.
