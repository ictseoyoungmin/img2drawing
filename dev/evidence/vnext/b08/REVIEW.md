# B08 intent scaffolding review

Reviewed: **2026-08-31**

The B08 fixture uses the B05 subject and construction with one shared
`DrawingSession`. It starts with `observed / croquis / pose / pencil_loose`, authors and
inspects the same construction, then records `hybrid / figure_drawing / subject /
graphite_academic` as a second intent event. No stroke is edited during the change.

Evidence in [`b08_intent_trace.json`](b08_intent_trace.json) records:

- two complete intent snapshots and the previous-digest provenance chain;
- one focused inspection from the existing B07 inspection boundary;
- both minimal mode fixtures and both minimal style fixtures;
- identical before/after drawing-state hash and action-history cursor (`38`);
- checkpoint resume restoring the changed intent and both intent events.

The fixture exercises data resolution only. It does not introduce a mode-specific
session, renderer, stage/cursor transition, raster post-filter, automatic score, or
custom-prose parser.
