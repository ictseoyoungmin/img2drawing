# v1.0.0 stable contract freeze

Freeze ID: **v1.0.0-A8-2026-09-05**

`CONTRACT_FREEZE.json` is the machine-readable stable snapshot. The implementation boundary was
established through B18, the public-root alignment was hardened through A2, and the deployable
instruction graph was hardened through A8. The v1.0.0 promotion changes package/release identity
and documentation; persisted schemas, supported `DrawingSession` members, canonical
`RenderProfile`, ownership boundaries, and explicit R23 checkpoint schemas remain structurally
unchanged.

The stable package identity is `1.0.0` and the public contract identifier is
`DrawingSession/1.0.0-vnext`.

The freeze protects public interfaces and persisted meanings; it does not turn mechanical CI into
an artistic-quality score. The curated Astra demo is positive capability evidence, while formal
D01-D06 cross-subject/cross-agent validation remains incomplete.

There remains one canonical session/history/inspection/render/output core. The similarly named
`img2drawing.core.session.DrawingSession` is a preserved low-level legacy replay record and is not root-exported;
R23 orchestration stays behind `img2drawing.legacy.r23` until a later bounded retirement decision.
