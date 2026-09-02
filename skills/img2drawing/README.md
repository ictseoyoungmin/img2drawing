# img2drawing runtime and Agent Skill

img2drawing is an observation-first, stage-free drawing runtime. Its canonical public
surface is `DrawingSession`; an Agent authors explicit strokes, records bounded visual
evidence, corrects a selected residual, and produces replayable output from one history.

The Python wheel contains the runtime, required JSON data, license, and notice. The source
distribution additionally contains the Agent Skill, canonical references, support and
migration guidance, and the selected observed and subjectless mechanical examples.

Start with `SKILL.md` for Agent operation, `SUPPORT.md` for the public boundary,
`FREEZE.md` for the dogfood contract, and
`examples/` for deterministic integration mechanics. These examples prove API and
artifact behavior only; they make no claim about general drawing quality.
