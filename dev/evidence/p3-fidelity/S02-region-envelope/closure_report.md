# S02 — Region envelope evidence closure evidence

Status: `CLOSED`

Implementation commit: `54daaf6` (`feat: add region envelope evidence`)

## Scope

S02 adds an evaluator-authored, normalized region envelope profile and a
provenance-aware geometry comparison. It targets the near-arm failure mode in
which the shoulder→elbow axis is plausible but the occupied arm width and
visible length collapse. The utility emits evidence only; P3 closure decisions
remain a later S03 responsibility.

## Verification

- `PYTHONPATH=skills/img2drawing/src python3 -m pytest -q skills/img2drawing/tests`
  → `18 passed`.
- Subject-only benchmark smoke → `SUBJECT_ONLY_BENCHMARK_PASS`.
- `py_compile` passed for the envelope and public export modules.
- `python3 -m json.tool` passed for `region_envelope.schema.json`.
- `git diff --check` passed.
- 100 comparisons over the 16-station fixture stayed under the 100 ms test
  budget.

## Gates covered

- normalized axis and strictly increasing 2–16 station contour pairs;
- side role, visible fraction, occlusion, and uncertainty preservation;
- local-axis and optional subject-height width evidence;
- distinct observation ids, artifact hashes, and shared S01 lock digest;
- stale drawing-state rejection when the current state digest is supplied;
- same-artifact, lock-mismatch, malformed station, and missing-state rejection;
- evidence-only authority with no artistic PASS/FAIL decision;
- near-arm upper/mid/lower fixture and human-readable SVG board.

## Deliberate boundary

The disposable spike does not promote edge detection or semantic segmentation
into the production contract. Manual paired contour sampling remains the
authoritative input, with existing image evidence helpers available only as
visual aids. No CV, network, or anatomy inference dependency was added.
