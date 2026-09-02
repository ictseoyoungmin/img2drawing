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

`DrawingIntent.reference_mode` must match the session's immutable `ReferenceAuthority`.
Observed work uses a readable subject; imaginative work uses an explicit canvas and
declared goals; hybrid work separates preserved constraints from deliberate
transformations. See [`reference-authority.md`](reference-authority.md) for creation,
inspection, persistence, and error behavior.

The allowed values are:

- `reference_mode`: `observed`, `imaginative`, `hybrid`
- `drawing_mode`: `croquis`, `figure_drawing`, `tonal_study`, `line_study`, `free_draw`
- `finish_intent`: `pose`, `subject`, `form_light`, `expressive`
- `style_profile`: `pencil_loose`, `graphite_academic`, `graphite_tonal`, or an explicit
  `custom:<identifier>` for prose that the Agent structures itself

`session.set_intent(next_intent, reason="...")` appends an `IntentChangeRecord` containing
the full data snapshot, previous digest, reason, and current action-history cursor. It
does not mutate strokes, invalidate an action, or fork a second history. A checkpoint
stores the current intent and its provenance; old observed sessions with no intent
continue to resume normally. `set_intent()` cannot change `reference_mode`, because that
would silently redefine the comparison authority for existing evidence and residuals.

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

The retained modes are intentionally small and distinct: croquis prioritizes gesture and
line economy; figure drawing carries connected anatomy, garment, contact, and requested
identity; tonal study authors value families, form turns, and edges; line study carries
shape and overlap through economical relational lines; and free-draw follows explicit
composition, focal, gesture, and shape-language goals under any reference authority.
`session.mode_guide` is a derived lookup of the current intent, not persisted mode state.

## StyleGuide

`resolve_style_guide(style_profile, overrides=None)` returns direct authoring advice for
line behavior, construction visibility, detail, value, edges, and notes. The three
retained bases are `pencil_loose`, `graphite_academic`, and `graphite_tonal`. Overrides
replace explicit fields on one base only; unknown fields, a second base, inheritance, and
plugin registries are rejected. A `custom:<identifier>` requires one complete
Agent-structured `StyleGuide`; the runtime does not parse prose or combine it with a base.
Ambiguous terms raise `StyleClarificationRequired`, and explicitly identified conflicts
with task/reference/geometry truth raise `StyleConflictError`.

The advice must be enacted in explicit drawing actions. Changing `style_profile` through
`session.set_intent()` appends intent provenance but does not mutate existing marks or the
`RenderProfile`; actual visual changes use ordinary keep/retire/replace/add operations.
See [`styles/authoring-styles.md`](styles/authoring-styles.md) for the canonical preset,
custom, precedence, and mid-session-edit contract.

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
canonical finish method. The questions still do not certify that the drawing is done;
when the Agent finds no material residual, bind that decision through the separate
[`review/completion.md`](review/completion.md) `FinishRecord` contract.

## Compatibility lookup

For an existing naming convention only, `compatibility_intent("full_body_croquis")`
returns an ordinary `DrawingIntent(reference_mode="observed", drawing_mode="croquis", ...)`
with a compatibility provenance key. The alias is a lookup, not a mode, stage, or
completion state.
