# img2drawing

An Agent Skill that makes Claude (or any Codex-style coding agent with skill support)
**actually draw** — with explicit, inspectable pencil strokes — instead of generating
an image.

With a readable reference, the agent observes the pose and authors explicit whole-figure
relationships before refining contour, value, and identity. Without a reference, it uses
declared imaginative goals and drawing-only evidence—never a fabricated subject or
overlay. Both routes render and inspect the current drawing before correction.

The ordered JSON action log and checkpoint keep every revision inspectable, resumable,
and replayable. See the deterministic [observed](skills/img2drawing/examples/observed/README.md)
and [subjectless](skills/img2drawing/examples/subjectless/README.md) integration examples.
They demonstrate mechanics, not general artistic quality. Curated historical results live
in the [showcase](showcase/README.md).

## Why this exists

Image generation models produce a finished image in one shot with no inspectable
intermediate reasoning. img2drawing does the opposite: it drives a real stroke-based
drawing session through explicit agent-authored construction marks, where the agent is the
one deciding pose, anatomy and correctness — the runtime only renders, checkpoints, and
hands back evidence for the agent to judge. Every stroke and revision is recorded and
replayable.

## Status

Pre-1.0 release candidate (`0.6.0rc1`, release slice B17). The stage-free vNext product
surface is frozen for validation through B18: one `DrawingSession` carries
observation/construction, bounded inspection,
residual correction, orthogonal `DrawingIntent`, finish-specific authoring guidance,
intent/state/inspection-bound completion provenance, and immutable observed, imaginative,
or hybrid reference authority. Subjectless sessions use drawing-only evidence rather than
fabricating a reference image, overlay, registration, or subject-space measurement.
Croquis, figure drawing, tonal study, line study, and free-draw resolve to distinct
plain-data guidance while sharing that same session/history/inspection/output core.
Three compact style presets, explicit one-base overrides, and complete structured custom
guidance affect Agent-authored marks only; they never replace the persisted renderer.
Derived authored-element lookup and bounded summaries make current/superseded stroke and
fill responsibility navigable without adding a second history or ownership lifecycle.
Canonical vNext PNG, cursor replay, and GIF export share one persisted `RenderProfile`
and renderer; the latest replay frame is checked against an independently rendered final.
Legacy R23 review and recovery remain available for compatibility and historical
comparison; they are not the default vNext loop. Intent-aware completion binds an Agent
decision to the exact current intent, drawing, action cursor, and inspection; it does not
automatically judge quality. See [`dev/CHANGELOG.md`](dev/CHANGELOG.md) for release history.

## Requirements

- Python 3.10+
- `numpy`, `Pillow` (installed automatically); `pytest`, `jsonschema`, `build` for the
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
autonomous loop and operating spec. See
[`skills/img2drawing/SUPPORT.md`](skills/img2drawing/SUPPORT.md) for the public API matrix
and [`skills/img2drawing/MIGRATION.md`](skills/img2drawing/MIGRATION.md) only when handling
an old checkpoint.

## How it's organized

```
.
├── showcase/          # curated, human-facing results and comparison pages
│   ├── README.md      # showcase index
│   └── entries/       # one page and its display assets per result
├── skills/
│   └── img2drawing/   # deployable skill, runtime, canonical references, and examples
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
