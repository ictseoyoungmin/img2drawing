# Stage Reconstruction Benchmarks

These are runnable packaging fixtures for fresh-worker validation.

`full_body_croquis_subject_only/` contains:
- a directly bundled subject reference;
- benchmark metadata;
- a runnable runtime/import smoke.

Benchmark coordinates are not drawing heuristics. A worker must still observe the
subject and author its own strokes.


## Subject-only is the default real-world path

`full_body_croquis_subject_only/` deliberately contains only:
- `subject.png`
- `benchmark.json`
- `run_smoke.py`

It contains **no same-subject P1/P2/P3/P4/P5 target drawings**.

The per-stage exemplar images used by img2drawing are generic grammar exemplars.
They teach representation vocabulary and detail budget only. They are not target
answers for the current subject and must never donate pose, coordinates, proportions
or perspective.

When a user provides only one subject image, the worker constructs each stage from:
`subject geometry truth + frozen StageContract + generic grammar + verified prior stage`.
