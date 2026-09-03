# img2drawing runtime and Agent Skill

img2drawing is an observation-first, stage-free drawing skill and runtime. The Agent
observes or declares its reference authority, authors explicit strokes, inspects the
current render, corrects the highest-impact residual, and exports replayable output from
one history.

Start with `SKILL.md`. It is a router, not a textbook: use `references/INDEX.md` to load
only the smallest guidance leaf needed for the current task or residual.

This deployable surface intentionally contains no `examples/` directory until curated
examples are strong enough to serve as drawing guidance rather than accidental style or
geometry templates. Drawing knowledge and public API contracts live under `references/`;
implementation details stay in `src/` and are not part of the Agent instruction route.
