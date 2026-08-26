# Canonical Full-body Croquis Hardening Example

This is a focused P1 workflow example, not the full P1→P5 subject-only benchmark.

It demonstrates the required autonomous P1 sequence:

`crown-origin gesture → render/review → Agent-selected local review → REVISE →
explicit replace_stroke → fresh review → pass-memory continuation → ADVANCE`

## Non-negotiable details demonstrated
- The dominant gesture starts at the **crown**, not the neck.
- Inside the head it acts as a curved **facial-centre** line that carries face direction.
- The same dominant intention continues through chin → neck → spine → pelvis →
  support leg → landing point.
- Head-envelope, shoulder/pelvis rhythm and counterbalance marks stay subordinate.
- The known-failed P1 grammar exemplar is not allowed to override the StageContract.
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
