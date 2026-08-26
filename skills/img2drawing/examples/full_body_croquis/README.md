# Canonical Full-body Croquis Hardening Example

This is a focused P1 workflow example, not the full P1→P5 subject-only benchmark.

It demonstrates the required autonomous P1 sequence:

`P1 gesture → render/review → Agent-selected local review → REVISE →
explicit replace_stroke → fresh review → pass-memory continuation → ADVANCE`

## Non-negotiable details demonstrated
- P1 states one dominant **line of action** plus a simple head ovoid with a tilt mark,
  shoulder and pelvis tilt lines, arm and leg direction paths, and ground contact — and
  nothing else. No facial features, hair, clothing or muscle.
- Everything except the line of action stays subordinate to it.
- The frozen StageContract is the representation authority; `references/stages/` carries
  the guidance and the rendered pipeline overview.
- Local crops are selected explicitly by the Agent.
- Pass 2 receives pass-1 remaining concerns and exact inter-pass correction provenance.
- No user approval is requested between routine passes.
- `advance` happens only after a fresh review clears the carried concerns.

## Run

```bash
python run.py --output /tmp/img2drawing-canonical
```

The run writes:
- pass-1 and pass-2 worker packets;
- `pass_memory.json` for each pass;
- local review artifacts;
- review records;
- `canonical_trace.json`.

It intentionally stops with `P2_primary_axes` as the current stage. The example
proves the canonical hardening workflow; it does not claim a finished P1→P5 drawing.
