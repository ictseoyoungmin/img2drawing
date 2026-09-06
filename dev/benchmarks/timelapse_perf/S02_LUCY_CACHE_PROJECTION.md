# S02 Lucy-546 cache projection

This file records only aggregate performance structure from the user-supplied Lucy session. It does
not commit subject-specific drawing geometry, authored coordinates, or stroke-control tables.

At 941×1672, ss4, every_n=4:

- 546 authored actions
- 138 sampled frames
- 392 final active strokes
- 35,116 material passes including the current exporter's independent final render
- 541 distinct cacheable stroke-content versions across sampled states
- 34,575 cache hits if every distinct version is materialized once
- 98.4594% projected cache hit rate
- 78.98 MB projected 8-bit mask cache working set
- 315.91 MB equivalent naive RGBA-tile cache working set

The projection validates content-addressing rather than `stroke_id`-only caching: replacement history
can expose multiple raster-distinct versions of one stable stroke identity.

A bounded full cache-only replay attempt still spent too much time rebuilding/downsampling complete
ss4 canvases. That remaining cost is deliberately assigned to S04 incremental composition rather
than hidden inside S02.
