# Drawing intent and authoring guidance

`DrawingIntent` is a portable declaration of what the Agent is trying to make. It is
not a workflow state machine. The four axes are independent and can be combined without
deriving a hidden stage:

```python
from img2drawing import (
    DrawingIntent, DrawingSession,
    resolve_finish_guide, resolve_mode_guide, resolve_style_guide,
)

intent = DrawingIntent(
    reference_mode="observed",
    drawing_mode="croquis",
    finish_intent="pose",
    style_profile="pencil_loose",
)
session = DrawingSession.create(subject="subject.png", output_dir="out", intent=intent)
mode = resolve_mode_guide(intent.drawing_mode)
finish = resolve_finish_guide(intent.finish_intent)
style = resolve_style_guide(intent.style_profile)
```

The current production session still requires `subject` to be a readable image. An
imaginative, hybrid, or `free_draw` intent can be recorded and used as guidance, but a
subjectless blank-canvas session is not implemented yet; later mode slices own that
behavior. If no reference is available, state the limitation instead of calling
`DrawingSession.create()` and promising an output.

The allowed values are:

- `reference_mode`: `observed`, `imaginative`, `hybrid`
- `drawing_mode`: `croquis`, `figure_drawing`, `tonal_study`, `free_draw`
- `finish_intent`: `pose`, `subject`, `form_light`, `expressive`
- `style_profile`: `pencil_loose`, `graphite_academic`, or an explicit
  `custom:<identifier>` for prose that the Agent structures itself

`session.set_intent(next_intent, reason="...")` appends an `IntentChangeRecord` containing
the full data snapshot, previous digest, reason, and current action-history cursor. It
does not mutate strokes, invalidate an action, or fork a second history. A checkpoint
stores the current intent and its provenance; old sessions with no intent continue to
resume normally.

## ModeGuide

`resolve_mode_guide(drawing_mode)` returns immutable plain data containing:

- primary observations;
- a recommended (not gated) grammar;
- typical omissions;
- finish emphasis; and
- completion questions for the Agent to answer.

The guide contains no phase count, stage, cursor, advance/close operation, or visual
verdict. If inspection contradicts the current hypothesis, select a different intent or
read the guide again; nothing needs to be reopened or advanced.

## StyleGuide

`resolve_style_guide(style_profile, overrides=None)` returns direct authoring advice for
line behavior, construction visibility, detail, value, edges, and notes. The two B08
bases are `pencil_loose` and `graphite_academic`. Overrides replace explicit fields on
one base only; unknown fields, a second base, inheritance, and plugin registries are
rejected. The advice must be enacted in authored strokes. It is not a renderer selector
or a post-filter for an already rendered PNG.

## FinishGuide

`resolve_finish_guide(finish_intent)` returns an immutable authoring policy for `pose`,
`subject`, `form_light`, or `expressive`. It contains priorities, constraints to preserve,
mark/value/edge policies, deliberate omissions, relational observations, and questions
for the Agent. The relation records say what to observe, how to author it, and which
shortcuts to avoid.

The guide does not mutate geometry or history. The Agent reads it and authors explicit
`draw()`, `fill_region()`, or correction actions through the existing session. It has no
finish stage, cursor, likeness score, PASS/FAIL, or close operation. `pose` preserves an
economical macro statement; `subject` adds relational recognition; `form_light` requires
form-before-value; and `expressive` records constraints before selective simplification.

Guide precedence is deliberate: subject/reference geometry and explicit preserved
constraints outrank finish advice, and finish advice outranks a conflicting style
preference. See [`finish/identity-and-value.md`](finish/identity-and-value.md) for the
canonical finish method. Completion recording is a separate later capability; these
questions do not certify that the drawing is done.

## Compatibility lookup

For an existing naming convention only, `compatibility_intent("full_body_croquis")`
returns an ordinary `DrawingIntent(reference_mode="observed", drawing_mode="croquis", ...)`
with a compatibility provenance key. The alias is a lookup, not a mode, stage, or
completion state.
