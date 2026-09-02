# vNext dogfood-ready contract freeze

Freeze ID: **B18-dogfood-ready-2026-09-02**

`CONTRACT_FREEZE.json` is the machine-readable snapshot for D01-D06 validation. It pins
the `0.6.0rc1` root exports, supported `DrawingSession` members, schema identifiers,
intent axes, canonical RenderProfile, ownership boundaries, and explicit R23 checkpoint
schemas.

The freeze protects public interfaces and persisted meanings; it does not freeze private
helpers or claim artistic quality. A dogfood defect must reopen the earliest responsible
B-slice, make the smallest contract-aware correction, rerun its technical gates, and then
rerun the affected D-case from sealed input. Any intentional public/schema change must
update the version or schema identifier and this snapshot in the same reviewed change.

There remains one canonical vNext session/history/inspection/render/output core. The
similarly named `img2drawing.core.session.DrawingSession` is a preserved low-level legacy
replay record and is not root-exported; R23 orchestration stays behind
`img2drawing.legacy.r23` until the post-dogfood retirement slice.
