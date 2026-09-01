# img2drawing

An Agent Skill that makes Claude (or any Codex-style coding agent with skill support)
**actually draw** — with explicit, inspectable pencil strokes — instead of generating
an image.

Given one reference photo, the agent reads the pose and authors an ordered whole-figure
construction (line of action → head/ribcage/pelvis masses → balance/plumb → joints/limbs),
then renders and inspects the actual drawing before adding detail. The legacy five-stage
pipeline remains available for compatibility, but is not the default vNext workflow.

![Sniper Girl croquis timelapse](showcase/entries/croquis-sniper-girl-opus5-r22/croquis_timelapse.gif)

- **Model:** Claude Opus 5
- **Skill:** img2drawing `0.5.2.dev23` · release slice `R23`
- **Prompting:** single initial prompt

This is the result of an autonomous run started from a single user prompt. The work does
not end with the finished drawing: the same or another agent can continue editing it using
the JSON action log and checkpoint. Because `checkpoint.json` contains more than 43,000
lines, agents should query only the required stage/action/reopen ranges instead of reading
the entire file.

[Detailed showcase entry](showcase/entries/croquis-sniper-girl-opus5-r22/README.md) ·
[Full showcase](showcase/README.md)

![img2drawing subject-only P1→P5 progression](dev/dogfood/target-subject/img2drawing-r21-target-progression.png)

## Why this exists

Image generation models produce a finished image in one shot with no inspectable
intermediate reasoning. img2drawing does the opposite: it drives a real stroke-based
drawing session through explicit agent-authored construction marks, where the agent is the
one deciding pose, anatomy and correctness — the runtime only renders, checkpoints, and
hands back evidence for the agent to judge. Every stroke and revision is recorded and
replayable.

## Status

Pre-1.0 (`0.5.2.dev23`, release slice R23). The stage-free vNext product surface is closed
through B09: one `DrawingSession` now carries observation/construction, bounded inspection,
residual correction, orthogonal `DrawingIntent`, and finish-specific authoring guidance.
Legacy R23 review and recovery remain available for compatibility and historical
comparison; they are not the default vNext loop. B10 intent-aware completion is the sole
active implementation slice. See [`dev/CHANGELOG.md`](dev/CHANGELOG.md) for release history.

## Requirements

- Python 3.10+
- `numpy`, `Pillow`, `svgwrite` (installed automatically); `pytest`, `jsonschema` for the
  `dev/` test suite (`pip install "skills/img2drawing/[dev]"`)
- A coding agent that supports Agent Skills (Claude Code, Claude.ai, or similar)

## Install

**As an agent skill** — copy the skill folder into wherever your agent loads skills
from:

```bash
cp -r skills/img2drawing /path/to/your/skills/
```

Or package it into a distributable `.skill` file (a plain zip) with your agent's
skill-packaging tooling (e.g. Anthropic's `skill-creator`), and install that instead.

**As a Python library** (the skill's own runtime code, usable standalone):

```bash
pip install skills/img2drawing/
```

## Quickstart

```python
from img2drawing import DrawingIntent, DrawingSession, resolve_finish_guide

intent = DrawingIntent(drawing_mode="croquis", finish_intent="subject")
session = DrawingSession.create(subject="subject.png", output_dir="out", intent=intent)
finish = resolve_finish_guide(intent.finish_intent)
```

The agent then records a short `PoseObservation`, authors explicit ordered
`ConstructionMark`s inside an `InitialConstruct`, calls
`author_initial_construct(session, construct)`, and inspects it with
`inspect_initial_construct(session, construct)`. The Agent reads `finish` to select
relational mark/value/edge decisions; the guide does not mutate or close the session. See
[`skills/img2drawing/SKILL.md`](skills/img2drawing/SKILL.md) for the complete
autonomous loop and operating spec. `DrawingRun` and the P1–P5 stage loop remain
available for legacy continuations.

Run the bundled subject-only benchmark (dev-side regression fixture, not part of the
shipped skill):

```bash
python dev/benchmarks/stage_reconstruction/full_body_croquis_subject_only/run_smoke.py
```

## How it's organized

```
.
├── showcase/          # curated, human-facing results and comparison pages
│   ├── README.md      # showcase index
│   └── entries/       # one page and its display assets per result
├── skills/
│   └── img2drawing/   # the deployable skill: SKILL.md, runtime source, references,
│                       # playbooks, references — everything that ships
├── dev/                # release builds, dogfood runs, verification evidence,
│   ├── dogfood/        # persistent reproducible runs and continuation records
│   ├── tests/          # pytest suite for skills/img2drawing's runtime
│   ├── schemas/        # JSON schemas used by the test suite (not runtime-loaded)
│   ├── tools/           # dev-side audit scripts (fresh-worker evidence audit, etc.)
│   ├── benchmarks/      # regression/smoke fixtures for the drawing pipeline
│   └── ...             # release artifacts, audits, and the changelog
└── temp/               # ignored scratch space for unpromoted runs
```

`skills/img2drawing/` is self-contained and independently packageable; everything
under `dev/` supports developing, reproducing, and releasing it but never ships inside
the skill itself. `showcase/` contains lightweight curated copies of selected outputs;
the corresponding full run records live under `dev/dogfood/`. `temp/` is disposable and
should not be used as the long-term source of a showcase entry or a continuation run.

## Contributing

Issues and pull requests are welcome. If you're extending the drawing pipeline itself,
start with [`skills/img2drawing/SKILL.md`](skills/img2drawing/SKILL.md) — it's both the
spec the agent reads and the source of truth for how the runtime is meant to be used.

## License

Copyright 2026 ictseoyoungmin. Licensed under the Apache License, Version 2.0 — see
[LICENSE](LICENSE).
