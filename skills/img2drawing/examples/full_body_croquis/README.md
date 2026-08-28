# Canonical Full-body Croquis Hardening Example

This is a focused P1 workflow example, not the full P1→P5 subject-only benchmark.

It demonstrates the required autonomous P1 sequence:

`P1 gesture → subject/target/drawing review → Agent-selected local reviews → REVISE →
explicit pelvis/hip/leg replacement → fresh review → pass-memory continuation → ADVANCE`

## Non-negotiable details demonstrated
- P1 states an observed head outline with a tilt mark, an open jaw-to-clavicle neck
  connection, spine/shoulder/pelvis rhythm, one curved centre-path flow per limb and ground
  contact — and nothing else. No facial features, hair, clothing or muscle.
- Each limb curve passes through its joint markers. The example does not bracket arms or
  legs with paired lines that could be mistaken for sleeve, trouser or limb width.
- Face, spine, shoulder, pelvis and limb flows share the construction hierarchy; the spine
  is not promoted into a dominant black centre pole.
- The pre-draw observation lock records view, near side, arm visibility/occlusion,
  weight side and the subject-derived landmarks used by the stroke plan.
- The frozen StageContract is the representation authority; `references/stages/` carries
  the guidance and the rendered pipeline overview.
- Local crops are selected explicitly by the Agent and both boxes are derived from one
  normalized subject-to-canvas transform, so a crop cannot translate or stretch a mismatch
  into a better-looking fit.
- `p1_target.png` is the user-approved same-task P1 target. Whole-view and local reviews
  therefore compare subject, target and current drawing without treating the target as a
  substitute for subject evidence.
- Pass 2 receives pass-1 remaining concerns and exact inter-pass correction provenance.
- No user approval is requested between routine passes.
- `advance` happens only after a fresh review clears the carried concerns.

## Run

```bash
python run.py --output ./temp/img2drawing-canonical
```

The run writes:
- pass-1 and pass-2 worker packets;
- `pass_memory.json` for each pass;
- local review artifacts;
- review records;
- `canonical_trace.json`.

Pass 1 starts from a new target-registered construction but deliberately leaves the pelvis
line through the provisional hip row, with medial femoral heads and a low image-left knee.
The three-way review catches those mismatches. Pass 2 raises the pelvis line to the pelvic
crest, moves the hip markers laterally, raises the support knee and redraws each leg from
the corrected joint chain.

It intentionally stops with `P2_primary_axes` as the current stage. The example
proves the canonical hardening workflow; it does not claim a finished P1→P5 drawing.
