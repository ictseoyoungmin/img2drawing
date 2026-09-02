# img2drawing runtime and Agent Skill

img2drawing is an observation-first, stage-free drawing runtime. Its canonical public
surface is `DrawingSession`; an Agent authors explicit strokes, records bounded visual
evidence, corrects a selected residual, and produces replayable output from one history.

Start with `SKILL.md` for Agent operation and `references/INDEX.md` for the canonical
knowledge route. `examples/` contains deterministic integration mechanics only; they make
no claim about general drawing quality.

This directory is the deployable skill/runtime surface. Release-candidate notes, API
freeze snapshots, migration/support matrices, dogfood control-plane records, and historical
stage/playbook material belong under `dev/` and are intentionally excluded from the skill
attention surface.
