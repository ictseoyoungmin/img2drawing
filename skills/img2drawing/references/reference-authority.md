# Reference authority

Reference authority states what the Agent may compare the current drawing against. It is
immutable for one `DrawingSession`, portable in the checkpoint, and separate from mode,
style, renderer, inspection budget, and completion. It never chooses a residual or emits
an artistic verdict.

## Observed

A readable subject and its SHA-256 are evidence authority. Existing observed creation is
unchanged:

```python
from img2drawing import DrawingIntent, DrawingSession

session = DrawingSession.create(
    subject="subject.png",
    output_dir="out",
    intent=DrawingIntent(reference_mode="observed"),
)
```

The session derives `ReferenceAuthority.observed(subject_sha256)`. A caller may provide an
explicit observed authority, but its hash must match the readable subject. An older
observed checkpoint with no authority record resumes by deriving the same authority;
drawing/action hashes do not change.

## Imaginative

No subject exists. An explicit canvas plus concrete declared goals are comparison truth:

```python
from img2drawing import DrawingIntent, DrawingSession, ReferenceAuthority

authority = ReferenceAuthority.imaginative(
    (
        "a broad ascending arc anchors the composition",
        "a small counter-shape activates the lower-right corner",
    )
)
session = DrawingSession.create(
    canvas=(1024, 1024),
    output_dir="out",
    intent=DrawingIntent(reference_mode="imaginative", drawing_mode="free_draw"),
    reference_authority=authority,
)
```

A generic label such as “imaginative” is not enough: `declared_goals` must name usable
composition, shape, focal, rhythm, or subject goals. The Agent records observations by
comparing those goals with the current raw drawing.

`session.inspect()` produces only:

```text
inspection_sheet.png  drawing-only presentation
raw_drawing.png        authoritative current render
inspection.json        state/intent/authority provenance
```

It does not create a blank subject, registered drawing, contrast overlay, or measurements
file. `session.require_reference()` and subject registration, overlay controls,
subject-space ROI/guide/grid/measurement inputs raise `ReferenceUnavailableError`.

The ordinary `observe → draw → inspect → record_residual → correct → inspect → finish`
loop, checkpoint/resume, final PNG, and replay/GIF use the same implementations as
observed work.

## Hybrid

Hybrid authority uses a readable subject but records two different dispositions:

```python
from img2drawing import (
    DrawingIntent, DrawingSession, ReferenceAuthority, ReferenceConstraint,
)

authority = ReferenceAuthority.hybrid(
    subject_sha256,
    (
        ReferenceConstraint(
            "pose", "preserve the three-quarter torso turn", "preserved"
        ),
        ReferenceConstraint(
            "coat", "change the coat silhouette", "transformed",
            transformation="extend it into a triangular cape",
            rationale="requested fantasy transformation",
        ),
    ),
)
session = DrawingSession.create(
    subject="subject.png",
    output_dir="out",
    intent=DrawingIntent(reference_mode="hybrid"),
    reference_authority=authority,
)
```

A hybrid authority must contain at least one `preserved` and one `transformed`
constraint. A transformed constraint requires both the intended transformation and its
rationale. This prevents a transformed feature from being judged as an observed mismatch
or a preserved feature from being silently discarded.

## Persistence and intent changes

The checkpoint stores the complete authority plus its digest. Every new inspection binds
that digest. Resume rejects mismatched authority/subject/intent or tampered authority
payloads. An older hybrid checkpoint that recorded only the intent may resume only when
the caller supplies an explicit matching `reference_authority`; the runtime does not infer
preserved or transformed constraints.

`session.set_intent()` may change drawing mode, finish intent, or style within the same
reference mode. It rejects a reference-mode change because existing observations,
inspections, residuals, and corrections already depend on the session's comparison truth.
