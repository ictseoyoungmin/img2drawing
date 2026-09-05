# img2drawing

**Current stable: v1.0.1**

An Agent Skill that makes Claude, GPT-class coding agents, or other skill-capable coding agents
**actually draw** — with explicit, inspectable pencil strokes — instead of generating a finished
image.

With a readable reference, the agent observes the subject and authors explicit spatial
relationships before resolving contour, form, value, and identity. Without a reference, it uses
declared imaginative goals and drawing-only evidence—never a fabricated subject or fake overlay.
Both routes render and inspect the current drawing before correction.

The action history keeps every revision inspectable, resumable, and replayable. Curated
human-facing results live in the [showcase](showcase/README.md); the deployable skill does not ship
an `examples/` tree until there are genuinely representative instructional examples.

## v1.0.1 — Astra-derived authoring ergonomics

v1.0.1 absorbs reusable mechanics exposed by the successful Astra run without copying its
subject-specific coordinates, scripts, control-point tables, or answer geometry:

- `img2drawing.vnext.retune_stroke()` changes stroke material while preserving authored geometry;
- `img2drawing.vnext.sample_catmull_rom()` provides deterministic shared smooth-curve sampling;
- `continuous_pencil` provides a low-taper option for boundaries whose endpoints should read as
  continuous, while `form_pencil` remains unchanged;
- guidance now separates geometry residuals from material residuals and groups related edits by
  coherent visible/structural problems rather than arbitrary stroke counts;
- curve smoothness follows observed topology: real cusps, corners, joins, and tangency breaks are
  authored explicitly rather than rounded away.

The patch adds no persisted action kind or schema, does not widen the canonical package-root API,
and does not introduce a new drawing lifecycle. [Read the v1.0.1 release notes](docs/releases/v1.0.1.md).

## Featured v1.0.0 demonstration

GPT-6 Astra completed a detailed observed croquis using explicit authored strokes only; the release
baseline adds no subject-specific answer geometry from that run. The session contains 490 actions:
358 stroke additions, 120 replacements, 12 deletions, and **0 fill actions**, with a canonical
replay final frame that exactly matches the final PNG. This is a curated capability result, not a
claim that formal cross-agent/cross-subject validation is complete.

<a href="showcase/entries/croquis-sniper-girl-astra-v1/README.md"><img src="showcase/entries/croquis-sniper-girl-astra-v1/timelapse.gif" alt="End-to-end timelapse" width="320"></a>

[![Reference versus Astra drawing](showcase/entries/croquis-sniper-girl-astra-v1/ref-vs-drawing.jpg)](showcase/entries/croquis-sniper-girl-astra-v1/README.md)

[Read the v1.0.0 release notes](docs/releases/v1.0.0.md)

## Why this exists

Image generation models produce a finished image in one shot with no inspectable drawing process.
img2drawing does the opposite: the agent observes, places real strokes, renders what it actually
authored, compares the result against its reference authority, and corrects the highest-impact
mismatch. The runtime records and replays those authored changes; it does not decide pose, anatomy,
identity, or artistic correctness for the agent.

## Core drawing principle

**Croquis economizes marks, not observed geometry.**

Fewer lines must come from better line selection, not from replacing the subject with a circle
head, tube limbs, box feet, generic hair strands, or symbolic zigzag folds. The instruction graph
under `skills/img2drawing/references/` separates observation, construction, descriptive geometry,
figure-specific knowledge, review, output, and public API usage so a worker can load only the
guidance needed for the current residual.

## Requirements

- Python 3.10+
- `numpy`, `Pillow` (installed automatically); `pytest`, `jsonschema`, `build` for the development
  test suite
- A coding agent that supports Agent Skills

## Install

**As an agent skill** — copy the skill folder into wherever your agent loads skills from:

```bash
cp -r skills/img2drawing /path/to/your/skills/
```

**As a Python library**:

```bash
pip install skills/img2drawing/
```

## Quickstart

```python
from img2drawing import DrawingIntent, DrawingSession

intent = DrawingIntent(drawing_mode="croquis", finish_intent="subject")
session = DrawingSession.create(subject="subject.png", output_dir="out", intent=intent)
```

The agent then observes the subject, authors its own geometry, inspects the current render, and
corrects explicit residuals. See [`skills/img2drawing/SKILL.md`](skills/img2drawing/SKILL.md) for
the operating route and [`skills/img2drawing/references/INDEX.md`](skills/img2drawing/references/INDEX.md)
for the instruction graph.

## How it's organized

```text
.
├── showcase/          # curated, human-facing results and comparison pages
├── docs/releases/     # human-facing release notes
├── skills/
│   └── img2drawing/   # deployable skill, runtime, and canonical instruction graph
├── dev/               # tests, dogfood runs, planning, tooling, and release records
└── temp/              # ignored scratch space for unpromoted runs
```

`skills/img2drawing/` is self-contained and independently packageable. Drawing knowledge and
public usage contracts live in the skill; development and compatibility machinery stay outside
that attention route or inside the runtime implementation.

## Contributing

Issues and pull requests are welcome. For drawing behavior, start with
[`skills/img2drawing/SKILL.md`](skills/img2drawing/SKILL.md) and follow the smallest leaf in the
instruction graph that owns the problem you are changing.

## License

Copyright 2026 ictseoyoungmin. Licensed under the Apache License, Version 2.0 — see
[LICENSE](LICENSE).