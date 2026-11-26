<div align="center">
  <img src="skills/img2drawing/assets/icon.svg" width="96" height="96" alt="img2drawing icon">
  <h1>img2drawing</h1>
  <p><strong>From observation to explicit, editable pencil strokes.</strong></p>
  <p>
    <a href="https://github.com/ictseoyoungmin/img2drawing/releases/latest"><img src="https://img.shields.io/badge/version-v1.3.1-6f5a46" alt="Version v1.3.1"></a>
    <a href="https://github.com/ictseoyoungmin/img2drawing/actions/workflows/ci.yml"><img src="https://github.com/ictseoyoungmin/img2drawing/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
    <img src="https://img.shields.io/badge/python-3.10%2B-3776AB" alt="Python 3.10+">
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-59636e" alt="Apache 2.0"></a>
  </p>
</div>

**Current stable: v1.3.1** · [Releases](https://github.com/ictseoyoungmin/img2drawing/releases) · [Changelog](CHANGELOG.md)

An Agent Skill and Python drawing runtime for Claude Code, Codex, and other skill-capable agents.
Rather than requesting a finished image from an image generator, the agent observes a subject,
authors explicit strokes, inspects its drawing, and corrects visible problems.

**What's new in v1.3**

- Explicit landmark, proportion, occlusion and projected-volume tools for observation and construction.
- Editable curves, pressure/contact-width control, local erasure and atomic stroke/group corrections with previews.
- More focused portrait, hair, anatomy and fabric guidance, plus tonal/overlap inspection.
- Optional normalized graphite profiles, safer action validation, compact GIF export and a standalone skill ZIP.

v1.3.1 strengthens release-contract validation and consolidates development history without changing drawing behavior. Independent artistic-quality comparison was closed by maintainer acceptance, not measured PASS. [Release notes](docs/releases/v1.3.1.md).

## Drawing in action

<p align="center">
  <img src="docs/media/hand-line-studies.gif" width="560" alt="Hand studies drawn through explicit actions">
</p>

[![Observed croquis: reference and drawing](showcase/entries/croquis-sniper-girl-astra-v1/ref-vs-drawing.jpg)](showcase/entries/croquis-sniper-girl-astra-v1/README.md)

[Full drawing timelapse](showcase/entries/croquis-sniper-girl-astra-v1/timelapse.gif) · [Showcase](showcase/README.md)

Curated stroke-authoring examples, not a guarantee of quality across all subjects or agents.

## What it does

- **Observation and construction:** establish proportions, orientation, silhouette, and form from
  a reference or declared imaginative goals.
- **Pencil authoring:** create explicit lines, curves, and tonal strokes with controllable pressure,
  width, grade, and opacity. Tonal plans guide marks without automatic fills.
- **Inspection and correction:** compare the drawing with its reference, locate and revise strokes,
  and retire unnecessary construction marks.
- **Persistent history:** retain drawing actions and the render profile for inspection, resumption,
  and replay.
- **Output:** render PNGs and export end-to-end GIF timelapses from actual drawing actions.

**Croquis economizes marks, not observed geometry.** The agent makes artistic decisions;
the runtime supplies authoring, editing, and evidence tools.

## Install

Python 3.10+ is required. FFmpeg is optional for fast timelapse export.

### Agent Skill

Choose your agent:

```bash
npx skills add ictseoyoungmin/img2drawing --skill img2drawing --agent claude-code
npx skills add ictseoyoungmin/img2drawing --skill img2drawing --agent codex
```

For manual installation, copy only [skills/img2drawing/](skills/img2drawing/) into your agent's
skills directory. Developer test data and historical drawing runs are not needed.

### Python runtime

From a source checkout:

```bash
python -m pip install skills/img2drawing/
```

Packaged Python releases are available on [GitHub Releases](https://github.com/ictseoyoungmin/img2drawing/releases/latest).
On Windows, prefer a short extraction path.

## Quickstart

Give your agent a reference and a drawing goal:

> Read the img2drawing skill. Draw the attached reference with explicit pencil strokes.
> Establish the pose and major forms first, inspect and correct the drawing, and export
> the final PNG and full drawing timelapse. Do not use image generation or tracing.

For programmatic use:

```python
from img2drawing import DrawingIntent, DrawingSession

intent = DrawingIntent(drawing_mode="croquis", finish_intent="subject")
session = DrawingSession.create(
    subject="subject.png", output_dir="out", intent=intent
)

# Observe the reference and author strokes through the session.
# After authoring and inspection:
# session.render_final("out/final.png")
# session.export_timelapse("out/timelapse", every_n=4)
```

Start with [SKILL.md](skills/img2drawing/SKILL.md).
The [public API](skills/img2drawing/references/api/public-surface.md) documents runtime usage;
the [instruction graph](skills/img2drawing/references/INDEX.md) routes drawing knowledge.

## Project structure

```text
skills/img2drawing/    Deployable skill, runtime, drawing guidance
showcase/             Curated results
docs/releases/        Detailed release notes
dev/                  Tests, benchmarks, development tooling
CHANGELOG.md          Version history
```

The skill is self-contained. Development artifacts are kept separate.

## Development

- [Release notes](docs/releases/) · [Development status](dev/planning/vnext/STATUS.md) · [Roadmap](dev/planning/vnext/ROADMAP.md)

Contributions are welcome. Keep private references and generated run outputs outside the repository; prefer small, reproducible tests.

## License

[Apache License 2.0](LICENSE).
