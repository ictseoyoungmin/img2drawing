# vNext dogfood-ready contract freeze

Freeze ID: **B18+A2-public-root-2026-09-03**

`CONTRACT_FREEZE.json` is the machine-readable snapshot for D01-D06 validation. The
baseline was established at B18 and intentionally realigned in A2 after the instruction-
graph audit showed that the package root exposed too many low-level/history/schema names.

The aligned candidate is `0.6.0rc2`. `DrawingSession/0.6.0-vnext`, supported
`DrawingSession` members, persisted schema identifiers, intent axes, canonical
`RenderProfile`, ownership boundaries, and explicit R23 checkpoint schemas are unchanged.
The intentional contract change is discoverability: `img2drawing.__all__` now names only
the normal high-level framework route plus the small observed-construction facade.
Pre-rc2 direct root imports remain available through deprecated lazy compatibility shims.

The freeze protects public interfaces and persisted meanings; it does not freeze private
helpers or claim artistic quality. A dogfood defect must reopen the earliest responsible
B/A premise, make the smallest contract-aware correction, rerun its technical gates, and
then rerun the affected D-case from sealed input. Any later intentional public/schema
change must update the version or schema identifier and this snapshot in the same reviewed
change.

There remains one canonical vNext session/history/inspection/render/output core. The
similarly named `img2drawing.core.session.DrawingSession` is a preserved low-level legacy
replay record and is not root-exported; R23 orchestration stays behind
`img2drawing.legacy.r23` until the post-dogfood retirement decision.
