# Runtime discovery boundary

Use this leaf only to confirm what public authoring runtime exists and where the boundary is. It is
not drawing knowledge and it is not permission to inspect implementation internals.

The ordinary worker is **runtime-aware and source-opaque**:

- know that `img2drawing` provides the supported final-authoring runtime;
- discover capabilities from the documented public surface or the small capability manifest;
- do not read the whole `src/` tree, renderer classes, cache internals, persistence internals, or
  private helpers as a prerequisite for drawing;
- do not silently replace the runtime with Pillow/ImageDraw, OpenCV raster edits, SVG/canvas, or a
  bespoke rasterizer when a public capability appears missing;
- report a runtime capability gap and keep the visual/artistic decision separate from framework
  implementation work.

A source-opaque capability check is available without renderer inspection:

```python
from img2drawing.runtime import runtime_capabilities

caps = runtime_capabilities()
assert caps.orchestration == "DrawingSession"
assert caps.final_authoring_runtime
assert not caps.implementation_read_required
assert caps.capability_gap_policy == "report-not-bypass"
```

The manifest intentionally exposes capability names and boundaries only. It must not grow into a
map of private modules, renderer implementation classes, cache objects, internal history layouts,
or other source-navigation hints.

## Drawing-worker rule

Before the first programmatic mark:

```text
read SKILL.md
→ know img2drawing runtime exists
→ read api/public-surface.md when operation details are needed
→ optionally inspect runtime_capabilities()
→ author through DrawingSession/public helpers
```

Never route ordinary drawing as:

```text
read SKILL.md
→ ignore runtime
→ build final image directly with Pillow/OpenCV
```

and never route it as:

```text
read SKILL.md
→ crawl src/
→ learn private renderer implementation
→ depend on implementation details
```

Pillow, NumPy, OpenCV, crops, overlays, and similar tools remain valid for bounded observation or
evidence work when the relevant instruction leaves allow them. They are not alternative final
stroke-authoring runtimes.
