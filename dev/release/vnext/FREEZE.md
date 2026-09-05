# v1.0.1 stable contract freeze

Freeze ID: **v1.0.1-A9-2026-09-06**

`CONTRACT_FREEZE.json` is the machine-readable stable snapshot. The implementation boundary was
established through B18, the public-root alignment was hardened through A2, the deployable
instruction graph through A8, and A9 absorbs only generalized authoring mechanics demonstrated by
the Astra capability run.

The v1.0.1 patch adds specialized authoring utilities and one low-taper pencil preset without
changing persisted schemas, canonical `DrawingSession` ownership, the narrow package-root export
surface, `RenderProfile`, or R23 checkpoint compatibility. The new helpers emit existing drawing
history actions rather than introducing a second edit model.

The stable package identity is `1.0.1` and the public contract identifier is
`DrawingSession/1.0.1-vnext`.

The freeze protects public interfaces and persisted meanings; it does not turn mechanical CI into
an artistic-quality score. The curated Astra demo remains positive capability evidence, while
formal D01-D06 cross-subject/cross-agent validation remains incomplete.

There remains one canonical session/history/inspection/render/output core. The similarly named
`img2drawing.core.session.DrawingSession` is a preserved low-level legacy replay record and is not root-exported; R23 orchestration stays behind `img2drawing.legacy.r23` until a later bounded
retirement decision.